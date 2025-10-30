from django.db import models
from django.conf import settings


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    teacher = models.CharField(max_length=100)

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
