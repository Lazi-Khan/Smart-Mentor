import secrets
import time

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = "Send and verify an email OTP"

    def handle(self, *args, **options):
        email = input("Enter your email address: ").strip()

        if "@" not in email or "." not in email.split("@")[-1]:
            self.stdout.write(self.style.ERROR("Invalid email address."))
            return

        otp = f"{secrets.randbelow(1_000_000):06d}"

        try:
            send_mail(
                subject="Smart Mentor Email Verification",
                message=f"Your OTP is {otp}. It expires in 5 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as error:
            self.stdout.write(self.style.ERROR(
                f"Email sending failed: {error}"
            ))
            return

        self.stdout.write("OTP email requested. Check your email.")
        expires_at = time.monotonic() + 300

        for attempt in range(3):
            if time.monotonic() >= expires_at:
                break

            entered_otp = input("Enter the 6-digit OTP: ").strip()

            if time.monotonic() >= expires_at:
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