import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import text

from app.config import settings
from app.database import Base, engine
from app.routers import (
    ai,
    analytics,
    auth,
    challenges,
    collaborations,
    comments,
    ip,
    notifications,
    projects,
    proposals,
    reports,
    routing,
    universities,
    uploads,
    ws,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("samadhan")

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    # Warm the AI classifier at boot so the first request isn't slow.
    from app.ai.classifier import get_classifier

    get_classifier()
    logger.info("Samadhan Setu API started. AI mode ready.")
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Samadhan Setu API", version=settings.APP_VERSION, lifespan=lifespan)

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors(), "code": "VALIDATION_ERROR"},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s", request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "code": "INTERNAL_ERROR"},
        )

    @app.get("/health")
    def health():
        db_ok = True
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:
            db_ok = False

        from app.ai.llm import get_ai_mode

        return {
            "status": "ok" if db_ok else "degraded",
            "db": "ok" if db_ok else "unreachable",
            "ai_mode": get_ai_mode(),
            "version": settings.APP_VERSION,
        }

    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(challenges.router, prefix="/api/v1")
    app.include_router(ai.router, prefix="/api/v1")
    app.include_router(universities.router, prefix="/api/v1")
    app.include_router(routing.router, prefix="/api/v1")
    app.include_router(proposals.router, prefix="/api/v1")
    app.include_router(collaborations.router, prefix="/api/v1")
    app.include_router(projects.router, prefix="/api/v1")
    app.include_router(ip.router, prefix="/api/v1")
    app.include_router(comments.router, prefix="/api/v1")
    app.include_router(notifications.router, prefix="/api/v1")
    app.include_router(analytics.router, prefix="/api/v1")
    app.include_router(reports.router, prefix="/api/v1")
    app.include_router(uploads.router, prefix="/api/v1")
    app.include_router(ws.router, prefix="/api/v1")

    return app


app = create_app()
