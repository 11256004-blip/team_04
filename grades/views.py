from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Course, Enrollment
from .forms import CourseForm, EnrollForm


def home(request):
    # homepage with a link to the main page
    return render(request, 'grades/home.html')


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
from django.shortcuts import render

def grades(request):
    return render(request, 'grades.html')
