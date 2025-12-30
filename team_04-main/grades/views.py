from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST
from .models import Course, Enrollment, UserProfile, Comment
from .forms import CourseForm, EnrollForm, UserProfileEditForm, CommentForm

User = get_user_model()


def _is_admin(user):
    """Check if user is admin"""
    if not user.is_authenticated:
        return False
    return hasattr(user, 'profile') and user.profile.role == 'admin'


def _is_teacher(user):
    """Check if user is teacher"""
    if not user.is_authenticated:
        return False
    return hasattr(user, 'profile') and user.profile.role == 'teacher'


def _is_student(user):
    """Check if user is student"""
    if not user.is_authenticated:
        return False
    return hasattr(user, 'profile') and user.profile.role == 'student'


# ===== AUTHENTICATION VIEWS =====

@login_required
def logout_confirm(request):
    """Show logout confirmation page"""
    context = {
        'user': request.user,
    }
    return render(request, 'grades/logout_confirm.html', context)


@login_required
@require_POST
def custom_logout(request):
    """Logout the user and redirect to home"""
    username = request.user.username
    logout(request)
    
    context = {
        'username': username,
    }
    return render(request, 'grades/logged_out.html', context)


# ===== STUDENT VIEWS =====

def home(request):
    # homepage with a link to the main page
    return render(request, 'grades/home.html')


def main(request):
    # show the logged-in user's enrollments if authenticated,
    # otherwise fall back to the first user in the database (for single-student demo)
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

    return render(request, 'grades/main.html', {
        'student': student,
        'enrollments': enrollments,
        'overall_avg': overall_avg,
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

    if request.method == 'POST':
        form = EnrollForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student = student
            enrollment.save()
            return redirect('grades:main')
    else:
        form = EnrollForm()

    return render(request, 'grades/enroll.html', {'form': form})


def unenroll(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    # only allow the owner to unenroll
    if request.user.is_authenticated and enrollment.student == request.user:
        enrollment.delete()
    return redirect('grades:main')


@login_required
def edit_profile(request):
    """Edit user profile - first name, last name, and avatar"""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('grades:main')
    else:
        form = UserProfileEditForm(instance=profile, user=request.user)
    
    return render(request, 'grades/edit_profile.html', {'form': form})


@login_required
def add_comment(request, course_id):
    """Add or update comment for a course"""
    course = get_object_or_404(Course, id=course_id)
    student = request.user
    
    # Check if student is enrolled in the course
    enrollment = get_object_or_404(Enrollment, student=student, course=course)
    
    # Get existing comment if it exists
    comment = Comment.objects.filter(student=student, course=course).first()
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.student = student
            comment.course = course
            comment.save()
            return redirect('grades:course_comments', course_id=course_id)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'grades/add_comment.html', {
        'form': form,
        'course': course,
        'is_editing': comment is not None,
    })


@login_required
def edit_comment(request, comment_id):
    """Edit own comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Only the author can edit their comment
    if comment.student != request.user:
        return HttpResponseForbidden('你沒有權限編輯此留言')
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('grades:course_comments', course_id=comment.course.id)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'grades/edit_comment.html', {
        'form': form,
        'comment': comment,
        'course': comment.course,
    })


@login_required
def course_comments(request, course_id):
    """View all comments for a course"""
    course = get_object_or_404(Course, id=course_id)
    comments = Comment.objects.filter(course=course).select_related('student').order_by('-created_at')
    
    # Get current user's comment if exists
    user_comment = Comment.objects.filter(student=request.user, course=course).first()
    
    # Check if user is enrolled
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    
    return render(request, 'grades/course_comments.html', {
        'course': course,
        'comments': comments,
        'user_comment': user_comment,
        'is_enrolled': is_enrolled,
    })


def grades(request):
    return render(request, 'grades.html')


# ===== ADMIN VIEWS =====

@login_required
def admin_dashboard(request):
    """Admin dashboard showing overview of users, courses, and enrollments"""
    if not _is_admin(request.user):
        return HttpResponseForbidden('只有管理者可以訪問此頁面')

    stats = {
        'total_students': User.objects.filter(profile__role='student').count(),
        'total_teachers': User.objects.filter(profile__role='teacher').count(),
        'total_courses': Course.objects.count(),
        'total_enrollments': Enrollment.objects.count(),
    }

    context = {
        'stats': stats,
        'recent_enrollments': Enrollment.objects.select_related('student', 'course').order_by('-id')[:10],
    }

    return render(request, 'grades/admin/dashboard.html', context)


@login_required
def admin_users(request):
    """Admin page to manage all users"""
    if not _is_admin(request.user):
        return HttpResponseForbidden('只有管理者可以訪問此頁面')

    users = User.objects.select_related('profile').all()
    return render(request, 'grades/admin/users.html', {'users': users})


@login_required
def admin_user_detail(request, user_id):
    """Admin page to view/edit a specific user"""
    if not _is_admin(request.user):
        return HttpResponseForbidden('只有管理者可以訪問此頁面')

    user = get_object_or_404(User, id=user_id)
    enrollments = user.enrollments.select_related('course').all() if hasattr(user, 'enrollments') else []

    return render(request, 'grades/admin/user_detail.html', {
        'target_user': user,
        'enrollments': enrollments,
    })


@login_required
def admin_courses(request):
    """Admin page to manage all courses"""
    if not _is_admin(request.user):
        return HttpResponseForbidden('只有管理者可以訪問此頁面')

    courses = Course.objects.select_related('teacher').all()
    return render(request, 'grades/admin/courses.html', {'courses': courses})


@login_required
def admin_course_detail(request, course_id):
    """Admin page to view/edit a specific course"""
    if not _is_admin(request.user):
        return HttpResponseForbidden('只有管理者可以訪問此頁面')

    course = get_object_or_404(Course, id=course_id)
    enrollments = course.enrollments.select_related('student').all()

    return render(request, 'grades/admin/course_detail.html', {
        'course': course,
        'enrollments': enrollments,
    })


# ===== TEACHER VIEWS =====

@login_required
def teacher_dashboard(request):
    """Teacher dashboard showing their courses and students"""
    if not _is_teacher(request.user):
        return HttpResponseForbidden('只有教師可以訪問此頁面')

    # Get courses taught by this teacher
    courses = Course.objects.filter(teacher=request.user)
    stats = {
        'total_courses': courses.count(),
        'total_students': Enrollment.objects.filter(course__in=courses).values('student').distinct().count(),
        'total_enrollments': Enrollment.objects.filter(course__in=courses).count(),
    }

    context = {
        'stats': stats,
        'courses': courses,
    }

    return render(request, 'grades/teacher/dashboard.html', context)


@login_required
def teacher_course_detail(request, course_id):
    """Teacher page to view and manage a specific course"""
    if not _is_teacher(request.user):
        return HttpResponseForbidden('只有教師可以訪問此頁面')

    course = get_object_or_404(Course, id=course_id)

    # Check if the logged-in teacher owns this course
    if course.teacher != request.user:
        return HttpResponseForbidden('你沒有權限管理此課程')

    enrollments = course.enrollments.select_related('student').all()

    context = {
        'course': course,
        'enrollments': enrollments,
    }

    return render(request, 'grades/teacher/course_detail.html', context)


@login_required
@require_http_methods(["POST"])
def teacher_update_grade(request, enrollment_id):
    """Teacher endpoint to update a student's grade"""
    if not _is_teacher(request.user):
        return HttpResponseForbidden('只有教師可以訪問此頁面')

    enrollment = get_object_or_404(Enrollment, id=enrollment_id)

    # Check if the logged-in teacher owns this course
    if enrollment.course.teacher != request.user:
        return HttpResponseForbidden('你沒有權限編輯此成績')

    # Update scores
    midterm = request.POST.get('midterm_score')
    final = request.POST.get('final_score')

    if midterm:
        enrollment.midterm_score = float(midterm)
    if final:
        enrollment.final_score = float(final)

    enrollment.save()

    return redirect('grades:teacher_course_detail', course_id=enrollment.course.id)


@login_required
def teacher_add_course(request):
    """Teacher page to add a new course"""
    if not _is_teacher(request.user):
        return HttpResponseForbidden('只有教師可以訪問此頁面')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect('grades:teacher_dashboard')
    else:
        form = CourseForm()

    return render(request, 'grades/teacher/add_course.html', {'form': form})


@login_required
def teacher_student_list(request):
    """Teacher page to view all students in their courses"""
    if not _is_teacher(request.user):
        return HttpResponseForbidden('只有教師可以訪問此頁面')

    # Get all courses taught by this teacher
    courses = Course.objects.filter(teacher=request.user)
    
    # Get filter parameter
    course_id = request.GET.get('course_id')
    
    if course_id:
        try:
            selected_course = Course.objects.get(id=course_id, teacher=request.user)
            enrollments = selected_course.enrollments.select_related('student', 'course').all()
        except Course.DoesNotExist:
            return HttpResponseForbidden('你沒有權限訪問此課程')
    else:
        # Show all enrollments from all courses if no specific course selected
        enrollments = Enrollment.objects.filter(course__in=courses).select_related('student', 'course').all()
        selected_course = None

    context = {
        'courses': courses,
        'enrollments': enrollments,
        'selected_course': selected_course,
    }

    return render(request, 'grades/teacher/student_list.html', context)


@login_required
def teacher_grade_entry(request, course_id):
    """Teacher page to enter grades for a course (midterm and final)"""
    if not _is_teacher(request.user):
        return HttpResponseForbidden('只有教師可以訪問此頁面')

    course = get_object_or_404(Course, id=course_id)

    # Check if the logged-in teacher owns this course
    if course.teacher != request.user:
        return HttpResponseForbidden('你沒有權限編輯此課程的成績')

    enrollments = course.enrollments.select_related('student').all()

    if request.method == 'POST':
        # Process grade updates
        for enrollment in enrollments:
            midterm_key = f'midterm_{enrollment.id}'
            final_key = f'final_{enrollment.id}'
            
            midterm = request.POST.get(midterm_key)
            final = request.POST.get(final_key)
            
            if midterm:
                try:
                    enrollment.midterm_score = float(midterm)
                except ValueError:
                    pass
            
            if final:
                try:
                    enrollment.final_score = float(final)
                except ValueError:
                    pass
            
            enrollment.save()
        
        return redirect('grades:teacher_dashboard')

    context = {
        'course': course,
        'enrollments': enrollments,
    }

    return render(request, 'grades/teacher/grade_entry.html', context)
