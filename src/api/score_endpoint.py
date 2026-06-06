"""
POST /score — parola güvenlik skoru endpointi.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from src.security.patterns import detect_patterns
from src.security.risk_scorer import HybridRiskScorer

router = APIRouter()
scorer = HybridRiskScorer()


class ScoreRequest(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Parola boş olamaz.")
        return v


class ScoreResponse(BaseModel):
    password_length: int
    strength_score: float
    risk_score: float
    security_level: str
    weak_patterns: list[str]
    message: str


@router.post("/score", response_model=ScoreResponse)
def score_password(request: ScoreRequest):
    password = request.password.strip()
    if not password:
        raise HTTPException(status_code=422, detail="Parola boş olamaz.")

    result = scorer.score(password)
    strength_score = result.final_score
    risk_score = round(100 - strength_score, 2)
    level = result.security_level
    patterns = detect_patterns(password)

    messages = {
        "Çok Zayıf": "Bu parola çok zayıf. Hemen değiştirin.",
        "Zayıf": "Bu parola zayıf. Daha güçlü bir parola seçin.",
        "Orta": "Parola orta düzeyde güvenli. İyileştirilebilir.",
        "Güçlü": "Parola güçlü.",
        "Çok Güçlü": "Mükemmel! Parola çok güçlü.",
    }

    return ScoreResponse(
        password_length=len(password),
        strength_score=strength_score,
        risk_score=risk_score,
        security_level=level,
        weak_patterns=patterns,
        message=messages[level],
    )