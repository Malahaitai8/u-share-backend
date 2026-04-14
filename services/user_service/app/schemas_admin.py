# services/user_service/app/schemas_admin.py
# 校园垃圾分类统计相关 Schema

from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class OverviewResponse(BaseModel):
    total_classifications: int = 0
    total_points: int = 0
    total_users: int = 0
    station_count: int = 0
    week_classifications: int = 0
    week_points: int = 0
    week_active_users: int = 0


class TrendItem(BaseModel):
    date: str
    count: int
    points: int


class TrendResponse(BaseModel):
    trend: List[TrendItem]


class TypeStatsItem(BaseModel):
    type: str
    count: int
    percentage: float


class TypeStatsResponse(BaseModel):
    stats: List[TypeStatsItem]


class MethodStatsItem(BaseModel):
    method: str
    count: int
    percentage: float


class MethodStatsResponse(BaseModel):
    stats: List[MethodStatsItem]


class LocationStatsItem(BaseModel):
    dustbin_name: str
    dustbin_lng: Optional[float]
    dustbin_lat: Optional[float]
    count: int
    percentage: float


class LocationStatsResponse(BaseModel):
    stats: List[LocationStatsItem]


class LeaderboardItem(BaseModel):
    user_id: int
    username: str
    total_classifications: int
    total_points: int
    rank: int


class LeaderboardResponse(BaseModel):
    users: List[LeaderboardItem]
