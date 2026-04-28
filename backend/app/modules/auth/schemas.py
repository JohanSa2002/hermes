from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    business_name: str
    business_type: str
    timezone: str = "UTC"
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v

    @field_validator("business_name")
    @classmethod
    def business_name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre del negocio no puede estar vacío")
        return v.strip()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(TokenResponse):
    business_id: int
    user_id: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    access_token: str


class MetaCallbackRequest(BaseModel):
    code: str
    redirect_uri: str


class UserRead(BaseModel):
    id: int
    business_id: int
    email: str
    role: str

    model_config = {"from_attributes": True}
