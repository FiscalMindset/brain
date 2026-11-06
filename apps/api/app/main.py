"""SecondBrain API — FastAPI application entry point."""
from __future__ import annotations
import logging, time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import agents, audit, auth, dashboard, graph, integrations, memory, projects, research, search, sources
from app.core.config import settings
from app.core.database import init_db
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("secondbrain")
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
app = FastAPI(title="SecondBrain API", version=settings.APP_VERSION, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")] or ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    logger.info("%s %s %s %.3fs", request.method, request.url.path, response.status_code, time.time() - start)
    return response
@app.exception_handler(Exception)
async def global_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
@app.get("/api/health")
def health(): return {"status": "ok", "service": "secondbrain-api"}
for r in (auth.router, sources.router, search.router, research.router, projects.router, agents.router, integrations.router, memory.router, graph.router, dashboard.router, audit.router):
    app.include_router(r, prefix="/api")
