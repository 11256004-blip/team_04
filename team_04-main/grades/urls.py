from django.urls import path
from . import views

app_name = 'grades'

urlpatterns = [
    path('', views.home, name='home'),
    path('main/', views.main, name='main'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('add_course/', views.add_course, name='add_course'),
    path('enroll/', views.enroll, name='enroll'),
    path('unenroll/<int:enrollment_id>/', views.unenroll, name='unenroll'),
    
    # Student profile routes
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('add_comment/<int:course_id>/', views.add_comment, name='add_comment'),
    path('edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('course_comments/<int:course_id>/', views.course_comments, name='course_comments'),
    
    # Authentication routes
    path('logout_confirm/', views.logout_confirm, name='logout_confirm'),
    path('logout/', views.custom_logout, name='custom_logout'),
    
    # Admin routes
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/user/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/courses/', views.admin_courses, name='admin_courses'),
    path('admin/course/<int:course_id>/', views.admin_course_detail, name='admin_course_detail'),
    
    # Teacher routes
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/course/<int:course_id>/', views.teacher_course_detail, name='teacher_course_detail'),
    path('teacher/update_grade/<int:enrollment_id>/', views.teacher_update_grade, name='teacher_update_grade'),
    path('teacher/add_course/', views.teacher_add_course, name='teacher_add_course'),
    path('teacher/student_list/', views.teacher_student_list, name='teacher_student_list'),
    path('teacher/grade_entry/<int:course_id>/', views.teacher_grade_entry, name='teacher_grade_entry'),
]

