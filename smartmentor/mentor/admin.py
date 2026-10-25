from django.contrib import admin
from .models import ExcelFile, Notification

admin.site.register(ExcelFile)
admin.site.register(Notification)
admin.site.site_header = "🎓 SMART MENTOR"
admin.site.site_title = "Smart Mentor Portal"
admin.site.index_title = "Student Academic Performance Dashboard"
