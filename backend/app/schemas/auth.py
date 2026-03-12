from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    display_name: str
    password: str
    user_type: str = "EMPLOYEE"
    primary_node_id: str | None = None


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    display_name: str
    user_type: str
    primary_node_id: str | None
    is_active: bool

    model_config = {"from_attributes": True}
