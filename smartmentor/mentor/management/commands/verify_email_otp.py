import secrets
import time

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Send and verify an email OTP"

    def handle(self, *args, **options):
        email = input("Enter your email address: ").strip()

        if "@" not in email or "." not in email.split("@")[-1]:
            self.stdout.write(self.style.ERROR("Invalid email address."))
            return

        otp = f"{secrets.randbelow(1000000):06d}"

        try:
            send_mail(
                "Smart Mentor Email Verification",
                f"Your OTP is {otp}. It expires in 5 minutes.",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as error:
            self.stdout.write(self.style.ERROR(
                f"Email sending failed: {error}"
            ))
            return

        self.stdout.write("OTP email requested. Check your terminal or inbox.")
        expires_at = time.monotonic() + 300

        for attempt in range(3):
            entered_otp = input("Enter the 6-digit OTP: ").strip()

            if time.monotonic() > expires_at:
                break

            if secrets.compare_digest(entered_otp, otp):
                self.stdout.write(self.style.SUCCESS(
                    "Email verified successfully!"
                ))
                return

            self.stdout.write(self.style.WARNING("Incorrect OTP."))

        self.stdout.write(self.style.ERROR(
            "Verification failed or OTP expired."
        ))