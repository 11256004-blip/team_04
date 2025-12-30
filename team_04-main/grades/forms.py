from django import forms
from django.contrib.auth.models import User
from .models import Course, Enrollment, UserProfile, ROLE_CHOICES, Comment


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'teacher', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EnrollForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        # student will be set from request.user in the view
        fields = ['course', 'midterm_score', 'final_score']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'midterm_score': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1}),
            'final_score': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'department']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class UserProfileEditForm(forms.ModelForm):
    """Form for editing user profile with avatar"""
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '名字'}),
        label='名字'
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '姓氏'}),
        label='姓氏'
    )
    
    class Meta:
        model = UserProfile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'avatar': '個人頭像',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.last_name = self.cleaned_data.get('last_name', '')
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile


class CommentForm(forms.ModelForm):
    """Form for adding/editing comments"""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '輸入你對課程的留言...',
            }),
        }
        labels = {
            'content': '留言內容',
        }

