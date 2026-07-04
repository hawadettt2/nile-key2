# Nile Key — دليل النشر

## المتطلبات
- Python 3.9+
- Node.js 18+
- Docker / Docker Compose (اختياري)

## خيار 1: Docker Compose

### الإعداد المحلي
1. أنشئ ملف `.env` في جذر المشروع أو استخدم الملف الموجود مسبقاً.
2. للحصول على إعدادات افتراضية مناسبة للتطوير المحلي، يمكن استخدام القيم المرفقة.
3. في الإنتاج، استبدل القيم بمتغيرات سرية حقيقية ولا ترفع ملف `.env` إلى المستودع.

```bash
# تشغيل الخدمة
docker compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Health check: `/health` endpoint for backend, nginx root for frontend

### متغيرات البيئة
| المتغير | الوصف |
|---------|-------|
| `SECRET_KEY` | مفتاح توقيع JWT — يجب تغييره في الإنتاج |
| `ALLOWED_ORIGINS` | قائمة بأصول CORS المسموحة |
| `DATABASE_URL` | رابط قاعدة البيانات |
| `VITE_API_URL` | عنوان Backend الذي ستستخدمه واجهة المستخدم المبنية |

## خيار 2: PythonAnywhere / تشغيل محلي بدون Docker

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run build
# لرفع المجلد على gh-pages
```

## ملاحظات
- متغير `SECRET_KEY` مطلوب في البيئة
- CORS يقرأ من `ALLOWED_ORIGINS` في إعدادات Backend
- قاعدة البيانات الافتراضية: `sqlite:///./nile_key.db`
- في Docker، يخزن SQLite البيانات في `/app/data/nile_key.db` داخل الحاوية
- في الإنتاج، تجنب استخدام قيم CORS wildcard وتأكد من تشغيل الخدمة خلف HTTPS

## API Endpoints
| الخدمة | المسار |
|--------|--------|
| Auth | `/api/v1/auth/*` |
| Suppliers | `/api/v1/suppliers/*` |
| Customers | `/api/v1/customers/*` |
| Shipments | `/api/v1/shipping/*` |
| Invoices | `/api/v1/invoices/*` |
| Customs | `/api/v1/customs/*` |
| Documents | `/api/v1/documents/*` |
| Resources | `/api/v1/resources/*` |
