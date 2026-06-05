"""
POST /score — parola güvenlik skoru endpointi.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from src.security.patterns import detect_patterns

router = APIRouter()


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
    risk_score: float
    security_level: str
    weak_patterns: list[str]
    message: str


def _security_level(risk_score: float) -> str:
    if risk_score >= 80:
        return "Çok Zayıf"
    elif risk_score >= 60:
        return "Zayıf"
    elif risk_score >= 40:
        return "Orta"
    elif risk_score >= 20:
        return "Güçlü"
    else:
        return "Çok Güçlü"


@router.post("/score", response_model=ScoreResponse)
def score_password(request: ScoreRequest):
    password = request.password.strip()
    if not password:
        raise HTTPException(status_code=422, detail="Parola boş olamaz.")

    patterns = detect_patterns(password)

    # Kural tabanlı basit risk skoru (model entegrasyonuna kadar)
    length_score = max(0, 100 - len(password) * 5)
    pattern_penalty = len(patterns) * 15
    raw_score = min(100.0, length_score + pattern_penalty)
    risk_score = round(raw_score, 2)

    level = _security_level(risk_score)

    messages = {
        "Çok Zayıf": "Bu parola çok zayıf. Hemen değiştirin.",
        "Zayıf": "Bu parola zayıf. Daha güçlü bir parola seçin.",
        "Orta": "Parola orta düzeyde güvenli. İyileştirilebilir.",
        "Güçlü": "Parola güçlü.",
        "Çok Güçlü": "Mükemmel! Parola çok güçlü.",
    }

    return ScoreResponse(
        password_length=len(password),
        risk_score=risk_score,
        security_level=level,
        weak_patterns=patterns,
        message=messages[level],
    )
