# app/schemas.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# --- User Schemas ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    username: str = Field(..., example="newuser123", description="新用户的唯一用户名")
    password: str = Field(..., example="a_strong_password", description="用户的登录密码")

class User(UserBase):
    id: int
    username: str = Field(..., example="newuser123")

    class Config:
        from_attributes = True


# --- Stats Schemas ---
class ClassificationRecordBase(BaseModel):
    garbage_type: Optional[str] = None
    recognition_method: Optional[str] = None
    points_earned: int = 0

class ClassificationRecordCreate(ClassificationRecordBase):
    pass

class ClassificationRecord(ClassificationRecordBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    current_points: int = 0
    total_points: int = 0
    total_classifications: int = 0
    week_classifications: int = 0
    week_points: int = 0
    rank_percentile: float = 0.0

    class Config:
        from_attributes = True


class LeaderboardInfo(BaseModel):
    rank_percentile: float = 0.0
