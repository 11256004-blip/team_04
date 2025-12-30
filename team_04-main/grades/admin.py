from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Course, Enrollment, UserProfile


# ===== 卸載並重新註冊 User Admin - 新增教師帳號 =====

admin.site.unregister(User)  # 卸載原有的 User Admin


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """擴展 Django 原生 User Admin，新增快速建立教師的功能"""
    
    change_list_template = 'admin/user_change_list.html'
    
    def get_urls(self):
        """新增自訂 URL 用於建立教師"""
        urls = super().get_urls()
        custom_urls = [
            path('create-teacher/', self.admin_site.admin_view(self.create_teacher_view), 
                 name='create_teacher'),
        ]
        return custom_urls + urls
    
    def create_teacher_view(self, request):
        """建立教師帳號的視圖"""
        if request.method == 'POST':
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            department = request.POST.get('department')
            
            # 檢查用戶名是否已存在
            if User.objects.filter(username=username).exists():
                messages.error(request, f'用戶名 "{username}" 已存在！')
                return render(request, 'admin/create_teacher.html')
            
            # 檢查郵箱是否已存在
            if email and User.objects.filter(email=email).exists():
                messages.error(request, f'郵箱 "{email}" 已存在！')
                return render(request, 'admin/create_teacher.html')
            
            try:
                # 建立用戶
                user = User.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password
                )
                
                # 建立 UserProfile 並設定為教師
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'role': 'teacher',
                        'department': department
                    }
                )
                
                messages.success(request, f'✅ 教師帳號 "{username}" 已成功建立！')
                return redirect('admin:auth_user_changelist')
            
            except Exception as e:
                messages.error(request, f'❌ 建立教師失敗: {str(e)}')
                return render(request, 'admin/create_teacher.html')
        
        return render(request, 'admin/create_teacher.html')
    
    def changelist_view(self, request, extra_context=None):
        """在用戶列表頁面新增 "建立教師" 按鈕"""
        extra_context = extra_context or {}
        extra_context['show_create_teacher_button'] = True
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """用戶角色管理"""
    list_display = ('user', 'role', 'department', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'department')
    list_editable = ('role', 'department')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """課程管理 - 支援快速新增課程和指定教師"""
    list_display = ('id', 'name', 'code', 'teacher', 'student_count', 'created_at')
    list_filter = ('created_at', 'teacher')
    search_fields = ('name', 'code')
    change_list_template = 'admin/course_change_list.html'
    
    # 新增和編輯頁面的字段配置
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'teacher', 'description')
        }),
        ('時間戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    # 在編輯頁面限制教師選擇為教師角色
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'teacher':
            # 只顯示角色為 'teacher' 的用戶
            kwargs['queryset'] = User.objects.filter(profile__role='teacher')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def student_count(self, obj):
        """顯示該課程的學生人數"""
        count = obj.enrollments.count()
        return f'{count} 人'
    student_count.short_description = '學生人數'
    
    def get_urls(self):
        """新增自訂 URL 用於快速建立課程"""
        urls = super().get_urls()
        custom_urls = [
            path('create-quick/', self.admin_site.admin_view(self.create_course_quick_view), 
                 name='create_course_quick'),
        ]
        return custom_urls + urls
    
    def create_course_quick_view(self, request):
        """快速建立課程的視圖"""
        teachers = User.objects.filter(profile__role='teacher').values_list('id', 'first_name', 'last_name', 'username')
        
        if request.method == 'POST':
            name = request.POST.get('name')
            code = request.POST.get('code')
            teacher_id = request.POST.get('teacher')
            description = request.POST.get('description')
            
            # 檢查課程代碼是否已存在
            if Course.objects.filter(code=code).exists():
                messages.error(request, f'課程代碼 "{code}" 已存在！')
                return render(request, 'admin/create_course.html', {'teachers': teachers})
            
            try:
                teacher = None
                if teacher_id:
                    teacher = User.objects.get(id=teacher_id)
                
                # 建立課程
                course = Course.objects.create(
                    name=name,
                    code=code,
                    teacher=teacher,
                    description=description
                )
                
                messages.success(request, f'✅ 課程 "{name}" (代碼: {code}) 已成功建立！')
                return redirect('admin:grades_course_changelist')
            
            except Exception as e:
                messages.error(request, f'❌ 建立課程失敗: {str(e)}')
                return render(request, 'admin/create_course.html', {'teachers': teachers})
        
        return render(request, 'admin/create_course.html', {'teachers': teachers})
    
    def changelist_view(self, request, extra_context=None):
        """在課程列表頁面新增 "快速建立課程" 按鈕"""
        extra_context = extra_context or {}
        extra_context['show_create_course_button'] = True
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """學生註冊管理"""
    list_display = ('id', 'student', 'course', 'midterm_score', 'final_score', 'average')
    list_filter = ('course', 'student')
    search_fields = ('student__username', 'course__name')

    def average(self, obj):
        return obj.average()
