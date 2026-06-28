# Nile Key — دليل النشر

## المتطلبات
- Python 3.9+
- Node.js 18+

## Backend (PythonAnywhere Free)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Frontend (GitHub Pages)
```bash
cd frontend
npm install
npm run build
# ارفع مجلد dist على gh-pages
```

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
