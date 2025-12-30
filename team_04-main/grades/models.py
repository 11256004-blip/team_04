from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone


# User role choices
ROLE_CHOICES = [
    ('student', 'Student'),
    ('teacher', 'Teacher'),
    ('admin', 'Admin'),
]


class UserProfile(models.Model):
    """Extended user profile for role-based access control"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    department = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default_avatar.png')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        verbose_name_plural = "User Profiles"


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='teaching_courses', limit_choices_to={'profile__role': 'teacher'})
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Enrollment(models.Model):
    # use Django's User model for the student
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    midterm_score = models.FloatField(null=True, blank=True)
    final_score = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} - {self.course}"

    def average(self):
        scores = [s for s in (self.midterm_score, self.final_score) if s is not None]
        return sum(scores) / len(scores) if scores else None


class Comment(models.Model):
    """Course comments by students"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.name}"
