from django import forms
from .models import Course, Enrollment


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'teacher']


class EnrollForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        # student will be set from request.user in the view
        fields = ['course', 'midterm_score', 'final_score']
