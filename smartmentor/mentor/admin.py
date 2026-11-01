

from django.contrib import admin
from .models import ExcelFile, Notification

admin.site.site_header = "🎓 SMART MENTOR STUDENT ACADEMIC PERFORMANCE"
admin.site.site_title = "Smart Mentor Portal"
admin.site.index_title = "Student Academic Performance Dashboard"


@admin.register(ExcelFile)
class ExcelFileAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "file")
    search_fields = ("title",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recipient_email",
        "message",
        "created_at",
        "is_read"
    )

    search_fields = ("recipient_email", "message")
    list_filter = ("is_read", "created_at")
