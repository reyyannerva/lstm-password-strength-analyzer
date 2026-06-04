"""
FastAPI application entrypoint.
"""

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.generate_endpoint import router as generate_router
from src.api.score_endpoint import router as score_router


PROJECT_NAME = "LSTM Password Strength Analyzer"
API_TITLE = "LSTM Password Strength Analyzer API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
LSTM tabanlı parola güvenlik analizi ve güvenli parola üretme API sistemi.

Bu API, parola skorlama ve güvenli parola üretme işlemlerini sağlar.
"""

TAGS_METADATA = [
    {
        "name": "Health",
        "description": "API çalışma durumu ve servis bilgisi endpointleri.",
    },
    {
        "name": "Password Scoring",
        "description": "Parola güvenlik skoru ve zayıf desen tespiti işlemleri.",
    },
    {
        "name": "Password Generator",
        "description": "Güvenli parola üretme ve skorlama işlemleri.",
    },
]


def create_app() -> FastAPI:
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION,
        openapi_tags=TAGS_METADATA,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(score_router, tags=["Password Scoring"])
    app.include_router(generate_router, tags=["Password Generator"])

    register_health_routes(app)

    return app


def register_health_routes(app: FastAPI) -> None:
    @app.get("/", tags=["Health"])
    def root() -> dict[str, Any]:
        return {
            "project": PROJECT_NAME,
            "api": API_TITLE,
            "version": API_VERSION,
            "status": "running",
            "docs": "/docs",
            "endpoints": {
                "health": "GET /health",
                "score": "POST /score",
                "generate": "POST /generate",
            },
        }

    @app.get("/health", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {
            "status": "ok",
            "message": "API çalışıyor.",
            "version": API_VERSION,
        }


app = create_app()