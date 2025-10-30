# 🎓 學生修課分數計算系統

一個基於 Django 開發的現代化成績管理系統，具有精美的漸層 UI 設計與完整的課程管理功能。

## ✨ 功能特色

### 核心功能
- 📊 **成績管理**：查看期中、期末成績與自動計算平均分數
- 📚 **課程管理**：新增、查看課程資訊（課名、課號、任課老師）
- 📝 **選課系統**：學生可加選或退選課程
- 👥 **多使用者支援**：使用 Django User 系統，支援登入/登出

### 介面特色
- 🎨 **現代化設計**：紫色漸層主題，專業卡片式佈局
- 📱 **響應式設計**：支援手機、平板、電腦多種螢幕尺寸
- ⚡ **流暢動畫**：按鈕懸停、表格互動等細膩效果
- 🔍 **直觀操作**：清晰的導航與操作提示

## 🚀 快速開始

### 環境需求
- Python 3.8+
- Django 5.2.7

### 安裝步驟

1. **Clone 專案**
```bash
git clone https://github.com/11256004-blip/team_04.git
cd team_04
```

2. **建立虛擬環境**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
# 或
source .venv/bin/activate    # macOS/Linux
```

3. **安裝依賴**
```bash
pip install django
```

4. **執行資料庫遷移**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **建立測試資料**
```bash
python populate_initial.py
```
這會建立：
- 使用者：`student1` (密碼: `password`)
- 三門課程：程式設計、微積分、英文
- 選課紀錄與成績

6. **啟動開發伺服器**
```bash
python manage.py runserver
```

7. **開啟瀏覽器**
訪問 http://127.0.0.1:8000/

## 📖 使用說明

### 測試帳號
- **帳號**: `student1` 或 `team04`
- **密碼**: `password`

### 主要頁面
- **首頁**: `/` - 系統介紹
- **功能主頁**: `/main/` - 查看所有課程與成績
- **課程詳細**: `/course/<id>/` - 查看特定課程資訊
- **新增課程**: `/add_course/` - 新增新課程
- **加選課程**: `/enroll/` - 加選課程（需登入）
- **登入**: `/accounts/login/` - 使用者登入

### 為新使用者建立選課紀錄
如果你建立了新的使用者（例如 `team04`），可以執行：
```bash
python manage.py shell -c "from django.contrib.auth import get_user_model; from grades.models import Course, Enrollment; User=get_user_model(); user=User.objects.get(username='team04'); c1=Course.objects.get(code='CS101'); c2=Course.objects.get(code='MATH101'); c3=Course.objects.get(code='ENG101'); Enrollment.objects.get_or_create(student=user, course=c1, defaults={'midterm_score':85,'final_score':90}); Enrollment.objects.get_or_create(student=user, course=c2, defaults={'midterm_score':78,'final_score':82}); Enrollment.objects.get_or_create(student=user, course=c3, defaults={'midterm_score':92,'final_score':88}); print('完成！')"
```

## 🗂️ 專案結構

```
scoresystem/
├── manage.py                    # Django 管理指令
├── populate_initial.py          # 初始資料建立腳本
├── add_team04_enrollments.py    # team04 選課建立腳本
├── scoresystem/                 # 專案設定
│   ├── settings.py             # Django 設定
│   └── urls.py                 # 主路由
└── grades/                      # 成績管理 app
    ├── models.py               # 資料模型（Course, Enrollment）
    ├── views.py                # 視圖函數
    ├── urls.py                 # app 路由
    ├── forms.py                # 表單
    ├── admin.py                # 管理後台
    └── templates/grades/       # 模板
        ├── base.html           # 基礎模板
        ├── main.html           # 功能主頁
        ├── course_detail.html  # 課程詳細
        ├── add_course.html     # 新增課程
        ├── enroll.html         # 加選課程
        └── registration/
            └── login.html      # 登入頁面
```

## 🎨 設計特色

### 配色方案
- **主色調**: 紫藍漸層 (#667eea → #764ba2)
- **次要色**: 粉紫漸層 (#f093fb → #f5576c)
- **警告色**: 粉橘漸層 (#fa709a → #fee140)

### 資料模型

**Course (課程)**
- `name`: 課程名稱
- `code`: 課程代碼（唯一）
- `teacher`: 任課老師

**Enrollment (選課紀錄)**
- `student`: 學生（Django User）
- `course`: 課程
- `midterm_score`: 期中成績
- `final_score`: 期末成績
- `average()`: 自動計算平均分數

## 🛠️ 技術棧

- **後端框架**: Django 5.2.7
- **資料庫**: SQLite3
- **前端**: Django Templates + Custom CSS
- **認證系統**: Django Authentication

## 📝 TODO / 未來功能

- [ ] 新增圖表顯示成績趨勢
- [ ] 匯出成績為 Excel/PDF
- [ ] 搜尋/篩選功能
- [ ] 深色模式
- [ ] 成績排名系統
- [ ] 通知系統

## 👥 開發團隊

Team 04

## 📄 授權

此專案為教育用途開發。

## 🙏 致謝

感謝 Django 框架與開源社群的支持。

---

**🎓 讓成績管理變得簡單又美觀！**
