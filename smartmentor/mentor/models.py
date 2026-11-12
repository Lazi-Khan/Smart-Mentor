
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


# ==========================================
# EXCEL FILE MODEL
# ==========================================

class ExcelFile(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='excel_files/')

    class Meta:
        verbose_name = "Student Excel File"
        verbose_name_plural = "Student Excel Files"

    def __str__(self):
        return self.title


# ==========================================
# NOTIFICATION MODEL
# ==========================================

class Notification(models.Model):
    recipient_email = models.EmailField(default='')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Student Notification"
        verbose_name_plural = "Student Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return self.message


# ==========================================
# STUDENT PROFILE MODEL
# ==========================================

class StudentProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    roll_number = models.CharField(max_length=30, unique=True)
    course = models.CharField(max_length=100)
    class_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True)
    academic_year = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.roll_number}"


# ==========================================
# TEACHER PROFILE MODEL
# ==========================================

class TeacherProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_profile"
    )

    employee_id = models.CharField(max_length=30, unique=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)

    class Meta:
        verbose_name = "Teacher Profile"
        verbose_name_plural = "Teacher Profiles"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"


# ==========================================
# SUBJECT MODEL
# ==========================================

class Subject(models.Model):

    subject_code = models.CharField(max_length=30, unique=True)
    subject_name = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    semester = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ['subject_name']

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"


# ==========================================
# TEACHER ASSIGNMENT MODEL
# ==========================================

class TeacherAssignment(models.Model):

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    class_name = models.CharField(max_length=100)
    academic_year = models.CharField(max_length=20)

    assigned_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Teacher Assignment"
        verbose_name_plural = "Teacher Assignments"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'teacher',
                    'subject',
                    'class_name',
                    'academic_year'
                ],
                name='unique_teacher_assignment'
            )
        ]

    def __str__(self):
        return f"{self.teacher} - {self.subject} - {self.class_name}"


# ==========================================
# STUDENT MARKS MODEL
# ==========================================

class StudentMark(models.Model):

    EXAM_CHOICES = [
        ('Internal', 'Internal'),
        ('External', 'External'),
        ('Practical', 'Practical'),
    ]

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="marks"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="student_marks"
    )

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entered_marks"
    )

    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_CHOICES
    )

    marks_obtained = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )

    max_marks = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(1)]
    )

    academic_year = models.CharField(max_length=20)

    exam_date = models.DateField(null=True, blank=True)

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Student Mark"
        verbose_name_plural = "Student Marks"
        ordering = ['student', 'subject']

        constraints = [
            models.UniqueConstraint(
                fields=[
                    'student',
                    'subject',
                    'exam_type',
                    'academic_year'
                ],
                name='unique_student_subject_exam_year'
            )
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.marks_obtained is not None and self.max_marks is not None:
            if self.max_marks < 1:
                raise ValidationError({
                    'max_marks': 'Maximum marks must be greater than zero.'
                })

            if self.marks_obtained > self.max_marks:
                raise ValidationError({
                    'marks_obtained': 'Obtained marks cannot exceed maximum marks.'
                })

    @property
    def percentage(self):
        if self.max_marks:
            return round(
                (self.marks_obtained / self.max_marks) * 100,
                2
            )
        return 0

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.exam_type}"
