
from django.contrib import admin
from django.urls import path
from mentor import views

admin.site.site_header = "SMART MENTOR STUDENT ACADEMIC PERFORMANCE"
admin.site.site_title = "SMART MENTOR"
admin.site.site_index_title = "Welcome to SMART MENTOR"

urlpatterns = [
    path('admin/', admin.site.urls),

    path('student-login/', views.student_login, name='student_login'),
    path('verify-otp/', views.verify_login_otp, name='verify_login_otp'),
       path('dashboard/', views.dashboard, name='dashboard')
]
