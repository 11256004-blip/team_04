# 學生帳號功能實現 - 技術總結

## 📋 實現概覽

已成功為學生帳號實現三個核心功能，涵蓋個人資訊管理和課程互動功能。

---

## 1️⃣ 功能一: 修改個人資訊 (姓名、個人頭像)

### 技術實現

#### 模型層 (Models)
```python
# UserProfile 新增字段
avatar = models.ImageField(
    upload_to='avatars/',
    blank=True,
    null=True,
    default='avatars/default_avatar.png'
)
```

#### 表單層 (Forms)
```python
class UserProfileEditForm(forms.ModelForm):
    # 額外的 User 字段
    first_name = forms.CharField(...)
    last_name = forms.CharField(...)
    
    class Meta:
        model = UserProfile
        fields = ['avatar']
    
    def save(self):
        # 同時保存 User 和 UserProfile
        profile = super().save()
        user.first_name = ...
        user.last_name = ...
        user.save()
        return profile
```

#### 視圖層 (Views)
```python
@login_required
def edit_profile(request):
    profile = request.user.profile
    
    if request.method == 'POST':
        form = UserProfileEditForm(
            request.POST, 
            request.FILES,      # 支持文件上傳
            instance=profile,
            user=request.user
        )
        if form.is_valid():
            form.save()
            return redirect('grades:main')
    else:
        form = UserProfileEditForm(instance=profile, user=request.user)
    
    return render(request, 'grades/edit_profile.html', {'form': form})
```

#### 模板層 (Templates)
```html
<!-- 頭像預覽 -->
{% if request.user.profile.avatar %}
    <img src="{{ request.user.profile.avatar.url }}" alt="頭像">
{% else %}
    <div>👤</div>
{% endif %}

<!-- 表單 -->
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    
    <!-- 名字輸入 -->
    <input type="text" name="first_name" value="{{ form.first_name.value }}">
    
    <!-- 姓氏輸入 -->
    <input type="text" name="last_name" value="{{ form.last_name.value }}">
    
    <!-- 頭像上傳 -->
    <input type="file" name="avatar" accept="image/*">
    
    <button type="submit">保存</button>
</form>
```

#### 配置層 (Settings)
```python
# 媒體文件設定
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

#### 路由層 (URLs)
```python
path('edit_profile/', views.edit_profile, name='edit_profile'),
```

### 功能特點
- ✅ 支持多種圖片格式 (JPG, PNG, GIF, WebP)
- ✅ 圖片預覽顯示
- ✅ 自動保存到 `media/avatars/` 目錄
- ✅ 開發環境自動提供媒體文件服務
- ✅ 優雅的表單驗證

---

## 2️⃣ 功能二: 對課程留言 (可修改自己的留言)

### 技術實現

#### 模型層 (Models)
```python
class Comment(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # 每個學生每個課程只能有一個留言
        unique_together = ('student', 'course')
        # 按最新優先排序
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.name}"
```

#### 表單層 (Forms)
```python
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': '輸入你對課程的留言...',
            }),
        }
```

#### 視圖層 (Views)
```python
@login_required
def add_comment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = request.user
    
    # 驗證學生已選課
    enrollment = get_object_or_404(Enrollment, student=student, course=course)
    
    # 檢查是否存在現有留言 (編輯模式)
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
```

#### 編輯留言視圖
```python
@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # 只有作者可以編輯
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
```

### 功能特點
- ✅ 自動偵測新增/編輯模式
- ✅ 權限驗證 (只有已選課學生)
- ✅ 所有權檢查 (只有作者可編輯)
- ✅ 時間戳記 (創建和更新時間分開)
- ✅ 1000 字元限制
- ✅ 實時字數統計

---

## 3️⃣ 功能三: 查看全部留言

### 技術實現

#### 視圖層 (Views)
```python
@login_required
def course_comments(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # 獲取課程的所有留言，並關聯學生信息
    comments = Comment.objects.filter(course=course)\
        .select_related('student')\
        .order_by('-created_at')
    
    # 獲取當前用戶的留言 (如存在)
    user_comment = Comment.objects.filter(
        student=request.user,
        course=course
    ).first()
    
    # 檢查用戶是否已選課
    is_enrolled = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).exists()
    
    return render(request, 'grades/course_comments.html', {
        'course': course,
        'comments': comments,
        'user_comment': user_comment,
        'is_enrolled': is_enrolled,
    })
```

#### 模板層 (Templates)
```html
<!-- 課程資訊頭部 -->
<div class="course-header">
    <h1>{{ course.name }}</h1>
    <p>課程代碼: {{ course.code }}</p>
</div>

<!-- 統計卡片 -->
<div class="stats">
    <div class="stat-card">
        <p class="stat-value">{{ comments.count }}</p>
        <p class="stat-label">課程留言</p>
    </div>
</div>

<!-- 操作按鈕 -->
{% if is_enrolled %}
    {% if user_comment %}
        <a href="{% url 'grades:edit_comment' user_comment.id %}">
            ✏️ 編輯我的留言
        </a>
    {% else %}
        <a href="{% url 'grades:add_comment' course.id %}">
            💬 新增留言
        </a>
    {% endif %}
{% endif %}

<!-- 留言列表 -->
<div class="comments-list">
    {% for comment in comments %}
        <div class="comment-card">
            <!-- 作者信息 -->
            <div class="comment-header">
                <img src="{{ comment.student.profile.avatar.url }}" 
                     alt="{{ comment.student.username }}" 
                     class="avatar">
                <div class="user-info">
                    <p class="username">
                        {{ comment.student.get_full_name|default:comment.student.username }}
                        {% if comment.student == request.user %}
                            <span class="badge">我</span>
                        {% endif %}
                    </p>
                    <p class="time">
                        {% if comment.updated_at > comment.created_at %}
                            編輯於 {{ comment.updated_at|date:"Y-m-d H:i" }}
                        {% else %}
                            {{ comment.created_at|date:"Y-m-d H:i" }}
                        {% endif %}
                    </p>
                </div>
                
                <!-- 編輯按鈕 (僅限作者) -->
                {% if comment.student == request.user and is_enrolled %}
                    <a href="{% url 'grades:edit_comment' comment.id %}">✏️</a>
                {% endif %}
            </div>
            
            <!-- 留言內容 -->
            <div class="comment-content">
                {{ comment.content|linebreaks }}
            </div>
        </div>
    {% empty %}
        <div class="empty-state">
            <p>暫無留言</p>
        </div>
    {% endfor %}
</div>
```

### 功能特點
- ✅ 顯示課程所有留言
- ✅ 自動關聯學生頭像和名字
- ✅ 時間戳記 (區分創建/編輯)
- ✅ 自己的留言特殊標示 (藍色邊框)
- ✅ 快速編輯按鈕 (僅限作者)
- ✅ 友好的空狀態提示
- ✅ 按時間倒序排列

---

## 🔐 權限控制系統

### 認證層
```python
# 所有功能都需要登入
@login_required
def edit_profile(request): ...
def add_comment(request): ...
```

### 授權層
```python
# 檢查學生是否已選課
enrollment = get_object_or_404(Enrollment, student=student, course=course)

# 檢查是否為留言作者
if comment.student != request.user:
    return HttpResponseForbidden('你沒有權限編輯此留言')

# 檢查是否已選課 (用於決定UI顯示)
is_enrolled = Enrollment.objects.filter(
    student=request.user,
    course=course
).exists()
```

---

## 📊 資料庫遷移

### 遷移檔案
```
grades/migrations/0003_userprofile_avatar_comment.py
```

### 遷移操作
```bash
python manage.py makemigrations  # 建立遷移
python manage.py migrate         # 應用遷移
```

### 表結構

**Comment 表**
```sql
CREATE TABLE grades_comment (
    id BIGINT PRIMARY KEY,
    student_id INT NOT NULL REFERENCES auth_user,
    course_id INT NOT NULL REFERENCES grades_course,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME AUTO_UPDATE,
    UNIQUE (student_id, course_id)
);

CREATE INDEX idx_course_comments ON grades_comment(course_id);
CREATE INDEX idx_student_comments ON grades_comment(student_id);
```

---

## 🎨 前端設計

### 設計語言
- **色系**: 紫色梯度 (#667eea → #764ba2)
- **字型**: Segoe UI, Tahoma, Geneva
- **佈局**: 響應式網格
- **動畫**: 流暢的過渡效果

### 組件設計

#### 按鈕樣式
```css
.btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 25px;
    border-radius: 25px;
    transition: transform 0.3s, box-shadow 0.3s;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}
```

#### 卡片設計
```css
.card {
    background: white;
    border-radius: 15px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    padding: 30px;
}
```

#### 頭像設計
```css
.avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #667eea;
}
```

---

## 🔄 數據流程

### 修改個人資訊流程
```
User Input
   ↓
Form Validation (Django Forms)
   ↓
Check Authentication (@login_required)
   ↓
Process File Upload (ImageField)
   ↓
Save to Database
   ↓
Redirect to Success Page
   ↓
Display Updated Profile
```

### 發表留言流程
```
User Input
   ↓
Form Validation
   ↓
Check Authentication
   ↓
Check Enrollment (IsEnrolled?)
   ↓
Check Unique Constraint (Student + Course)
   ↓
Save to Database
   ↓
Redirect to Comments Page
   ↓
Display Comment in List
```

### 編輯留言流程
```
Click Edit Button
   ↓
Load Comment Data
   ↓
Check Ownership (Is Author?)
   ↓
Display Edit Form
   ↓
User Modifies Content
   ↓
Update Database (Auto-update timestamp)
   ↓
Redirect to Comments Page
   ↓
Show Updated Comment
```

---

## 📦 依賴和配置

### 新增 Python 包
```
Pillow>=9.0.0  # 圖片處理
```

### Django 配置
```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'grades',  # 應用
]

MIDDLEWARE = [
    # ... 所有中間件
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,  # 自動尋找應用內的 templates
        'OPTIONS': {
            'context_processors': [
                # ... 上下文處理器
            ],
        },
    },
]

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### URL 配置
```python
# scoresystem/urls.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... 其他路由
]

# 開發環境提供媒體文件
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
```

---

## ✅ 驗證清單

系統檢查:
```bash
$ python manage.py check
System check identified no issues (0 silenced).
```

遷移檢查:
```bash
$ python manage.py makemigrations
Migrations for 'grades':
  grades\migrations\0003_userprofile_avatar_comment.py
    + Add field avatar to userprofile
    + Create model Comment
```

數據庫檢查:
```bash
$ python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, grades, sessions
Running migrations:
  Applying grades.0003_userprofile_avatar_comment... OK
```

---

## 🎯 結論

成功實現了學生帳號的三個核心功能，涵蓋個人資訊管理、課程互動和社群功能。系統設計遵循 Django 最佳實踐，包括適當的權限控制、資料驗證和錯誤處理。所有功能都通過系統檢查，數據庫遷移成功應用，應用已準備好進行全面測試和部署。
