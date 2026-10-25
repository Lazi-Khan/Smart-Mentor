
from django.db import models


class ExcelFile(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='excel_files/')

    class Meta:
        verbose_name = "Student Excel File"
        verbose_name_plural = "Student Excel Files"

    def __str__(self):
        return self.title


class Notification(models.Model):
    recipient_email = models.EmailField(default='')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Student Notification"
        verbose_name_plural = "Student Notifications"

    def __str__(self):
        return self.message
