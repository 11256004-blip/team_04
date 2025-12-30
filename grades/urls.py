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
]

