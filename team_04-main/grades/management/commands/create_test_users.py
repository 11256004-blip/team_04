from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from grades.models import UserProfile, Course, Enrollment
from django.utils import timezone


class Command(BaseCommand):
    help = '建立測試用戶與課程 - 包括管理員、教師和學生'

    def handle(self, *args, **options):
        # 建立管理員
        admin_user, admin_created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': '系統',
                'last_name': '管理員',
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if admin_created:
            admin_user.set_password('admin123')
            admin_user.save()
            admin_profile, _ = UserProfile.objects.get_or_create(
                user=admin_user,
                defaults={'role': 'admin', 'department': '系統部'}
            )
            self.stdout.write(self.style.SUCCESS(f'✅ 已建立管理員: admin (密碼: admin123)'))
        else:
            self.stdout.write('ℹ️  管理員已存在: admin')

        # 建立教師
        teachers_data = [
            ('teacher1', '王', '小芬', 'teacher1@example.com', '資訊系'),
            ('teacher2', '李', '明穎', 'teacher2@example.com', '數學系'),
        ]
        
        teachers = []
        for username, last_name, first_name, email, dept in teachers_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                }
            )
            if created:
                user.set_password('teacher123')
                user.save()
                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'role': 'teacher', 'department': dept}
                )
                self.stdout.write(self.style.SUCCESS(f'✅ 已建立教師: {username} (密碼: teacher123)'))
            else:
                self.stdout.write(f'ℹ️  教師已存在: {username}')
            teachers.append(user)

        # 建立學生
        students_data = [
            ('student1', '陳', '家豪', 'student1@example.com'),
            ('student2', '林', '怡涵', 'student2@example.com'),
            ('student3', '黃', '大明', 'student3@example.com'),
            ('student4', '劉', '美美', 'student4@example.com'),
        ]
        
        students = []
        for username, last_name, first_name, email in students_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                }
            )
            if created:
                user.set_password('student123')
                user.save()
                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'role': 'student', 'department': '學生'}
                )
                self.stdout.write(self.style.SUCCESS(f'✅ 已建立學生: {username} (密碼: student123)'))
            else:
                self.stdout.write(f'ℹ️  學生已存在: {username}')
            students.append(user)

        # 建立課程
        courses_data = [
            ('CS101', 'Python 程式設計', '使用 Python 學習程式設計基礎', teachers[0]),
            ('CS102', 'Web 開發', '學習 HTML、CSS 和 JavaScript', teachers[0]),
            ('MATH101', '微積分', '微積分基礎數學', teachers[1]),
            ('MATH102', '線性代數', '線性代數與矩陣運算', teachers[1]),
        ]
        
        for code, name, description, teacher in courses_data:
            course, created = Course.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': description,
                    'teacher': teacher,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ 已建立課程: {code} - {name}'))
            else:
                self.stdout.write(f'ℹ️  課程已存在: {code}')

        # 為學生建立註冊和成績
        courses = Course.objects.all()
        for i, student in enumerate(students):
            # 每個學生隨機註冊 2-3 門課程
            enrolled_courses = courses[i % len(courses):(i % len(courses)) + 2]
            for course in enrolled_courses:
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={
                        'midterm_score': 70 + (i * 5) % 30,
                        'final_score': 72 + (i * 7) % 28,
                    }
                )
                if created:
                    self.stdout.write(f'✅ 已為 {student.username} 建立 {course.code} 的註冊')

        self.stdout.write(self.style.SUCCESS('\n🎉 測試用戶和課程建立完成！'))
        self.stdout.write('\n📋 測試帳戶信息:')
        self.stdout.write('  管理員: admin / admin123')
        self.stdout.write('  教師: teacher1 / teacher123, teacher2 / teacher123')
        self.stdout.write('  學生: student1-4 / student123')
