# 學生帳號功能完整說明書

## 🎯 新增功能總覽

在學生帳號中成功實裝了三個核心功能：

### 1. 📝 修改個人資訊 (姓名、個人頭像)
- **位置**: 學生首頁 (`/main/`) 的「修改個人資訊」按鈕
- **功能**: 修改學生的名字、姓氏以及上傳個人頭像
- **URL**: `/edit_profile/`

### 2. 💬 對課程留言 (可修改自己的留言)
- **位置**: 課程詳情頁面或留言頁面
- **功能**: 在已選課程中發表留言，並可以編輯自己的留言
- **URL**: `/add_comment/<course_id>/` 和 `/edit_comment/<comment_id>/`

### 3. 👁️ 查看全部留言
- **位置**: 每個課程都有「查看課程留言」按鈕
- **功能**: 查看該課程所有學生發表的留言，以及留言的時間和作者
- **URL**: `/course_comments/<course_id>/`

---

## 🏗️ 技術架構

### 新增模型 (Models)

#### 1. Comment 模型
```python
class Comment(models.Model):
    student = ForeignKey(User)           # 留言者
    course = ForeignKey(Course)          # 課程
    content = TextField()                 # 留言內容
    created_at = DateTimeField()         # 建立時間
    updated_at = DateTimeField()         # 修改時間
    
    # 獨特條件: 每個學生對每個課程只能有一個留言
    unique_together = ('student', 'course')
    
    # 按最新留言優先排序
    ordering = ['-created_at']
```

#### 2. UserProfile 模型更新
```python
# 新增字段
avatar = ImageField(upload_to='avatars/')  # 頭像圖片欄位
```

### 新增表單 (Forms)

#### 1. UserProfileEditForm
- 編輯使用者名字和姓氏
- 上傳頭像圖片
- 驗證圖片格式和大小

#### 2. CommentForm
- 輸入留言內容
- 字數限制: 1000 字元
- 支持 Markdown 文本換行

### 新增視圖 (Views)

#### 1. edit_profile(request)
- **方法**: GET/POST
- **權限**: @login_required (需登入)
- **功能**: 
  - GET: 顯示修改表單，預填現有資訊
  - POST: 保存修改並重定向回首頁

#### 2. add_comment(request, course_id)
- **方法**: GET/POST
- **權限**: @login_required (需登入)
- **驗證**: 確認學生已選課
- **功能**:
  - 新增留言
  - 自動偵測是否為編輯 (如已存在則視為編輯模式)

#### 3. edit_comment(request, comment_id)
- **方法**: GET/POST
- **權限**: @login_required + 只有作者可編輯
- **功能**: 編輯自己的留言內容

#### 4. course_comments(request, course_id)
- **方法**: GET
- **權限**: 所有使用者可訪問
- **功能**:
  - 顯示課程的所有留言
  - 標示目前使用者的留言
  - 提供編輯按鈕 (僅限作者)

---

## 🎨 新增/修改的模板

### 1. edit_profile.html
**路徑**: `grades/templates/grades/edit_profile.html`

**主要功能**:
- 圓形頭像預覽 (有預設頭像則顯示，無則顯示預設圖示)
- 名字和姓氏輸入欄位
- 拖拽上傳或點擊選擇頭像
- 檔案名顯示確認
- 保存/取消按鈕

**設計特點**:
- 響應式設計
- 梯度背景色
- 文件選擇確認提示
- 實時文件名顯示

### 2. add_comment.html
**路徑**: `grades/templates/grades/add_comment.html`

**主要功能**:
- 課程名稱顯示
- 多行文本區域輸入留言
- 實時字數統計 (最多 1000 字)
- 提示訊息說明禮儀

**設計特點**:
- 實時字數計算
- 文本框焦點效果
- 課程綁定確認
- 多個導航按鈕

### 3. edit_comment.html
**路徑**: `grades/templates/grades/edit_comment.html`

**主要功能**:
- 顯示原始留言時間
- 顯示編輯時間
- 編輯留言內容
- 字數統計

**設計特點**:
- 編輯時間追蹤
- 黃色警告框提示
- 相同的編輯界面

### 4. course_comments.html
**路徑**: `grades/templates/grades/course_comments.html`

**主要功能**:
- 課程標題和資訊展示
- 留言統計 (留言數)
- 新增/編輯留言快速入口
- 所有留言列表展示
- 留言作者信息 (頭像、名字、時間)
- 編輯按鈕 (僅限作者)

**設計特點**:
- 漸變背景課程頭部
- 統計卡片網格佈局
- 左邊框色區分自己的留言
- 頭像圓形展示
- 時間戳記 (若編輯過則顯示編輯時間)
- 無留言時顯示友好提示

### 5. main.html (修改)
**修改**:
- 添加「修改個人資訊」按鈕
- 在修課列表中添加留言快速連結 (💬 按鈕)

### 6. course_detail.html (修改)
**修改**:
- 在課程標題下添加「查看課程留言」按鈕

---

## 📊 資料庫更新

### 遷移檔案
**檔名**: `0003_userprofile_avatar_comment.py`

**變更**:
1. 為 UserProfile 添加 avatar 欄位
2. 建立新的 Comment 模型

### 字段說明

#### Comment 表
| 字段 | 類型 | 說明 |
|-----|------|------|
| id | BigAutoField | 主鍵 |
| student_id | ForeignKey | 學生 ID |
| course_id | ForeignKey | 課程 ID |
| content | TextField | 留言內容 |
| created_at | DateTimeField | 建立時間 |
| updated_at | DateTimeField | 更新時間 |

#### UserProfile 表新增字段
| 字段 | 類型 | 說明 |
|-----|------|------|
| avatar | ImageField | 個人頭像 |

---

## 🔐 權限控制

### 修改個人資訊
- ✅ 只有自己能修改自己的個人資訊
- ✅ 需要登入
- ✅ 自動綁定到 `request.user`

### 留言功能
| 操作 | 學生已選課 | 權限 |
|-----|---------|------|
| 查看留言 | 不限制 | 所有人都可看 |
| 新增留言 | 必須 | 已選課學生 |
| 編輯自己的留言 | 必須 | 僅限作者 |
| 編輯別人的留言 | - | 🚫 被拒絕 (403 Forbidden) |

---

## 🔄 流程圖

### 修改個人資訊流程
```
點擊「修改個人資訊」
    ↓
填寫名字、姓氏、選擇頭像
    ↓
點擊「保存修改」
    ↓
驗證表單
    ↓
保存到資料庫
    ↓
重定向回首頁
    ↓
新的個人資訊已生效 ✅
```

### 留言流程
```
點擊「查看課程留言」
    ↓
查看所有課程留言
    ↓
已選課? 
    ├─ 是 → 顯示「新增留言」按鈕
    └─ 否 → 提示需要選課
    ↓
點擊「新增留言」
    ↓
填寫留言內容
    ↓
點擊「發表留言」
    ↓
驗證:
    ├─ 學生已選課? ✓
    └─ 內容長度? ✓
    ↓
保存到 Comment 表
    ↓
返回留言列表頁面
    ↓
在列表中看到自己的留言 ✅
```

---

## 🧪 測試指南

### 環境準備
```powershell
cd c:\Users\user\Downloads\team_04-main\team_04-main
python manage.py runserver 127.0.0.1:8000
```

訪問 `http://127.0.0.1:8000/`

### 測試帳號
```
帳號: student1
密碼: student123

帳號: student2
密碼: student123
```

### 測試場景 1: 修改個人資訊

**步驟**:
1. 使用 `student1` 登入
2. 進入首頁 (`/main/`)
3. 點擊「👤 修改個人資訊」按鈕
4. 輸入名字: "王"，姓氏: "小明"
5. 上傳一個圖片作為頭像
6. 點擊「✅ 保存修改」

**預期結果**:
- ✅ 表單驗證成功
- ✅ 重定向回首頁
- ✅ 首頁顯示新的個人名字
- ✅ 頭像顯示在相關位置

### 測試場景 2: 新增課程留言

**前置條件**:
- 已登入 `student1`
- `student1` 已選修至少一個課程

**步驟**:
1. 在首頁查看修課列表
2. 選擇一個課程，點擊 「💬」 按鈕
3. 點擊「💬 新增留言」或「✏️ 編輯我的留言」
4. 輸入留言: "這堂課很有趣，講師講解清楚！"
5. 點擊「✅ 發表留言」

**預期結果**:
- ✅ 留言成功保存
- ✅ 返回留言列表
- ✅ 能看到自己的留言
- ✅ 留言旁有「✏️」編輯按鈕

### 測試場景 3: 編輯自己的留言

**前置條件**:
- 已發表一個留言

**步驟**:
1. 在留言列表頁面
2. 點擊自己留言旁的「✏️」按鈕
3. 修改內容: "非常棒的課程！"
4. 點擊「✅ 更新留言」

**預期結果**:
- ✅ 留言內容已更新
- ✅ "編輯於" 時間戳已更新
- ✅ 返回留言列表
- ✅ 修改成功反映在列表中

### 測試場景 4: 查看所有留言

**步驟**:
1. 訪問任何課程的留言頁面
2. 查看所有學生發表的留言

**預期結果**:
- ✅ 顯示課程資訊
- ✅ 統計留言數量
- ✅ 列出所有留言
- ✅ 顯示每個留言的作者、頭像、時間
- ✅ 自己的留言有藍色左邊框標示
- ✅ 自己的留言有「✏️」編輯按鈕

### 測試場景 5: 權限驗證

**測試編輯別人的留言**:
1. 以 `student1` 登入
2. 發表一個留言
3. 登出並以 `student2` 登入
4. 嘗試直接訪問編輯 URL: `/edit_comment/1/`

**預期結果**:
- ✅ 顯示 403 Forbidden 錯誤
- ✅ 提示訊息: "你沒有權限編輯此留言"

**測試未選課發表留言**:
1. 以 `student1` 登入
2. 訪問未選修課程的留言頁面
3. 嘗試新增留言

**預期結果**:
- ✅ 無法點擊「新增留言」
- ✅ 顯示提示訊息: "請先選課才能留言"

---

## 📁 檔案清單

### 新增檔案
```
grades/templates/grades/edit_profile.html        # 修改個人資訊
grades/templates/grades/add_comment.html         # 新增留言
grades/templates/grades/edit_comment.html        # 編輯留言
grades/templates/grades/course_comments.html     # 查看所有留言
media/avatars/                                   # 頭像儲存目錄
```

### 修改檔案
```
grades/models.py                                 # 添加 Comment 模型、avatar 欄位
grades/views.py                                  # 添加 4 個新視圖
grades/forms.py                                  # 添加 2 個新表單
grades/urls.py                                   # 添加 4 個新 URL 路由
grades/templates/grades/main.html                # 添加按鈕和留言連結
grades/templates/grades/course_detail.html       # 添加留言按鈕
scoresystem/settings.py                          # 媒體文件配置
scoresystem/urls.py                              # 媒體服務配置
```

### 資料庫遷移
```
grades/migrations/0003_userprofile_avatar_comment.py
```

---

## 🚀 URL 路由表

| 路由 | 名稱 | 方法 | 說明 |
|-----|------|------|------|
| `/edit_profile/` | `edit_profile` | GET/POST | 修改個人資訊 |
| `/add_comment/<id>/` | `add_comment` | GET/POST | 新增課程留言 |
| `/edit_comment/<id>/` | `edit_comment` | GET/POST | 編輯自己的留言 |
| `/course_comments/<id>/` | `course_comments` | GET | 查看課程留言 |

---

## 💾 資料存儲

### 頭像存儲
- **目錄**: `media/avatars/`
- **格式**: JPG, PNG, GIF, WebP
- **訪問**: `http://127.0.0.1:8000/media/avatars/<filename>`

### 留言存儲
- **表**: `grades_comment`
- **字段**: student_id, course_id, content, created_at, updated_at

---

## 🔧 配置說明

### settings.py
```python
# 媒體文件配置
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### urls.py
```python
# 開發環境媒體文件服務
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 📝 常見問題

### Q: 上傳頭像後看不到圖片?
A: 
- 確認 `media/avatars/` 目錄已建立
- 確認伺服器正在執行
- 清除瀏覽器緩存
- 檢查圖片格式是否支援

### Q: 能否刪除留言?
A: 
目前版本支援編輯但不支援刪除。可通過編輯為空來實現類似效果。

### Q: 同一課程能發表多個留言嗎?
A:
不能。資料庫設定了 unique_together 限制，每個學生對每個課程只能有一個留言。如要修改，請編輯現有留言。

### Q: 留言有字數限制嗎?
A:
是的，最多 1000 字元。前端會實時統計，超過時會自動截斷。

---

## ✨ 功能亮點

1. **完整的頭像管理**
   - 上傳、預覽、替換
   - 預設頭像圖示
   - 響應式展示

2. **智能留言系統**
   - 自動偵測新增/編輯
   - 編輯時間追蹤
   - 字數實時統計
   - 權限自動驗證

3. **優秀的使用者體驗**
   - 梯度背景設計
   - 流暢的動畫效果
   - 清晰的視覺層級
   - 友好的提示訊息

4. **安全的資料保護**
   - 登入驗證
   - 權限檢查
   - 資料庫完整性約束
   - CSRF 保護

---

## 🎉 完成標記

✅ 模型設計完成
✅ 表單實現完成
✅ 視圖邏輯完成
✅ 模板設計完成
✅ URL 路由完成
✅ 權限控制完成
✅ 文件上傳配置完成
✅ 資料庫遷移完成
✅ 系統檢查通過 (0 errors)
✅ 伺服器成功啟動

所有功能已完整實裝並準備好進行全面測試！
