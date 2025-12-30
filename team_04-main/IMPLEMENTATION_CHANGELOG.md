# 學生帳號功能 - 實現變更清單

## 📋 實現總覽

日期: 2025-12-30
功能: 學生帳號功能增強
狀態: ✅ 完成 (0 errors, 0 warnings)

---

## 🔄 新增模型 (Models)

### 1. Comment 模型
**文件**: `grades/models.py`
**變更**: 添加新模型

```python
class Comment(models.Model):
    """課程留言模型"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('student', 'course')
```

### 2. UserProfile 模型更新
**文件**: `grades/models.py`
**變更**: 添加 avatar 欄位

```python
class UserProfile(models.Model):
    # ... 原有欄位 ...
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default_avatar.png')
```

---

## 📝 新增表單 (Forms)

### 文件: `grades/forms.py`

#### 1. UserProfileEditForm
```python
class UserProfileEditForm(forms.ModelForm):
    """編輯使用者資訊表單"""
    first_name = forms.CharField(...)
    last_name = forms.CharField(...)
    
    class Meta:
        model = UserProfile
        fields = ['avatar']
```

#### 2. CommentForm
```python
class CommentForm(forms.ModelForm):
    """課程留言表單"""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }
```

---

## 🖼️ 新增視圖 (Views)

### 文件: `grades/views.py`

#### 1. edit_profile(request)
```python
@login_required
def edit_profile(request):
    """編輯個人資訊"""
    profile = request.user.profile
    # ... 表單處理邏輯
```

#### 2. add_comment(request, course_id)
```python
@login_required
def add_comment(request, course_id):
    """添加/編輯課程留言"""
    course = get_object_or_404(Course, id=course_id)
    # ... 留言處理邏輯
```

#### 3. edit_comment(request, comment_id)
```python
@login_required
def edit_comment(request, comment_id):
    """編輯自己的留言"""
    comment = get_object_or_404(Comment, id=comment_id)
    # ... 只允許作者編輯
```

#### 4. course_comments(request, course_id)
```python
@login_required
def course_comments(request, course_id):
    """查看課程全部留言"""
    course = get_object_or_404(Course, id=course_id)
    comments = Comment.objects.filter(course=course)
    # ... 顯示所有留言
```

---

## 🔗 URL 路由 (URLs)

### 文件: `grades/urls.py`

**新增路由**:
```python
# Student profile routes
path('edit_profile/', views.edit_profile, name='edit_profile'),
path('add_comment/<int:course_id>/', views.add_comment, name='add_comment'),
path('edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
path('course_comments/<int:course_id>/', views.course_comments, name='course_comments'),
```

---

## 🎨 新增模板 (Templates)

### 1. edit_profile.html
**路徑**: `grades/templates/grades/edit_profile.html`
**功能**: 修改個人資訊表單
**特色**:
- 圓形頭像預覽
- 名字/姓氏輸入
- 文件上傳器
- 實時文件名顯示

### 2. add_comment.html
**路徑**: `grades/templates/grades/add_comment.html`
**功能**: 新增課程留言表單
**特色**:
- 多行文本區域
- 實時字數統計
- 1000 字元限制
- 課程綁定確認

### 3. edit_comment.html
**路徑**: `grades/templates/grades/edit_comment.html`
**功能**: 編輯自己的留言
**特色**:
- 時間戳記顯示
- 相同的表單介面
- 字數統計

### 4. course_comments.html
**路徑**: `grades/templates/grades/course_comments.html`
**功能**: 查看課程全部留言
**特色**:
- 課程資訊頭部
- 統計卡片
- 留言列表
- 作者頭像和信息
- 編輯按鈕 (僅限作者)

### 5. main.html (修改)
**變更**:
- 添加「👤 修改個人資訊」按鈕
- 在修課表格添加「💬」留言快速連結

### 6. course_detail.html (修改)
**變更**:
- 添加「💬 查看課程留言」按鈕

---

## ⚙️ 配置更新 (Settings)

### 文件: `scoresystem/settings.py`

**新增配置**:
```python
# Media files (User uploads)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## 🌐 主 URL 配置更新 (Main URLs)

### 文件: `scoresystem/urls.py`

**變更**:
```python
from django.conf.urls.static import static

# 在 urlpatterns 末尾添加
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 📦 依賴包

### 新增包
```
Pillow>=9.0.0  (用於圖片處理)
```

**安裝命令**:
```powershell
pip install Pillow
```

---

## 💾 資料庫遷移

### 遷移檔案
**檔名**: `grades/migrations/0003_userprofile_avatar_comment.py`

**執行命令**:
```bash
python manage.py makemigrations
python manage.py migrate
```

**執行結果**:
```
Applying grades.0003_userprofile_avatar_comment... OK
```

---

## 📁 檔案樹狀結構

```
grades/
├── models.py                           (✏️ 修改)
│   ├── UserProfile.avatar 欄位
│   └── Comment 新模型
├── forms.py                            (✏️ 修改)
│   ├── UserProfileEditForm
│   └── CommentForm
├── views.py                            (✏️ 修改)
│   ├── edit_profile()
│   ├── add_comment()
│   ├── edit_comment()
│   └── course_comments()
├── urls.py                             (✏️ 修改)
│   ├── /edit_profile/
│   ├── /add_comment/<id>/
│   ├── /edit_comment/<id>/
│   └── /course_comments/<id>/
├── templates/
│   └── grades/
│       ├── edit_profile.html           (✨ 新增)
│       ├── add_comment.html            (✨ 新增)
│       ├── edit_comment.html           (✨ 新增)
│       ├── course_comments.html        (✨ 新增)
│       ├── main.html                   (✏️ 修改)
│       └── course_detail.html          (✏️ 修改)
├── migrations/
│   └── 0003_userprofile_avatar_comment.py (✨ 新增)

media/                                   (✨ 新增)
├── avatars/                            (✨ 新增)

scoresystem/
├── settings.py                         (✏️ 修改)
└── urls.py                             (✏️ 修改)
```

---

## 📊 變更統計

| 類型 | 數量 |
|-----|-----|
| 新增模型 | 1 |
| 模型修改 | 1 |
| 新增表單 | 2 |
| 新增視圖 | 4 |
| 新增模板 | 4 |
| 修改模板 | 2 |
| 新增 URL 路由 | 4 |
| 配置修改 | 2 |
| 新增遷移 | 1 |
| 新增依賴包 | 1 |

---

## ✅ 系統檢查

### Django 系統檢查
```
System check identified no issues (0 silenced).
```

### 資料庫遷移
```
Migrations for 'grades':
  grades\migrations\0003_userprofile_avatar_comment.py
    + Add field avatar to userprofile
    + Create model Comment
```

### 遷移應用
```
Operations to perform:
  Apply all migrations
Running migrations:
  Applying grades.0003_userprofile_avatar_comment... OK
```

---

## 🧪 測試驗證

### 環境準備
```powershell
✅ Python 3.13.7
✅ Django 5.2.7
✅ Pillow 已安裝
✅ 資料庫已遷移
✅ 伺服器已啟動 (http://127.0.0.1:8000/)
```

### 功能測試清單
- [ ] 修改個人資訊 (名字、姓氏、頭像)
- [ ] 上傳個人頭像
- [ ] 新增課程留言
- [ ] 編輯自己的留言
- [ ] 查看課程全部留言
- [ ] 權限驗證 (未登入、未選課、非作者)
- [ ] 響應式設計測試

---

## 📝 文檔生成

### 新增文檔
1. ✅ `STUDENT_FEATURES_COMPLETE.md` - 完整功能說明 (500+ 行)
2. ✅ `QUICK_START_GUIDE.md` - 快速開始指南 (250+ 行)
3. ✅ `TECHNICAL_SUMMARY.md` - 技術實現總結 (400+ 行)

---

## 🎯 完成狀態

✅ **模型層**: 完成 (Comment 模型、UserProfile 更新)
✅ **表單層**: 完成 (UserProfileEditForm、CommentForm)
✅ **視圖層**: 完成 (4 個視圖函數)
✅ **模板層**: 完成 (4 新增 + 2 修改)
✅ **路由層**: 完成 (4 新路由)
✅ **配置層**: 完成 (媒體文件配置)
✅ **遷移層**: 完成 (資料庫已更新)
✅ **測試**: 準備好 (系統檢查 0 errors)
✅ **文檔**: 完成 (3 份詳細文檔)

---

## 🚀 部署建議

### 生產環境配置
1. 將 `DEBUG = False`
2. 配置白名單 `ALLOWED_HOSTS = ['your-domain.com']`
3. 使用生產級 WSGI 服務器 (Gunicorn, uWSGI)
4. 配置靜態文件服務 (WhiteNoise, CDN)
5. 配置媒體文件服務 (S3, 雲存儲)

### 備份建議
1. 定期備份 `db.sqlite3` 資料庫
2. 定期備份 `media/` 目錄
3. 版本控制所有代碼變更

---

## 📞 支持信息

### 常見問題
- Q: 為什麼看不到頭像? A: 確認 `media/avatars/` 目錄存在且圖片格式支援
- Q: 能否刪除留言? A: 目前只支援編輯，可清空內容實現刪除效果
- Q: 字數限制? A: 最多 1000 字元

### 聯絡方式
如有問題或建議，請提交 Issue 或 Pull Request

---

## 🎉 完成確認

所有學生帳號功能已成功實現並通過系統檢查。

系統狀態: ✅ 正常運行
伺服器地址: http://127.0.0.1:8000/
系統檢查: 0 errors, 0 warnings
資料庫狀態: 已遷移

開發者可以開始進行全面的功能測試。
