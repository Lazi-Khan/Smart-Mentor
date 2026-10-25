
import secrets
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.core.mail import send_mail
from django.shortcuts import render, redirect


def student_login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()

        User = get_user_model()
        user = User.objects.filter(email__iexact=email).first()

        if not user:
            messages.error(request, "Student account not found.")
            return render(request, "mentor/student_login.html")

        otp = f"{secrets.randbelow(1000000):06d}"

        request.session["login_otp"] = otp
        request.session["login_email"] = email
        request.session["otp_expiry"] = time.time() + 300

        try:
            send_mail(
                "Smart Mentor Login OTP",
                f"Your login OTP is {otp}. It expires in 5 minutes.",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception:
            messages.error(request, "Could not send OTP. Please try again.")
            return render(request, "mentor/student_login.html")

        return redirect("verify_login_otp")

    return render(request, "mentor/student_login.html")


def verify_login_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()
        saved_otp = request.session.get("login_otp")
        email = request.session.get("login_email")
        expiry = request.session.get("otp_expiry", 0)

        if not saved_otp or not email:
            messages.error(request, "Please request a new OTP.")
            return redirect("student_login")

        if time.time() > expiry:
            request.session.pop("login_otp", None)
            request.session.pop("login_email", None)
            request.session.pop("otp_expiry", None)
            messages.error(request, "OTP expired. Please log in again.")
            return redirect("student_login")

        if secrets.compare_digest(entered_otp, saved_otp):
            User = get_user_model()
            user = User.objects.filter(email__iexact=email).first()

            if user:
                login(request, user)
                request.session.pop("login_otp", None)
                request.session.pop("login_email", None)
                request.session.pop("otp_expiry", None)
                messages.success(request, "Login successful!")
                return redirect("dashboard")

        messages.error(request, "Incorrect OTP.")

    return render(request, "mentor/verify_login_otp.html")


def dashboard(request):
    return render(request, "mentor/dashboard.html")
