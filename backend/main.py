"""
Nile Key API v1.0
منصة مفتاح النيل الرقمية
FastAPI Backend — Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.routers import auth, shipping, invoice, suppliers, customers, customs, resources, documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    إدارة دورة حياة التطبيق:
    - Startup: تهيئة قاعدة البيانات
    - Shutdown: تنظيف الموارد (إن وجد)
    """
    # ========== STARTUP ==========
    print("[STARTUP] Starting Nile Key API...")
    init_db()
    print("[SUCCESS] Database initialized")
    yield
    # ========== SHUTDOWN ==========
    print("[SHUTDOWN] Shutting down Nile Key API...")


# إنشاء تطبيق FastAPI
app = FastAPI(
    title="Nile Key API",
    description="منصة مفتاح النيل الرقمية — بوابة استراتيجية للصادرات المصرية",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# إعداد CORS — يُعدل في الإنتاج ليكون أكثر تحديداً
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # TODO: حدد في الإنتاج: ["https://nile-key.com", "https://www.nile-key.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== تسجيل الـ Routers ==========
app.include_router(auth.router)
app.include_router(shipping.router)
app.include_router(invoice.router)
app.include_router(suppliers.router)
app.include_router(customers.router)
app.include_router(customs.router)
app.include_router(resources.router)
app.include_router(documents.router)


@app.get("/", tags=["Root"])
def root():
    """الصفحة الرئيسية — معلومات التطبيق"""
    return {
        "message": "Nile Key API v1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """فحص صحة التطبيق — يُستخدم في Monitoring"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }
