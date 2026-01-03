from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, logout as auth_logout
from django.contrib import messages
from .models import Course, Enrollment, UserProfile, Teacher
from .forms import CourseForm, EnrollForm, RegistrationForm, UserProfileForm, TeacherCourseForm, EnrollmentScoreForm


def home(request):
    # homepage with a link to the main page
    return render(request, 'grades/home.html')


def register(request):
    """使用者註冊視圖"""
    if request.user.is_authenticated:
        return redirect('grades:main')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 為新使用者建立 UserProfile
            UserProfile.objects.get_or_create(user=user)
            messages.success(request, '帳號建立成功！請登入。')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistrationForm()
    
    return render(request, 'grades/register.html', {'form': form})


@login_required
def logout_view(request):
    """登出視圖"""
    auth_logout(request)
    messages.success(request, '已成功登出。')
    return redirect('grades:home')


def main(request):
    # show the logged-in user's enrollments if authenticated,
    # otherwise fall back to the first user in the database (for single-student demo)
    User = get_user_model()
    if request.user.is_authenticated:
        student = request.user
    else:
        student = User.objects.first()

    if not student:
        # no users exist yet
        return render(request, 'grades/main.html', {
            'student': None,
            'enrollments': [],
            'overall_avg': None,
            'message': '目前尚無使用者，請執行 populate_initial.py 建立測試使用者與課程，或使用 admin 建立使用者。'
        })

    enrollments = student.enrollments.select_related('course').all()
    # compute average across courses (only consider enrollments with average)
    avgs = [e.average() for e in enrollments if e.average() is not None]
    overall_avg = sum(avgs) / len(avgs) if avgs else None
    
    # 獲取使用者的 Profile
    profile = UserProfile.objects.filter(user=student).first()

    return render(request, 'grades/main.html', {
        'student': student,
        'enrollments': enrollments,
        'overall_avg': overall_avg,
        'profile': profile,
    })


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollments = course.enrollments.select_related('student').all()
    return render(request, 'grades/course_detail.html', {
        'course': course,
        'enrollments': enrollments,
    })


def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('grades:main')
    else:
        form = CourseForm()
    return render(request, 'grades/add_course.html', {'form': form})


@login_required
def enroll(request):
    # enroll the logged-in user into a course
    student = request.user
    
    # 獲取還沒選過的課程
    enrolled_courses = student.enrollments.values_list('course_id', flat=True)
    available_courses = Course.objects.exclude(id__in=enrolled_courses)

    if request.method == 'POST':
        form = EnrollForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student = student
            
            # 檢查是否已經選過這門課
            if Enrollment.objects.filter(student=student, course=enrollment.course).exists():
                messages.error(request, '您已經選過這門課程了。')
                return redirect('grades:enroll')
            
            enrollment.save()
            messages.success(request, '成功加選課程！')
            return redirect('grades:main')
    else:
        form = EnrollForm()

    return render(request, 'grades/enroll.html', {
        'form': form,
        'available_courses': available_courses,
    })


@login_required
def unenroll(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    # only allow the owner to unenroll
    if request.user.is_authenticated and enrollment.student == request.user:
        course_name = enrollment.course.name
        enrollment.delete()
        messages.success(request, f'已成功退選課程：{course_name}')
    return redirect('grades:main')


@login_required
def profile(request):
    """修改個人資訊視圖"""
    # 獲取或建立 UserProfile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # 更新 User 欄位
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            
            # 保存 Profile
            form.save()
            messages.success(request, '個人資訊已成功更新。')
            return redirect('grades:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'grades/profile.html', {
        'form': form,
        'profile': profile,
    })


# ========================
# 教師相關視圖函數
# ========================

def is_teacher(user):
    """檢查使用者是否為教師"""
    return hasattr(user, 'teacher_profile')


@login_required
def teacher_courses(request):
    """顯示教師的課程列表"""
    # 檢查使用者是否為教師
    if not is_teacher(request.user):
        messages.error(request, '您沒有教師權限。')
        return redirect('grades:main')
    
    teacher = request.user.teacher_profile
    courses = teacher.courses.all()
    
    return render(request, 'grades/teacher_courses.html', {
        'teacher': teacher,
        'courses': courses,
    })


@login_required
def add_course_teacher(request):
    """教師新增課程"""
    # 檢查使用者是否為教師
    if not is_teacher(request.user):
        messages.error(request, '您沒有教師權限。')
        return redirect('grades:main')
    
    if request.method == 'POST':
        form = TeacherCourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            # 自動指派該課程給登入的教師
            course.teacher_fk = request.user.teacher_profile
            course.teacher = f"{request.user.last_name}{request.user.first_name}"
            course.save()
            messages.success(request, f'課程「{course.name}」已成功建立！')
            return redirect('grades:teacher_courses')
    else:
        form = TeacherCourseForm()
    
    return render(request, 'grades/add_course_teacher.html', {
        'form': form,
    })


@login_required
def course_students(request, course_id):
    """顯示課程中的學生列表（教師查看）"""
    # 檢查使用者是否為教師
    if not is_teacher(request.user):
        messages.error(request, '您沒有教師權限。')
        return redirect('grades:main')
    
    course = get_object_or_404(Course, id=course_id)
    
    # 確保該課程是由登入的教師教授的
    if course.teacher_fk != request.user.teacher_profile:
        messages.error(request, '您沒有權限查看此課程的學生。')
        return redirect('grades:teacher_courses')
    
    enrollments = course.enrollments.select_related('student').all()
    remaining_capacity = course.capacity - enrollments.count()
    
    return render(request, 'grades/course_students.html', {
        'course': course,
        'enrollments': enrollments,
        'remaining_capacity': remaining_capacity,
    })


@login_required
def update_student_score(request, enrollment_id):
    """教師編輯學生成績"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    # 檢查使用者是否為該課程的教師
    if not is_teacher(request.user):
        messages.error(request, '您沒有教師權限。')
        return redirect('grades:main')
    
    if enrollment.course.teacher_fk != request.user.teacher_profile:
        messages.error(request, '您沒有權限編輯此課程的學生成績。')
        return redirect('grades:teacher_courses')
    
    if request.method == 'POST':
        form = EnrollmentScoreForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            messages.success(request, f'已成功更新 {enrollment.student.username} 的成績。')
            return redirect('grades:course_students', course_id=enrollment.course.id)
    else:
        form = EnrollmentScoreForm(instance=enrollment)
    
    return render(request, 'grades/update_student_score.html', {
        'form': form,
        'enrollment': enrollment,
    })
