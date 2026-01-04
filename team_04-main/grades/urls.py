from django.urls import path
from . import views

app_name = 'grades'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('main/', views.main, name='main'),
    path('profile/', views.profile, name='profile'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('add_course/', views.add_course, name='add_course'),
    path('enroll/', views.enroll, name='enroll'),
    path('unenroll/<int:enrollment_id>/', views.unenroll, name='unenroll'),
    
    # 教師相關路由
    path('teacher/courses/', views.teacher_courses, name='teacher_courses'),
    path('teacher/add-course/', views.add_course_teacher, name='add_course_teacher'),
    path('teacher/course/<int:course_id>/students/', views.course_students, name='course_students'),
    path('teacher/enrollment/<int:enrollment_id>/update-score/', views.update_student_score, name='update_student_score'),
    
    # 課程留言相關路由
    path('course/<int:course_id>/comments/', views.course_comments, name='course_comments'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]

