"""
POST /generate — güvenli parola üretme endpointi.
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator

from src.security.generator import generate_password
from src.security.risk_scorer import calculate_hybrid_score

router = APIRouter(tags=["Password Generator"])

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


class GenerateRequest(BaseModel):
    length: int = Field(
        default=16,
        ge=MIN_PASSWORD_LENGTH,
        le=MAX_PASSWORD_LENGTH,
        description="Üretilecek parolanın uzunluğu.",
        examples=[16],
    )
    use_uppercase: bool = Field(default=True, description="Büyük harf kullan.")
    use_lowercase: bool = Field(default=True, description="Küçük harf kullan.")
    use_digits: bool = Field(default=True, description="Rakam kullan.")
    use_special: bool = Field(default=True, description="Özel karakter kullan.")

    @model_validator(mode="after")
    def validate_character_options(self):
        if not any(
            [
                self.use_uppercase,
                self.use_lowercase,
                self.use_digits,
                self.use_special,
            ]
        ):
            raise ValueError("En az bir karakter türü seçilmelidir.")

        return self


class GenerateResponse(BaseModel):
    generated_password: str
    password_length: int
    security_score: float
    security_level: str
    weak_patterns: list[str]
    feedback: list[str]
    message: str
    metadata: dict[str, Any]


def _build_message(security_level: str) -> str:
    messages = {
        "Çok Zayıf": "Üretilen parola çok zayıf. Daha uzun ve karmaşık bir parola önerilir.",
        "Zayıf": "Üretilen parola zayıf. Karakter çeşitliliği artırılmalıdır.",
        "Orta": "Üretilen parola orta seviyede güvenlidir. Daha güçlü hale getirilebilir.",
        "Güçlü": "Üretilen parola güçlüdür.",
        "Çok Güçlü": "Üretilen parola çok güçlüdür ve kullanıma uygundur.",
    }

    return messages.get(security_level, "Parola başarıyla üretildi.")


@router.post(
    "/generate",
    response_model=GenerateResponse,
    summary="Generate Secure Password",
    description=(
        "Belirtilen uzunluk ve karakter seçeneklerine göre güvenli parola üretir. "
        "Üretilen parola hibrit risk skorlayıcı ile değerlendirilir."
    ),
)
def generate_secure_password(request: GenerateRequest) -> GenerateResponse:
    if request.length < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=422,
            detail=f"Parola uzunluğu en az {MIN_PASSWORD_LENGTH} olmalıdır.",
        )

    if request.length > MAX_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=422,
            detail=f"Parola uzunluğu en fazla {MAX_PASSWORD_LENGTH} olabilir.",
        )

    try:
        generated = generate_password(length=request.length)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Parola üretme sırasında beklenmeyen bir hata oluştu: {str(exc)}",
        ) from exc

    password = generated.get("password")

    if not password:
        raise HTTPException(
            status_code=500,
            detail="Generator modülü geçerli bir parola döndürmedi.",
        )

    weak_patterns = generated.get("weak_patterns", [])

    score_result = calculate_hybrid_score(password)

    return GenerateResponse(
        generated_password=password,
        password_length=len(password),
        security_score=score_result["final_score"],
        security_level=score_result["security_level"],
        weak_patterns=weak_patterns,
        feedback=score_result["feedback"],
        message=_build_message(score_result["security_level"]),
        metadata={
            "requested_length": request.length,
            "actual_length": len(password),
            "options": {
                "use_uppercase": request.use_uppercase,
                "use_lowercase": request.use_lowercase,
                "use_digits": request.use_digits,
                "use_special": request.use_special,
            },
            "scoring_method": "hybrid_rule_based_lstm_ready",
            "generator_module": "src.security.generator.generate_password",
        },
    )