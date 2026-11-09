import json
import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.core.db import Db
from app.core.errors import error_response, register_errors
from app.core.spa import SPAStaticFiles
from app.modules.identity.routes import router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="JG Repuestos",
        version="0.1.0",
        docs_url="/api/v1/docs",
        openapi_url="/api/v1/openapi.json",
        redoc_url=None,
    )
    register_errors(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def request_metadata(request: Request, call_next):
        request_id = str(uuid4())
        started = time.monotonic()
        try:
            response = await call_next(request)
        except Exception:  # noqa: BLE001 - frontera HTTP: respuesta uniforme sin filtrar secretos
            # No registrar cuerpos, parámetros SQL ni secretos de configuración.
            logging.getLogger("jg.http").error(
                json.dumps({"request_id": request_id, "event": "request_failed"})
            )
            response = error_response(
                "INTERNAL_ERROR", "No fue posible completar la solicitud.", 500
            )
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Cache-Control"] = "no-store"
        logging.getLogger("jg.http").info(
            json.dumps(
                {
                    "request_id": request_id,
                    "method": request.method,
                    "status": response.status_code,
                    "duration_ms": round((time.monotonic() - started) * 1000),
                }
            )
        )
        return response

    @app.get("/api/v1/health", tags=["Sistema"])
    def health():
        return {"status": "ok", "service": "jg-repuestos", "phase": 1}

    @app.get("/api/v1/ready", tags=["Sistema"])
    def ready(db: Db):
        try:
            db.execute(text("SELECT 1 FROM users LIMIT 1"))
        except SQLAlchemyError:
            return error_response(
                "DATABASE_UNAVAILABLE", "Base de datos no disponible o sin migraciones.", 503
            )
        return {"status": "ready"}

    app.include_router(router, prefix="/api/v1")
    if settings.frontend_dist is not None:
        app.mount("/", SPAStaticFiles(directory=settings.frontend_dist, html=True), name="web")
    return app


app = create_app()
