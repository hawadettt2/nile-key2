"""
Digital Export Manager API v1.0
Digital Export Manager — Intelligent Operating Platform for export operations
FastAPI Backend — Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import init_db
from app.core.csrf import CSRFMiddleware
from app.core.eta_scheduler import init_scheduler, start_scheduler, shutdown_scheduler
from app.core.shipping_scheduler import init_scheduler as init_shipping_scheduler, start_scheduler as start_shipping_scheduler, shutdown_scheduler as shutdown_shipping_scheduler
from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.knowledge.graph_provider import KnowledgeGraphProvider
from app.agent.knowledge.company_knowledge_provider import CompanyKnowledgeProvider
from app.agent.memory.sqlite_provider import SQLiteMemoryProvider
from app.agent.llm.provider import GeminiProvider, llm_registry
from app.services.trade_intelligence import set_memory_provider, set_knowledge_registry
from app.routers import auth, shipping, invoice, suppliers, customers, customs, resources, documents, eta, notifications, audit, workflow, digital_export_manager_router, knowledge_graph, trade_intelligence, dashboard, search, users_router, roles_router, research

knowledge_provider_registry = KnowledgeProviderRegistry()
memory_provider = SQLiteMemoryProvider(db_path="nile_key.db")


class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", [])
                message["headers"].extend([
                    (b"x-frame-options", b"DENY"),
                    (b"x-content-type-options", b"nosniff"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                ])
            await send(message)

        await self.app(scope, receive, send_with_headers)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    إدارة دورة حياة التطبيق:
    - Startup: تهيئة قاعدة البيانات + تشغيل ETA Scheduler
    - Shutdown: إيقاف ETA Scheduler + تنظيف الموارد
    """
    # ========== STARTUP ==========
    print("[STARTUP] Starting Digital Export Manager API...")
    init_db()
    print("[SUCCESS] Database initialized")

    # Register LLM provider
    try:
        if settings.LLM_API_KEY:
            llm_provider = GeminiProvider(
                api_key=settings.LLM_API_KEY,
                model=settings.LLM_MODEL,
            )
            await llm_registry.register(llm_provider)
            print(f"[SUCCESS] LLM provider registered: {settings.LLM_PROVIDER}")
        else:
            print("[WARNING] LLM_API_KEY is not configured. LLM provider not registered.")
    except Exception as exc:
        print(f"[WARNING] LLM provider registration failed: {exc}")
    
    # Register Knowledge providers
    try:
        graph_provider = KnowledgeGraphProvider()
        await knowledge_provider_registry.register(graph_provider)
        print("[SUCCESS] Knowledge Graph provider registered")
    except Exception as exc:
        print(f"[WARNING] Knowledge Graph provider registration failed: {exc}")

    try:
        company_knowledge_provider = CompanyKnowledgeProvider()
        await knowledge_provider_registry.register(company_knowledge_provider)
        print("[SUCCESS] Company Knowledge provider registered")
    except Exception as exc:
        print(f"[WARNING] Company Knowledge provider registration failed: {exc}")
    
    # Wire Memory and Knowledge providers for Trade Intelligence
    try:
        set_memory_provider(memory_provider)
        set_knowledge_registry(knowledge_provider_registry)
        print("[SUCCESS] Trade Intelligence providers wired")
    except Exception as exc:
        print(f"[WARNING] Trade Intelligence provider wiring failed: {exc}")
    
    # Initialize ETA background scheduler
    try:
        eta_scheduler = init_scheduler()
        start_scheduler()
        print("[SUCCESS] ETA scheduler started")
    except Exception as exc:
        print(f"[WARNING] ETA scheduler failed to start: {exc}")

    # Initialize Shipping background scheduler
    try:
        shipping_scheduler = init_shipping_scheduler()
        start_shipping_scheduler()
        print("[SUCCESS] Shipping scheduler started")
    except Exception as exc:
        print(f"[WARNING] Shipping scheduler failed to start: {exc}")
    
    yield
    # ========== SHUTDOWN ==========
    print("[SHUTDOWN] Shutting down Digital Export Manager API...")
    try:
        shutdown_scheduler()
        print("[SUCCESS] ETA scheduler stopped")
    except Exception as exc:
        print(f"[WARNING] ETA scheduler shutdown error: {exc}")
    try:
        shutdown_shipping_scheduler()
        print("[SUCCESS] Shipping scheduler stopped")
    except Exception as exc:
        print(f"[WARNING] Shipping scheduler shutdown error: {exc}")


# إنشاء تطبيق FastAPI
app = FastAPI(
    title="Digital Export Manager API",
    description="Digital Export Manager — Intelligent Operating Platform for export operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)
app.state.limiter = auth.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# إعداد CORS — يُعدل في الإنتاج ليكون أكثر تحديداً
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)

# ========== تسجيل الـ Routers ==========
app.include_router(auth.router)
app.include_router(shipping.router)
app.include_router(invoice.router)
app.include_router(suppliers.router)
app.include_router(customers.router)
app.include_router(customs.router)
app.include_router(resources.router)
app.include_router(documents.router)
app.include_router(eta.router)
app.include_router(notifications.router)
app.include_router(audit.router)
app.include_router(workflow.router)
app.include_router(digital_export_manager_router)
app.include_router(knowledge_graph.router)
app.include_router(trade_intelligence.router)
app.include_router(dashboard.router)
app.include_router(search.router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(research.router)


@app.get("/", tags=["Root"])
def root():
    """الصفحة الرئيسية — معلومات التطبيق"""
    return {
        "message": "Digital Export Manager API v1.0",
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
