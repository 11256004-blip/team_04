from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html
from .models import Course, Enrollment, UserProfile, Teacher


# ==================== 教師管理 ====================

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    """教師管理後台"""
    
    list_display = ('display_name', 'department', 'phone', 'course_count', 'created_at')
    list_filter = ('department', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'department')
    readonly_fields = ('created_at', 'updated_at', 'course_count_detail')
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('user', 'department', 'office')
        }),
        ('聯絡資訊', {
            'fields': ('phone', 'office_hours')
        }),
        ('統計資訊', {
            'fields': ('course_count_detail',),
            'classes': ('collapse',)
        }),
        ('時間戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def display_name(self, obj):
        """顯示教師名稱"""
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.last_name} {obj.user.first_name}"
        return f"{obj.user.username}"
    display_name.short_description = '教師名稱'
    
    def course_count(self, obj):
        """顯示授課課程數"""
        count = obj.courses.count()
        return format_html(
            '<span style="background-color: #4CAF50; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            count
        )
    course_count.short_description = '授課課程'
    
    def course_count_detail(self, obj):
        """詳細顯示授課課程"""
        courses = obj.courses.all()
        if not courses:
            return "目前沒有授課課程"
        return format_html(
            '<ul style="margin: 0; padding-left: 20px;">{}</ul>',
            format_html(
                ''.join([f'<li>{course.name} ({course.code})</li>' for course in courses])
            )
        )
    course_count_detail.short_description = '授課課程列表'


# ==================== 課程管理 ====================

class EnrollmentInline(admin.TabularInline):
    """課程中內聯顯示選課學生"""
    model = Enrollment
    extra = 0
    fields = ('student', 'midterm_score', 'final_score', 'average_score')
    readonly_fields = ('student', 'midterm_score', 'final_score', 'average_score')
    can_delete = False
    
    def average_score(self, obj):
        """顯示平均成績"""
        avg = obj.average()
        if avg is None:
            return "-"
        return format_html(
            '<strong style="color: {};">{:.2f}</strong>',
            '#4CAF50' if avg >= 60 else '#FF9800',
            avg
        )
    average_score.short_description = '平均分數'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """課程管理後台"""
    
    list_display = ('code', 'name', 'teacher_name', 'credits', 'enrollment_count', 'capacity', 'status')
    list_filter = ('teacher_fk__user__last_name', 'credits')
    search_fields = ('code', 'name', 'teacher__icontains', 'teacher_fk__user__first_name', 'teacher_fk__user__last_name', 'description')
    readonly_fields = ('enrollment_count_detail',)
    inlines = [EnrollmentInline]
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('name', 'code', 'teacher', 'teacher_fk')
        }),
        ('課程詳情', {
            'fields': ('description', 'credits', 'capacity')
        }),
        ('選課資訊', {
            'fields': ('enrollment_count_detail',)
        }),
    )
    
    def teacher_name(self, obj):
        """顯示授課教師"""
        if obj.teacher_fk:
            if obj.teacher_fk.user.first_name and obj.teacher_fk.user.last_name:
                return f"{obj.teacher_fk.user.last_name}{obj.teacher_fk.user.first_name}"
            return obj.teacher_fk.user.username
        return obj.teacher or "未分配"
    teacher_name.short_description = '授課教師'
    
    def enrollment_count(self, obj):
        """顯示選課人數"""
        count = obj.enrollments.count()
        return format_html(
            '<span style="background-color: #2196F3; color: white; padding: 3px 10px; border-radius: 3px;">{}/{}</span>',
            count,
            obj.capacity
        )
    enrollment_count.short_description = '選課人數'
    
    def status(self, obj):
        """顯示課程狀態"""
        count = obj.enrollments.count()
        if count == 0:
            color = '#9E9E9E'
            status_text = '未開課'
        elif count >= obj.capacity:
            color = '#F44336'
            status_text = '已滿班'
        elif count >= obj.capacity * 0.8:
            color = '#FF9800'
            status_text = '名額緊張'
        else:
            color = '#4CAF50'
            status_text = '正常'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            status_text
        )
    status.short_description = '狀態'
    
    def enrollment_count_detail(self, obj):
        """詳細顯示選課學生"""
        enrollments = obj.enrollments.select_related('student').all()
        if not enrollments:
            return "目前沒有學生選課"
        
        html_items = []
        for enrollment in enrollments:
            avg = enrollment.average()
            avg_text = f"{avg:.2f}" if avg else "-"
            html_items.append(
                f'<li>{enrollment.student.username} - 期中: {enrollment.midterm_score or "-"}, '
                f'期末: {enrollment.final_score or "-"}, 平均: {avg_text}</li>'
            )
        
        return format_html(
            '<ul style="margin: 0; padding-left: 20px;">{}</ul>',
            format_html(''.join(html_items))
        )
    enrollment_count_detail.short_description = '選課學生列表'


# ==================== 選課管理 ====================

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """選課記錄管理後台"""
    
    list_display = ('student', 'course', 'midterm_score', 'final_score', 'average_score')
    list_filter = ('course__code', 'course__teacher')
    search_fields = ('student__username', 'course__code', 'course__name')
    readonly_fields = ('average_score_detail',)
    
    fieldsets = (
        ('選課資訊', {
            'fields': ('student', 'course', 'enrollment_date')
        }),
        ('成績', {
            'fields': ('midterm_score', 'final_score', 'average_score_detail')
        }),
    )
    
    def average_score(self, obj):
        """顯示平均分數"""
        avg = obj.average()
        if avg is None:
            return "-"
        return format_html(
            '<strong style="color: {};">{:.2f}</strong>',
            '#4CAF50' if avg >= 60 else '#FF9800',
            avg
        )
    average_score.short_description = '平均分數'
    
    def average_score_detail(self, obj):
        """詳細顯示平均分數"""
        avg = obj.average()
        if avg is None:
            return "尚未有完整成績"
        return format_html(
            '<strong style="font-size: 1.2em; color: {};">{:.2f} 分</strong>',
            '#4CAF50' if avg >= 60 else '#FF9800',
            avg
        )
    average_score_detail.short_description = '平均分數'


# ==================== 用戶檔案管理 ====================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')


# ==================== 增強 User Admin ====================

class TeacherInline(admin.StackedInline):
    """在 User 中內聯顯示教師資訊"""
    model = Teacher
    extra = 0
    fields = ('department', 'office', 'phone', 'office_hours')


class UserProfileInline(admin.StackedInline):
    """在 User 中內聯顯示個人檔案"""
    model = UserProfile
    extra = 0
    fields = ('avatar', 'bio')


class CustomUserAdmin(admin.ModelAdmin):
    """增強的 User 管理後台"""
    
    list_display = ('username', 'full_name', 'email', 'is_teacher', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('username', 'first_name', 'last_name', 'email')
        }),
        ('密碼', {
            'fields': ('password',),
            'classes': ('collapse',)
        }),
        ('權限', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('重要日期', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [UserProfileInline, TeacherInline]
    
    def full_name(self, obj):
        """顯示全名"""
        full_name = obj.get_full_name()
        return full_name if full_name else obj.username
    full_name.short_description = '全名'
    
    def is_teacher(self, obj):
        """顯示是否為教師"""
        if hasattr(obj, 'teacher_profile'):
            return format_html(
                '<span style="background-color: #4CAF50; color: white; padding: 3px 10px; border-radius: 3px;">是</span>'
            )
        return "否"
    is_teacher.short_description = '教師'


# 取消註冊原始的 User Admin，然後重新註冊增強版本
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
