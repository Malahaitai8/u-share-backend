# app/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
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


# --- Incentive Mall Schemas ---
class MallItem(BaseModel):
    id: str
    category: str
    title: str
    subtitle: str
    points_cost: int
    stock_total: int
    stock_remaining: int
    image_url: str
    image_name: str


class MallItemsResponse(BaseModel):
    categories: List[str]
    items: List[MallItem]


class VolunteerConvertRequest(BaseModel):
    points_to_convert: int = Field(100, ge=100, description="用于兑换志愿工时的积分（100的整数倍）")


class VolunteerConvertResponse(BaseModel):
    request_id: int
    points_spent: int
    hours_requested: float
    status: Literal["pending_school_review"]
    message: str


class VolunteerOverview(BaseModel):
    current_points: int
    total_points: int
    consumed_points: int
    total_classifications: int
    convertible_hours: float
    conversion_ratio: str = "每100积分可申请0.5小时志愿工时"


class LeaderboardEntry(BaseModel):
    rank: int
    name: str
    score: int
    title: str
    is_top_three: bool = False
    badge: Optional[str] = None


class LeaderboardResponse(BaseModel):
    board_type: Literal["personal", "dormitory"]
    entries: List[LeaderboardEntry]
