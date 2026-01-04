from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """擴展 Django User 模型，添加頭像和個人資訊"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, default='avatars/default-avatar.png')
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class Teacher(models.Model):
    """教師模型，與 User 一對一關聯"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    department = models.CharField(max_length=100, blank=True, help_text='系別或部門')
    office = models.CharField(max_length=100, blank=True, help_text='辦公室位置')
    phone = models.CharField(max_length=20, blank=True, help_text='聯絡電話')
    office_hours = models.TextField(blank=True, help_text='辦公時間')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '教師'
        verbose_name_plural = '教師'

    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return f"{self.user.last_name} {self.user.first_name}"
        return f"Teacher: {self.user.username}"


class Course(models.Model):
    name = models.CharField(max_length=200, help_text='課程名稱')
    code = models.CharField(max_length=50, unique=True, help_text='課程代碼（唯一）')
    teacher = models.CharField(max_length=100, blank=True, help_text='授課教師（文字）')
    teacher_fk = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses', help_text='授課教師（指定）')
    description = models.TextField(blank=True, help_text='課程描述')
    credits = models.IntegerField(default=3, help_text='學分數')
    capacity = models.IntegerField(default=30, help_text='最大人數')

    class Meta:
        verbose_name = '課程'
        verbose_name_plural = '課程'
        ordering = ['code']

    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_teacher_name(self):
        """取得教師名稱（優先使用 FK）"""
        if self.teacher_fk:
            if self.teacher_fk.user.first_name and self.teacher_fk.user.last_name:
                return f"{self.teacher_fk.user.last_name} {self.teacher_fk.user.first_name}"
            return self.teacher_fk.user.username
        return self.teacher or "未分配"


class Enrollment(models.Model):
    # use Django's User model for the student
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    midterm_score = models.FloatField(null=True, blank=True)
    final_score = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course')
        verbose_name = '選課記錄'
        verbose_name_plural = '選課記錄'

    def __str__(self):
        return f"{self.student} - {self.course}"

    def average(self):
        scores = [s for s in (self.midterm_score, self.final_score) if s is not None]
        return sum(scores) / len(scores) if scores else None


class CourseComment(models.Model):
    """課程留言模型"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_comments')
    content = models.TextField(help_text='留言內容')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '課程留言'
        verbose_name_plural = '課程留言'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username} - {self.course.name}: {self.content[:30]}"
