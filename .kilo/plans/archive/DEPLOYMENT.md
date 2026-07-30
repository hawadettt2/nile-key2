# Nile Key — دليل النشر

## المتطلبات
- Python 3.11+
- Node.js 18+
- Docker / Docker Compose (موصى به للإنتاج)

---

## خيار 1: Docker Compose (موصى به)

### الإعداد
1. أنشئ ملف `.env` في جذر المشروع.
2. تأكد من bahwa جميع المتغيرات المطلوبة معرفة في `.env.example`.
3. في الإنتاج، استبدل القيم بمتغيرات سرية حقيقية ولا ترفع ملف `.env` إلى المستودع.

```bash
# بناء وتشغيل الخدمات
docker compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Backend Health: `http://localhost:8000/health`
- API Docs: `http://localhost:8000/docs`

### التحقق من الصحة
```bash
# التحقق من أن الخدمات تعمل
curl http://localhost:8000/health
curl http://localhost:3000

# عرض السجلات
docker compose logs -f
```

### استكشاف الأخطاء
```bash
# إعادة بناء الصور بدون ذاكرة تخزين مؤقتة
docker compose build --no-cache

# إيقاف وإزالة الحاويات
docker compose down

# إيقاف مع إزالة البيانات (يحذف قاعدة البيانات)
docker compose down -v
```

---

## خيار 2: تشغيل محلي بدون Docker

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## متغيرات البيئة

| المتغير | الوصف | مطلوب |
|---------|-------|--------|
| `SECRET_KEY` | مفتاح توقيع JWT — 32+ حرف | ✅ |
| `DATABASE_URL` | رابط قاعدة البيانات | ❌ |
| `ALLOWED_ORIGINS` | قائمة بأصول CORS المسموحة (مفصولة بفواصل) | ✅ |
| `DEBUG` | وضع التصحيح | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | مدة صلاحية رمز الوصول | ❌ |
| `REFRESH_TOKEN_EXPIRE_DAYS` | مدة صلاحية رمز التحديث | ❌ |
| `COOKIE_SECURE` | ملفات تعريف الارتباط الآمنة | ❌ |
| `COOKIE_SAMESITE` | سياسة SameSite | ❌ |
| `COOKIE_DOMAIN` | نطاق ملفات تعريف الارتباط | ❌ |
| `SMTP_HOST` | خادم SMTP | ❌ |
| `SMTP_PORT` | منفذ SMTP | ❌ |
| `SMTP_USER` | مستخدم SMTP | ❌ |
| `SMTP_PASSWORD` | كلمة مرور SMTP | ❌ |
| `SMTP_FROM` | عنوان البريد الإلكتروني للمرسل | ❌ |
| `SMTP_USE_TLS` | استخدام TLS | ❌ |
| `LETME_API_ID` | معرّف LetMeShip API | ❌ |
| `LETME_API_PASSWORD` | كلمة مرور LetMeShip API | ❌ |
| `SENDCLOUD_PUBLIC_KEY` | المفتاح العام لـ SendCloud | ❌ |
| `SENDCLOUD_SECRET_KEY` | المفتاح السري لـ SendCloud | ❌ |
| `ETA_CLIENT_ID` | معرّف عميل ETA | ❌ |
| `ETA_CLIENT_SECRET` | سر عميل ETA | ❌ |
| `ETA_BASE_URL` | عنوان URL الأساسي لـ ETA | ❌ |
| `VITE_API_URL` | عنوان Backend للواجهة الأمامية المبنية | ❌ |

---

## بنية Docker

### الخدمات
| الخدمة | الصورة | المنفذ | الوصف |
|--------|--------|--------|-------|
| Backend | مبنية من `backend/Dockerfile` | 8000 | FastAPI backend |
| Frontend | مبنية من `frontend/Dockerfile` | 3000 | Nginx serving built frontend |

### الأحجام
| الحجم | الوصف |
|-------|-------|
| `db-data` | تخزين قاعدة بيانات SQLite (`/app/data/nile_key.db`) |

### فحص الصحة
| الخدمة | الفحص | الفاصل الزمني |
|--------|-------|---------------|
| Backend | `python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"` | 30 ثانية |
| Frontend | `pid=$(cat /var/run/nginx.pid 2>/dev/null); [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null || exit 1` | 30 ثانية |

---

## نقاط نهاية API

| الخدمة | المسار |
|--------|--------|
| الصحة | `/health` |
| الجذر | `/` |
| توثيق | `/docs`, `/redoc` |
| OpenAPI | `/openapi.json` |
| المصادقة | `/api/v1/auth/*` |
| الموردين | `/api/v1/suppliers/*` |
| العملاء | `/api/v1/customers/*` |
| الشحنات | `/api/v1/shipping/*` |
| الفواتير | `/api/v1/invoices/*` |
| الجمارك | `/api/v1/customs/*` |
| الوثائق | `/api/v1/documents/*` |
| الموارد | `/api/v1/resources/*` |
| ETA | `/api/v1/eta/*` |
| الإشعارات | `/api/v1/notifications/*` |
| التدقيق | `/api/v1/audit/logs` |
| سير العمل | `/api/v1/export-workflows` |
| الوكيل | `/api/v1/agent/*` |
| مدير التصدير الرقمي | `/api/v1/digital-export-manager/*` |
| الرسم المعرفي | `/api/v1/knowledge-graph/*` |
| ذكاء السوق | `/api/v1/trade-intelligence/*` |

---

## ملاحظات
- قاعدة البيانات الافتراضية: `sqlite:///./nile_key.db`
- في Docker، يتم تخزين SQLite في `/app/data/nile_key.db` داخل الحاوية
- حجم `db-data` يضمن persistency البيانات عبر إعادة تشغيل الحاويات
- في الإنتاج، تجنب استخدام أصول CORS wildcard وتأكد من HTTPS
- مفتاح `SECRET_KEY` يجب أن يكون 32+ حرفاً ولا يستخدم القيمة الافتراضية
- `ALLOWED_ORIGINS` يجب أن يحتوي على أصول محددة، لا `*`

---

## استكشاف الأخطاء وإصلاحها

### Backend لا يبدأ
1. تحقق من أن `SECRET_KEY` معرف وله 32+ حرف
2. تحقق من ملاءمة `ALLOWED_ORIGINS` (لا `*`)
3. تحقق من سجلات Docker: `docker compose logs backend`

### Frontend لا يبني
1. احذف `node_modules` وأعد التثبيت: `rm -rf node_modules && npm install`
2. تحقق من أن Node.js 18+ مثبت: `node --version`
3. تحقق من سجلات Docker: `docker compose logs frontend`

### قاعدة البيانات
1. في Docker: احذف الحجم `docker compose down -v` ثم `docker compose up --build`
2. محلياً: احذف `nile_key.db` وأعد تشغيل `uvicorn` لتشغيل `init_db()`

---

**تم التحديث:** 2026-07-21 | **الإصدار:** 1.1.0-MVP
