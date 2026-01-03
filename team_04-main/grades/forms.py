from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Course, Enrollment, UserProfile


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'teacher']


class EnrollForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        # student will be set from request.user in the view
        fields = ['course', 'midterm_score', 'final_score']


class RegistrationForm(UserCreationForm):
    """新增使用者註冊表單"""
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class UserProfileForm(forms.ModelForm):
    """修改個人資訊表單"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='名字',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='姓氏',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        label='電子郵件',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio']
        labels = {
            'avatar': '個人頭像',
            'bio': '個人簡介'
        }
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email


class TeacherCourseForm(forms.ModelForm):
    """教師新增課程表單"""
    class Meta:
        model = Course
        fields = ['name', 'code', 'description', 'credits', 'capacity']
        labels = {
            'name': '課程名稱',
            'code': '課程代碼',
            'description': '課程描述',
            'credits': '學分',
            'capacity': '最大人數'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例：程式設計 I'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例：CS101'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '課程概述和內容'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 6}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 200}),
        }


class EnrollmentScoreForm(forms.ModelForm):
    """教師編輯學生成績表單"""
    class Meta:
        model = Enrollment
        fields = ['midterm_score', 'final_score']
        labels = {
            'midterm_score': '期中成績',
            'final_score': '期末成績'
        }
        widgets = {
            'midterm_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': 0.5}),
            'final_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': 0.5}),
        }
