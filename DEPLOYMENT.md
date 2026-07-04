# Nile Key — دليل النشر

## المتطلبات
- Python 3.9+
- Node.js 18+
- Docker / Docker Compose (اختياري)

## خيار 1: Docker Compose

```bash
docker compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

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
