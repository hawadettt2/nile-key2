from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db
from app.routers import auth, shipping, invoice, suppliers, customers, customs, resources, documents

app = FastAPI(title="Nile Key API", description="Digital platform for Egyptian export management", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

for router in [auth, shipping, invoice, suppliers, customers, customs, resources, documents]:
    app.include_router(router.router)

@app.get("/")
def root():
    return {"message": "Nile Key API v1.0", "status": "running", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
