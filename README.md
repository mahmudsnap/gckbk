# 🎬 SnapYTube Ultimate v4.0

> منصة تحميل فيديو متكاملة تعمل على **Termux** | يدعم YouTube حتى 4K + 6 منصات أخرى

<div align="center">

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3+-green?logo=flask)
![yt-dlp](https://img.shields.io/badge/yt--dlp-Latest-red)
![Platform](https://img.shields.io/badge/Platform-Termux%20%7C%20Linux-orange)
![License](https://img.shields.io/badge/License-MIT-purple)

</div>

---

## 📱 المنصات المدعومة

| المنصة | الجودة |
|--------|--------|
| 🔴 YouTube | حتى 4K (2160p) |
| ⚫ TikTok | أفضل جودة |
| 🟣 Instagram | أفضل جودة |
| 🔵 Facebook | أفضل جودة |
| 🐦 Twitter / X | أفضل جودة |
| 🎬 Vimeo | أفضل جودة |
| ✂️ CapCut | أفضل جودة |

---

## 🚀 التثبيت من الصفر (Termux)

### الخطوة الوحيدة:

```bash
pkg install git -y && git clone https://github.com/YOUR_USERNAME/snapytube-ultimate && cd snapytube-ultimate && bash setup.sh
```

> **استبدل** `YOUR_USERNAME` باسم مستخدمك على GitHub

---

## ▶️ تشغيل السيرفر (بعد الإعداد)

```bash
bash start.sh
```

بعد التشغيل:
- افتح المتصفح على **`http://localhost:5001`**
- أو امسح **QR Code** من هاتف آخر على نفس الشبكة

---

## 📂 هيكل الملفات

```
snapytube-ultimate/
│
├── 📄 run.py           ← السيرفر الرئيسي (Flask)
├── 📄 config.py        ← الإعدادات والمتغيرات
├── 📄 downloader.py    ← محرك التحميل (yt-dlp)
├── 📄 index.html       ← واجهة المستخدم
├── 📄 requirements.txt ← مكتبات Python
│
├── 🟢 setup.sh         ← ثبّت كل شي (مرة واحدة)
├── 🟢 start.sh         ← شغّل السيرفر
│
└── 📁 users/           ← ملفات المستخدمين (تُنشأ تلقائياً)
    └── device_<IP>/
        ├── downloads/  ← الفيديوهات المحملة
        └── logs/       ← سجل التحميلات
```

---

## 🔌 API Endpoints

| Method | Endpoint | الوصف |
|--------|----------|-------|
| `GET` | `/` | الصفحة الرئيسية |
| `POST` | `/api/download` | تحميل فيديو |
| `POST` | `/api/download/progress` | تحميل مع شريط تقدم (SSE) |
| `GET` | `/api/videos` | قائمة الفيديوهات |
| `GET` | `/api/video/<filename>` | تحميل ملف |
| `GET` | `/api/stats` | إحصائيات |
| `GET` | `/api/health` | فحص السيرفر |

### مثال استخدام API:

```bash
curl -X POST http://localhost:5001/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=..."}'
```

---

## ⚙️ الإعدادات

كل الإعدادات في `config.py`:

```python
PORT = 5001              # منفذ السيرفر
MAX_FILE_SIZE_MB = 8000  # أقصى حجم (8 GB)
MAX_CONCURRENT_DOWNLOADS = 2  # تحميلات متزامنة
DOWNLOAD_TIMEOUT = 900   # مهلة الانتظار (ثانية)
```

---

## 🔧 متطلبات النظام

| الحزمة | الاستخدام |
|--------|-----------|
| `python` | تشغيل السيرفر |
| `ffmpeg` | دمج الفيديو والصوت |
| `git` | تحميل المشروع |

---

## 💡 نصائح

- **المنفذ محجوز؟** غيّر `PORT` في `config.py`
- **خطأ ffmpeg؟** شغّل `pkg install ffmpeg`
- **yt-dlp قديم؟** `start.sh` يحدّثه تلقائياً عند كل تشغيل
- **كل مستخدم** على الشبكة له مجلد منفصل حسب IP
- **الفيديوهات** تُحفظ في `users/device_<IP>/downloads/`

---

## 📝 رخصة

MIT License — استخدم حسب مسؤوليتك.

---

<div align="center">
بُني بـ ❤️ للاستخدام على Termux
</div>
