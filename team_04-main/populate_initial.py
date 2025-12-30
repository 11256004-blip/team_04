"""
Populate the database with 3 courses, a test user, and enrollments.

Run this from the project root with:

    python manage.py shell < populate_initial.py

or run directly with Python (it configures Django):

    python populate_initial.py

"""
import os

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scoresystem.settings')
    import django

    django.setup()
    from django.contrib.auth import get_user_model
    from grades.models import Course, Enrollment

    User = get_user_model()

    user, created = User.objects.get_or_create(username='student1')
    if created:
        user.set_password('password')
        user.save()
        print('Created user: student1 / password')
    else:
        print('User student1 already exists')

    c1, _ = Course.objects.get_or_create(code='CS101', defaults={'name': '程式設計', 'teacher': 'Alice'})
    c2, _ = Course.objects.get_or_create(code='MATH101', defaults={'name': '微積分', 'teacher': 'Bob'})
    c3, _ = Course.objects.get_or_create(code='ENG101', defaults={'name': '英文', 'teacher': 'Carol'})

    Enrollment.objects.get_or_create(student=user, course=c1, defaults={'midterm_score': 85, 'final_score': 90})
    Enrollment.objects.get_or_create(student=user, course=c2, defaults={'midterm_score': 78, 'final_score': 82})
    Enrollment.objects.get_or_create(student=user, course=c3, defaults={'midterm_score': 92, 'final_score': 88})

    print('Courses and enrollments ensured')
