"""POST /explain — password explanation endpoint."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from src.security.explain import explain_password

router = APIRouter(tags=["Password Explanation"])


class ExplainRequest(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Parola boş olamaz.")
        return v


class ExplainResponse(BaseModel):
    password: str
    security_level: str
    assessment: str
    missing_requirements: list[str]
    pattern_warnings: list[str]
    suggestions: list[str]
    is_strong: bool


@router.post(
    "/explain",
    response_model=ExplainResponse,
    summary="Explain Password Strength",
    description=(
        "Parola analiz sonucunu açıklar, risk nedenlerini listeler ve "
        "kullanıcıya iyileştirme önerileri döner."
    ),
)
def explain_password_endpoint(request: ExplainRequest) -> ExplainResponse:
    password = request.password.strip()

    if not password:
        raise HTTPException(status_code=422, detail="Parola boş olamaz.")

    explanation = explain_password(password)

    return ExplainResponse(
        password=explanation["password"],
        security_level=explanation["security_level"],
        assessment=explanation["assessment"],
        missing_requirements=explanation["missing_requirements"],
        pattern_warnings=explanation["pattern_warnings"],
        suggestions=explanation["suggestions"],
        is_strong=explanation["is_strong"],
    )
