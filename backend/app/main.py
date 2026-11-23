import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from app.api.routes import auth, dashboard, leads
from app.core.config import get_settings
from app.core.exceptions import LeadNotFoundError
from app.core.logging import configure_logging
from app.core.middleware import RequestSizeLimitMiddleware
from app.database.connection import create_mongo_client
from app.database.indexes import create_indexes
from app.repositories.lead_repository import LeadRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.lead_service import LeadService

logger = logging.getLogger(__name__)
settings = get_settings()
configure_logging(settings)


@asynccontextmanager
async def lifespan(application: FastAPI):
    client = create_mongo_client(settings)
    try:
        await client.admin.command("ping")
        database = client[settings.database_name]
        await create_indexes(database)
        application.state.mongo_client = client
        application.state.database = database
        application.state.auth_service = AuthService(UserRepository(database.users), settings)
        application.state.lead_service = LeadService(LeadRepository(database.leads))
        yield
    except PyMongoError:
        logger.error("MongoDB initialization failed.")
        raise
    finally:
        await client.close()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs" if settings.app_env.lower() != "production" else None,
    redoc_url="/redoc" if settings.app_env.lower() != "production" else None,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(RequestSizeLimitMiddleware, max_bytes=1_048_576)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(PyMongoError)
async def handle_database_error(_request: Request, _exc: PyMongoError):
    logger.error("A database operation failed.")
    return JSONResponse(status_code=503, content={"detail": "Database service is unavailable."})


@app.exception_handler(LeadNotFoundError)
async def handle_lead_not_found(_request: Request, _exc: LeadNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Lead not found."})


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}


@app.get("/ready", tags=["health"])
async def ready(request: Request):
    client = getattr(request.app.state, "mongo_client", None)
    if client is None:
        return JSONResponse(status_code=503, content={"status": "unavailable"})
    try:
        await client.admin.command("ping")
    except PyMongoError:
        logger.warning("Readiness check could not reach the database.")
        return JSONResponse(status_code=503, content={"status": "unavailable"})
    return {"status": "ready"}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(leads.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
