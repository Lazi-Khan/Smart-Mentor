import secrets
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.shortcuts import render, redirect

from .models import ExcelFile, Notification, StudentProfile, StudentMark


# NEW STUDENT REGISTRATION
def student_register(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        User = get_user_model()

        if not name or not email or not password:
            messages.error(request, "All fields are required.")

        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")

        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already registered.")

        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )

            messages.success(
                request,
                "Account created successfully! Please login."
            )

            return redirect("student_login")

    return render(request, "mentor/student_register.html")


# STUDENT LOGIN
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
            messages.error(request, "Could not send OTP.")
            return render(request, "mentor/student_login.html")

        return redirect("verify_login_otp")

    return render(request, "mentor/student_login.html")


# VERIFY OTP
def verify_login_otp(request):

    if request.method == "POST":

        entered_otp = request.POST.get("otp", "").strip()
        saved_otp = request.session.get("login_otp")
        email = request.session.get("login_email")
        expiry = request.session.get("otp_expiry", 0)

        if not saved_otp or not email:
            messages.error(request, "Request a new OTP.")
            return redirect("student_login")

        if time.time() > expiry:
            messages.error(request, "OTP expired.")
            return redirect("student_login")

        if secrets.compare_digest(entered_otp, saved_otp):

            User = get_user_model()
            user = User.objects.filter(email__iexact=email).first()

            if user:
                login(request, user)

                request.session.pop("login_otp", None)
                request.session.pop("login_email", None)
                request.session.pop("otp_expiry", None)

                return redirect("dashboard")

        messages.error(request, "Incorrect OTP.")

    return render(request, "mentor/verify_login_otp.html")


@login_required(login_url="student_login")
def dashboard(request):

    # Get Excel files
    excel_files = ExcelFile.objects.all()

    # Get logged-in student's profile
    student = StudentProfile.objects.filter(
        user=request.user
    ).first()

    # Get marks belonging to this student
    marks = []

    if student:
        marks = StudentMark.objects.filter(
            student=student
        ).select_related(
            "subject", "teacher"
        ).order_by("subject__subject_name")

    # Get notifications
    notifications = Notification.objects.filter(
        recipient_email__iexact=request.user.email
    ).order_by("-created_at")

    context = {
        "excel_files": excel_files,
        "notifications": notifications,
        "student": student,
        "marks": marks,
    }

    return render(request, "mentor/dashboard.html", context)
# STUDENT LOGOUT
def student_logout(request):
    logout(request)
    return redirect("student_login")