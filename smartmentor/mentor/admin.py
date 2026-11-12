from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import (
    ExcelFile,
    Notification,
    StudentProfile,
    TeacherProfile,
    Subject,
    TeacherAssignment,
    StudentMark,
)


User = get_user_model()


# =================================================
# SMART MENTOR ADMIN HEADER
# =================================================

admin.site.site_header = "🎓 SMART MENTOR"
admin.site.site_title = "Smart Mentor Portal"
admin.site.index_title = "Student Academic Performance Dashboard"
admin.site.site_url = "/student-login/"


# =================================================
# EXCEL FILE MANAGEMENT
# =================================================

@admin.register(ExcelFile)
class ExcelFileAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "file",
    )

    search_fields = ("title",)

    list_per_page = 15

    ordering = ("-id",)


# =================================================
# NOTIFICATION ACTIONS
# =================================================

@admin.action(description="Mark selected notifications as read")
def mark_as_read(modeladmin, request, queryset):
    queryset.update(is_read=True)


@admin.action(description="Mark selected notifications as unread")
def mark_as_unread(modeladmin, request, queryset):
    queryset.update(is_read=False)


# =================================================
# NOTIFICATION ADMIN
# =================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "recipient_email",
        "message",
        "created_at",
        "is_read",
    )

    search_fields = (
        "recipient_email",
        "message",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    ordering = ("-created_at",)

    actions = (
        mark_as_read,
        mark_as_unread,
    )

    list_per_page = 20


# =================================================
# STUDENT FORM
# =================================================

class StudentProfileForm(forms.ModelForm):

    first_name = forms.CharField(
        max_length=150,
        label="First Name"
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Last Name"
    )

    email = forms.EmailField(
        label="Email Address"
    )

    class Meta:
        model = StudentProfile
        exclude = ("user",)

    def clean_email(self):

        email = self.cleaned_data["email"].strip().lower()

        existing_user = User.objects.filter(
            email__iexact=email
        )

        if self.instance.pk:
            existing_user = existing_user.exclude(
                pk=self.instance.user_id
            )

        if existing_user.exists():
            raise ValidationError(
                "This email address is already registered."
            )

        return email


# =================================================
# STUDENT ACTIONS
# =================================================

@admin.action(description="Activate selected students")
def activate_students(modeladmin, request, queryset):

    for profile in queryset:
        profile.user.is_active = True
        profile.user.save()


@admin.action(description="Deactivate selected students")
def deactivate_students(modeladmin, request, queryset):

    for profile in queryset:
        profile.user.is_active = False
        profile.user.save()


# =================================================
# STUDENT PROFILE ADMIN
# =================================================

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):

    form = StudentProfileForm

    list_display = (
        "student_name",
        "student_email",
        "roll_number",
        "course",
        "class_name",
        "academic_year",
        "account_status",
    )

    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "roll_number",
        "course",
    )

    list_filter = (
        "course",
        "class_name",
        "academic_year",
        "user__is_active",
    )

    ordering = ("roll_number",)

    list_per_page = 20

    list_select_related = ("user",)

    readonly_fields = (
        "date_joined",
        "last_login",
    )

    actions = (
        activate_students,
        deactivate_students,
    )

    fieldsets = (

        ("Student Information", {
            "fields": (
                "first_name",
                "last_name",
                "email",
                "roll_number",
            )
        }),

        ("Academic Information", {
            "fields": (
                "course",
                "class_name",
                "academic_year",
            )
        }),

        ("Account Information", {
            "fields": (
                "date_joined",
                "last_login",
            )
        }),

    )

    def get_form(self, request, obj=None, **kwargs):

        form = super().get_form(
            request,
            obj,
            **kwargs
        )

        if obj and obj.user:

            form.base_fields["first_name"].initial = (
                obj.user.first_name
            )

            form.base_fields["last_name"].initial = (
                obj.user.last_name
            )

            form.base_fields["email"].initial = (
                obj.user.email
            )

        return form

    @admin.display(description="Student Name")
    def student_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    @admin.display(description="Email")
    def student_email(self, obj):
        return obj.user.email

    @admin.display(description="Status")
    def account_status(self, obj):

        if obj.user.is_active:
            return "✅ Active"

        return "❌ Inactive"

    def date_joined(self, obj):

        if obj.user:
            return obj.user.date_joined

        return "-"

    date_joined.short_description = "Date Joined"

    def last_login(self, obj):

        if obj.user:
            return obj.user.last_login

        return "-"

    last_login.short_description = "Last Login"

    @transaction.atomic
    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        email = form.cleaned_data["email"]
        first_name = form.cleaned_data["first_name"]
        last_name = form.cleaned_data["last_name"]

        if not change:

            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=None
            )

            obj.user = user

        else:

            user = obj.user

            user.username = email
            user.email = email
            user.first_name = first_name
            user.last_name = last_name

            user.save()

        super().save_model(
            request,
            obj,
            form,
            change
        )
       
# =================================================
# TEACHER MANAGEMENT
# =================================================

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):

    list_display = (
        "employee_id",
        "teacher_name",
        "teacher_email",
        "department",
        "designation",
        "phone",
    )

    search_fields = (
        "employee_id",
        "user__first_name",
        "user__last_name",
        "user__email",
    )

    list_filter = ("department", "designation")

    list_select_related = ("user",)

    @admin.display(description="Teacher Name")
    def teacher_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description="Email")
    def teacher_email(self, obj):
        return obj.user.email


# =================================================
# SUBJECT MANAGEMENT
# =================================================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        "subject_code",
        "subject_name",
        "course",
        "semester",
    )

    search_fields = (
        "subject_code",
        "subject_name",
        "course",
    )

    list_filter = ("course", "semester")


# =================================================
# TEACHER ASSIGNMENT
# =================================================

@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "teacher",
        "subject",
        "class_name",
        "academic_year",
        "assigned_date",
    )

    search_fields = (
        "teacher__user__first_name",
        "teacher__user__last_name",
        "subject__subject_name",
        "class_name",
    )

    list_filter = (
        "class_name",
        "academic_year",
        "subject",
    )

    list_select_related = ("teacher__user", "subject")


# =================================================
# STUDENT MARKS MANAGEMENT
# =================================================

@admin.register(StudentMark)
class StudentMarkAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "subject",
        "teacher",
        "exam_type",
        "marks_obtained",
        "max_marks",
        "percentage_display",
        "academic_year",
    )

    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__roll_number",
        "subject__subject_name",
    )

    list_filter = (
        "exam_type",
        "academic_year",
        "subject",
    )

    list_select_related = (
        "student__user",
        "subject",
        "teacher__user",
    )

    @admin.display(description="Percentage")
    def percentage_display(self, obj):
        return f"{obj.percentage}%"

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)
