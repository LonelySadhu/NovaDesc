from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from api.v1.equipment.router import router as equipment_router
from api.v1.ai.router import router as ai_router
from api.v1.knowledge_base.router import router as knowledge_base_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

@app.on_event("startup")
async def _startup() -> None:
    from core.dependencies import get_vector_store
    store = get_vector_store()
    await store.init()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(equipment_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(knowledge_base_router, prefix="/api/v1")


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}
