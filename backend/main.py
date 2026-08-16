"""
Digital Export Manager API v1.0
Digital Export Manager â€” Intelligent Operating Platform for export operations
FastAPI Backend â€” Entry Point
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
from app.core.credentials.credential_store import CredentialStore
from app.core.credentials.username_password_credential import UsernamePasswordCredential
from app.core.credentials.client_id_secret_credential import ClientIdSecretCredential
from app.core.credentials.api_key_credential import ApiKeyCredential
from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.knowledge.orchestrator import KnowledgeOrchestrator
from app.agent.decision_engine.engine import ReasoningEngine
from app.agent.knowledge.graph_provider import KnowledgeGraphProvider
from app.agent.knowledge.company_knowledge_provider import CompanyKnowledgeProvider
from app.agent.knowledge.regulations_provider import RegulationsKnowledgeProvider
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
    ط¥ط¯ط§ط±ط© ط¯ظˆط±ط© ط­ظٹط§ط© ط§ظ„طھط·ط¨ظٹظ‚:
    - Startup: طھظ‡ظٹط¦ط© ظ‚ط§ط¹ط¯ط© ط§ظ„ط¨ظٹط§ظ†ط§طھ + طھط´ط؛ظٹظ„ ETA Scheduler
    - Shutdown: ط¥ظٹظ‚ط§ظپ ETA Scheduler + طھظ†ط¸ظٹظپ ط§ظ„ظ…ظˆط§ط±ط¯
    """
    # ========== STARTUP ==========
    print("[STARTUP] Starting Digital Export Manager API...")
    init_db()
    print("[SUCCESS] Database initialized")

    # Register LLM provider
    try:
        llm_cred_store = CredentialStore()

        if settings.LLM_API_KEY:
            llm_cred_store.register(
                "llm_api_key",
                ApiKeyCredential(
                    key=settings.LLM_API_KEY,
                    source="env",
                ),
            )

            llm_provider = GeminiProvider(
                api_key=settings.LLM_API_KEY,
                model=settings.LLM_MODEL,
                credential_store=llm_cred_store,
            )
            await llm_registry.register(llm_provider)
            print(f"[SUCCESS] LLM provider registered: {settings.LLM_PROVIDER}")
        else:
            print("[WARNING] LLM_API_KEY is not configured. LLM provider not registered.")
    except Exception as exc:
        print(f"[WARNING] LLM provider registration failed: {exc}")
    try:
        from app.services.notification import credential_store as notification_credential_store

        if settings.SMTP_HOST and (settings.SMTP_USER or settings.SMTP_PASSWORD):
            notification_credential_store.register(
                "smtp_credentials",
                UsernamePasswordCredential(
                    username=settings.SMTP_USER,
                    password=settings.SMTP_PASSWORD,
                    source="env",
                ),
            )
            print("[SUCCESS] SMTP credentials registered in CredentialStore")
        else:
            print("[WARNING] SMTP credentials are not configured. SMTP credentials not registered.")
    except Exception as exc:
        print(f"[WARNING] SMTP credential registration failed: {exc}")
    
    # Register Knowledge providers
    # Register Moaah External Source Adapter when configured
    try:
        knowledge_cred_store = CredentialStore()

        if settings.MOAAH_API_KEY and settings.MOAAH_BASE_URL:
            from app.agent.knowledge.mooadapter import MoaahExternalSourceAdapter

            knowledge_cred_store.register(
                "moaah_api_key",
                ApiKeyCredential(
                    key=settings.MOAAH_API_KEY,
                    source="env",
                ),
            )

            moaah_adapter = MoaahExternalSourceAdapter(
                config={
                    "source_id": settings.MOAAH_SOURCE_ID,
                    "name": settings.MOAAH_SOURCE_NAME,
                    "type": settings.MOAAH_SOURCE_TYPE,
                    "version": settings.MOAAH_SOURCE_VERSION,
                    "updated_at": "2026-08-12T00:00:00Z",
                    "base_url": settings.MOAAH_BASE_URL,
                    "timeout_seconds": settings.MOAAH_TIMEOUT_SECONDS,
                },
                credential_store=knowledge_cred_store,
            )
            await knowledge_provider_registry.register(moaah_adapter)
            print(f"[SUCCESS] Moaah External Source Adapter registered: {settings.MOAAH_SOURCE_ID}")
        else:
            print("[WARNING] Moaah API credentials are not configured. Moaah adapter not registered.")
    except Exception as exc:
        print(f"[WARNING] Moaah External Source Adapter registration failed: {exc}")
    # Register TradeData External Source Adapter when configured
    try:
        if settings.TRADEDATA_API_KEY and settings.TRADEDATA_BASE_URL:
            from app.agent.knowledge.tradedata_provider import TradeDataExternalSourceAdapter

            knowledge_cred_store.register(
                "tradedata_api_key",
                ApiKeyCredential(
                    key=settings.TRADEDATA_API_KEY,
                    source="env",
                ),
            )

            tradedata_adapter = TradeDataExternalSourceAdapter(
                config={
                    "source_id": settings.TRADEDATA_SOURCE_ID,
                    "name": settings.TRADEDATA_SOURCE_NAME,
                    "type": settings.TRADEDATA_SOURCE_TYPE,
                    "version": settings.TRADEDATA_SOURCE_VERSION,
                    "updated_at": "2026-08-13T00:00:00Z",
                    "base_url": settings.TRADEDATA_BASE_URL,
                    "timeout_seconds": settings.TRADEDATA_TIMEOUT_SECONDS,
                },
                credential_store=knowledge_cred_store,
            )
            await knowledge_provider_registry.register(tradedata_adapter)
            print(f"[SUCCESS] TradeData External Source Adapter registered: {settings.TRADEDATA_SOURCE_ID}")
        else:
            print("[WARNING] TradeData API credentials are not configured. TradeData adapter not registered.")
    except Exception as exc:
        print(f"[WARNING] TradeData External Source Adapter registration failed: {exc}")
    # Register ZATCA External Source Adapter when configured
    try:
        if settings.ZATCA_API_KEY and settings.ZATCA_BASE_URL:
            from app.agent.knowledge.zatca_provider import ZatcaExternalSourceAdapter

            knowledge_cred_store.register(
                "zatca_api_key",
                ApiKeyCredential(
                    key=settings.ZATCA_API_KEY,
                    source="env",
                ),
            )

            zatca_adapter = ZatcaExternalSourceAdapter(
                config={
                    "source_id": settings.ZATCA_SOURCE_ID,
                    "name": settings.ZATCA_SOURCE_NAME,
                    "type": settings.ZATCA_SOURCE_TYPE,
                    "version": settings.ZATCA_SOURCE_VERSION,
                    "updated_at": "2026-08-14T00:00:00Z",
                    "base_url": settings.ZATCA_BASE_URL,
                    "timeout_seconds": settings.ZATCA_TIMEOUT_SECONDS,
                },
                credential_store=knowledge_cred_store,
            )
            await knowledge_provider_registry.register(zatca_adapter)
            print(f"[SUCCESS] ZATCA External Source Adapter registered: {settings.ZATCA_SOURCE_ID}")
        else:
            print("[WARNING] ZATCA API credentials are not configured. ZATCA adapter not registered.")
    except Exception as exc:
        print(f"[WARNING] ZATCA External Source Adapter registration failed: {exc}")
    # Register GCC-Stat External Source Adapter when configured
    try:
        if settings.GCCSTAT_BASE_URL and settings.GCCSTAT_API_KEY:
            from app.agent.knowledge.gccstat_provider import GccstatExternalSourceAdapter

            knowledge_cred_store.register(
                "gccstat_api_key",
                ApiKeyCredential(
                    key=settings.GCCSTAT_API_KEY,
                    source="env",
                ),
            )

            gccstat_adapter = GccstatExternalSourceAdapter(
                config={
                    "source_id": settings.GCCSTAT_SOURCE_ID,
                    "name": settings.GCCSTAT_SOURCE_NAME,
                    "type": settings.GCCSTAT_SOURCE_TYPE,
                    "version": settings.GCCSTAT_SOURCE_VERSION,
                    "updated_at": "2026-08-14T00:00:00Z",
                    "base_url": settings.GCCSTAT_BASE_URL,
                    "timeout_seconds": settings.GCCSTAT_TIMEOUT_SECONDS,
                },
                credential_store=knowledge_cred_store,
            )
            await knowledge_provider_registry.register(gccstat_adapter)
            print(f"[SUCCESS] GCC-Stat External Source Adapter registered: {settings.GCCSTAT_SOURCE_ID}")
        else:
            print("[WARNING] GCC-Stat API credentials are not configured. GCC-Stat adapter not registered.")
    except Exception as exc:
        print(f"[WARNING] GCC-Stat External Source Adapter registration failed: {exc}")
    # Register UN Comtrade External Source Adapter (Preview API works without API key)
    try:
        from app.agent.knowledge.uncomtrade_provider import UnComtradeExternalSourceAdapter

        uncomtrade_adapter = UnComtradeExternalSourceAdapter(
            config={
                "source_id": settings.UN_COMTRADE_SOURCE_ID,
                "name": settings.UN_COMTRADE_SOURCE_NAME,
                "type": settings.UN_COMTRADE_SOURCE_TYPE,
                "version": settings.UN_COMTRADE_SOURCE_VERSION,
                "updated_at": settings.UN_COMTRADE_UPDATED_AT,
                "base_url": settings.UN_COMTRADE_BASE_URL,
                "api_key": settings.UN_COMTRADE_API_KEY or None,
                "timeout_seconds": settings.UN_COMTRADE_TIMEOUT_SECONDS,
            },
        )
        await knowledge_provider_registry.register(uncomtrade_adapter)
        print(f"[SUCCESS] UN Comtrade External Source Adapter registered: {settings.UN_COMTRADE_SOURCE_ID}")
    except Exception as exc:
        print(f"[WARNING] UN Comtrade External Source Adapter registration failed: {exc}")
    # Register FAOSTAT External Source Adapter when configured
    try:
        cred_store = CredentialStore()

        if settings.FAOSTAT_BASE_URL and settings.FAOSTAT_USER and settings.FAOSTAT_PASSWORD:
            from app.agent.knowledge.faostat_provider import FaostatExternalSourceAdapter

            cred_store.register(
                "faostat_username",
                UsernamePasswordCredential(
                    username=settings.FAOSTAT_USER,
                    password="",
                    source="env",
                ),
            )
            cred_store.register(
                "faostat_password",
                UsernamePasswordCredential(
                    username="",
                    password=settings.FAOSTAT_PASSWORD,
                    source="env",
                ),
            )

            faostat_adapter = FaostatExternalSourceAdapter(
                config={
                    "source_id": settings.FAOSTAT_SOURCE_ID,
                    "name": settings.FAOSTAT_SOURCE_NAME,
                    "type": settings.FAOSTAT_SOURCE_TYPE,
                    "version": settings.FAOSTAT_SOURCE_VERSION,
                    "updated_at": "2026-08-14T00:00:00Z",
                    "base_url": settings.FAOSTAT_BASE_URL,
                    "timeout_seconds": settings.FAOSTAT_TIMEOUT_SECONDS,
                    "default_domain": settings.FAOSTAT_DEFAULT_DOMAIN,
                },
                credential_store=cred_store,
            )
            await knowledge_provider_registry.register(faostat_adapter)
            print(f"[SUCCESS] FAOSTAT External Source Adapter registered: {settings.FAOSTAT_SOURCE_ID}")
        else:
            print("[WARNING] FAOSTAT credentials are not configured. FAOSTAT adapter not registered.")
    except Exception as exc:
        print(f"[WARNING] FAOSTAT External Source Adapter registration failed: {exc}")
    try:
        if settings.ETA_CLIENT_ID and settings.ETA_CLIENT_SECRET:
            from app.services.eta import credential_store as eta_credential_store

            eta_credential_store.register(
                "eta_client_id",
                ClientIdSecretCredential(
                    client_id=settings.ETA_CLIENT_ID,
                    client_secret="",
                    source="env",
                ),
            )
            eta_credential_store.register(
                "eta_client_secret",
                ClientIdSecretCredential(
                    client_id="",
                    client_secret=settings.ETA_CLIENT_SECRET,
                    source="env",
                ),
            )
            print(f"[SUCCESS] ETA credentials registered in CredentialStore")
        else:
            print("[WARNING] ETA credentials are not configured. ETA credentials not registered.")
    except Exception as exc:
        print(f"[WARNING] ETA credential registration failed: {exc}")
    try:
        if settings.LETME_API_ID and settings.LETME_API_PASSWORD:
            from app.services.shipping import credential_store as shipping_credential_store

            shipping_credential_store.register(
                "letmeship_api_id",
                UsernamePasswordCredential(
                    username=settings.LETME_API_ID,
                    password=settings.LETME_API_PASSWORD,
                    source="env",
                ),
            )
            print(f"[SUCCESS] LetMeShip credentials registered in CredentialStore")
        else:
            print("[WARNING] LetMeShip credentials are not configured. LetMeShip credentials not registered.")
    except Exception as exc:
        print(f"[WARNING] LetMeShip credential registration failed: {exc}")
    try:
        if settings.SENDCLOUD_PUBLIC_KEY and settings.SENDCLOUD_SECRET_KEY:
            from app.services.shipping import credential_store as shipping_credential_store

            shipping_credential_store.register(
                "sendcloud_public_key",
                ClientIdSecretCredential(
                    client_id=settings.SENDCLOUD_PUBLIC_KEY,
                    client_secret=settings.SENDCLOUD_SECRET_KEY,
                    source="env",
                ),
            )
            print(f"[SUCCESS] SendCloud credentials registered in CredentialStore")
        else:
            print("[WARNING] SendCloud credentials are not configured. SendCloud credentials not registered.")
    except Exception as exc:
        print(f"[WARNING] SendCloud credential registration failed: {exc}")
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

    try:
        regulations_provider = RegulationsKnowledgeProvider(file_path=settings.REGULATIONS_FILE_PATH)
        await knowledge_provider_registry.register(regulations_provider)
        print("[SUCCESS] Regulations Knowledge provider registered")
    except Exception as exc:
        print(f"[WARNING] Regulations Knowledge provider registration failed: {exc}")
    
    # Wire Memory and Knowledge providers for Trade Intelligence
    try:
        set_memory_provider(memory_provider)
        set_knowledge_registry(knowledge_provider_registry)
        print("[SUCCESS] Trade Intelligence providers wired")
    except Exception as exc:
        print(f"[WARNING] Trade Intelligence provider wiring failed: {exc}")

    # ========== Knowledge Orchestration / Fusion Layer ==========
    if getattr(settings, "KNOWLEDGE_ORCHESTRATION_ENABLED", True):
        try:
            orchestrator = KnowledgeOrchestrator(
                registry=knowledge_provider_registry,
                config=settings,
            )
            print("[SUCCESS] Knowledge Orchestrator initialized")
        except Exception as exc:
            print(f"[WARNING] Knowledge Orchestrator initialization failed: {exc}")
            orchestrator = None
    else:
        orchestrator = None

    reasoning_engine = ReasoningEngine(
        knowledge_provider_registry=knowledge_provider_registry,
        memory_provider=memory_provider,
        llm_registry=llm_registry,
    )
    if orchestrator is not None:
        reasoning_engine._knowledge_orchestrator = orchestrator
        print("[SUCCESS] Knowledge Orchestrator attached to ReasoningEngine")

    app.state.reasoning_engine = reasoning_engine
    
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


# ط¥ظ†ط´ط§ط، طھط·ط¨ظٹظ‚ FastAPI
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

# ط¥ط¹ط¯ط§ط¯ CORS â€” ظٹظڈط¹ط¯ظ„ ظپظٹ ط§ظ„ط¥ظ†طھط§ط¬ ظ„ظٹظƒظˆظ† ط£ظƒط«ط± طھط­ط¯ظٹط¯ط§ظ‹
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)

# ========== طھط³ط¬ظٹظ„ ط§ظ„ظ€ Routers ==========
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
    """ط§ظ„طµظپط­ط© ط§ظ„ط±ط¦ظٹط³ظٹط© â€” ظ…ط¹ظ„ظˆظ…ط§طھ ط§ظ„طھط·ط¨ظٹظ‚"""
    return {
        "message": "Digital Export Manager API v1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """ظپط­طµ طµط­ط© ط§ظ„طھط·ط¨ظٹظ‚ â€” ظٹظڈط³طھط®ط¯ظ… ظپظٹ Monitoring"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }


