"""
Add enrollments for team04 user to the 3 existing courses.

Run with: python add_team04_enrollments.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scoresystem.settings')
django.setup()

from django.contrib.auth import get_user_model
from grades.models import Course, Enrollment

User = get_user_model()

# Get or create team04 user
user, created = User.objects.get_or_create(username='team04')
if created:
    user.set_password('password')
    user.save()
    print('Created user: team04')
else:
    print('User team04 already exists')

# Get the 3 courses (should already exist from populate_initial.py)
try:
    c1 = Course.objects.get(code='CS101')
    c2 = Course.objects.get(code='MATH101')
    c3 = Course.objects.get(code='ENG101')
    
    # Create enrollments for team04
    e1, created1 = Enrollment.objects.get_or_create(
        student=user, 
        course=c1, 
        defaults={'midterm_score': 85, 'final_score': 90}
    )
    if created1:
        print(f'Created enrollment: {user.username} -> {c1.name}')
    else:
        print(f'Enrollment already exists: {user.username} -> {c1.name}')
    
    e2, created2 = Enrollment.objects.get_or_create(
        student=user, 
        course=c2, 
        defaults={'midterm_score': 78, 'final_score': 82}
    )
    if created2:
        print(f'Created enrollment: {user.username} -> {c2.name}')
    else:
        print(f'Enrollment already exists: {user.username} -> {c2.name}')
    
    e3, created3 = Enrollment.objects.get_or_create(
        student=user, 
        course=c3, 
        defaults={'midterm_score': 92, 'final_score': 88}
    )
    if created3:
        print(f'Created enrollment: {user.username} -> {c3.name}')
    else:
        print(f'Enrollment already exists: {user.username} -> {c3.name}')
    
    print('\n✅ team04 enrollments setup complete!')
    print('Refresh your browser to see the courses.')

except Course.DoesNotExist:
    print('❌ Courses not found. Please run populate_initial.py first to create courses.')
