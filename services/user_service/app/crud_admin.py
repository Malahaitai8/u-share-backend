# services/user_service/app/crud_admin.py
# 校园垃圾分类统计相关 CRUD 操作

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, cast, Date
from datetime import datetime, timedelta, date
from typing import List, Optional
from . import models


def get_stats_overview(db: Session) -> dict:
    """获取总览数据"""
    # 总分类次数
    total_classifications = db.query(models.ClassificationRecord).count()
    
    # 总积分
    total_points = db.query(func.coalesce(func.sum(models.ClassificationRecord.points_earned), 0)).scalar() or 0
    
    # 总用户数
    total_users = db.query(models.User).count()
    
    # 站点数（从 classification_records 中有位置信息的记录统计）
    station_count = db.query(
        models.ClassificationRecord.dustbin_name
    ).filter(
        models.ClassificationRecord.dustbin_name.isnot(None)
    ).distinct().count()
    
    # 本周分类次数
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_classifications = db.query(models.ClassificationRecord).filter(
        models.ClassificationRecord.created_at >= week_start
    ).count()
    
    # 本周积分
    week_points = db.query(func.coalesce(func.sum(models.ClassificationRecord.points_earned), 0)).filter(
        models.ClassificationRecord.created_at >= week_start
    ).scalar() or 0
    
    # 本周活跃用户数
    week_active_users = db.query(
        models.ClassificationRecord.user_id
    ).filter(
        models.ClassificationRecord.created_at >= week_start
    ).distinct().count()
    
    return {
        "total_classifications": total_classifications,
        "total_points": int(total_points),
        "total_users": total_users,
        "station_count": station_count,
        "week_classifications": week_classifications,
        "week_points": int(week_points),
        "week_active_users": week_active_users
    }


def get_stats_trend(db: Session, start_date: str, end_date: str, period: str = "day") -> dict:
    """获取趋势数据"""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # 构建日期分组
    if period == "day":
        date_format = "%Y-%m-%d"
        date_trunc = cast(models.ClassificationRecord.created_at, Date)
    elif period == "week":
        date_format = "%Y-W%W"
        # 简化处理，按天分组后前端聚合
        date_trunc = cast(models.ClassificationRecord.created_at, Date)
    else:  # month
        date_format = "%Y-%m"
        date_trunc = cast(models.ClassificationRecord.created_at, Date)
    
    results = db.query(
        date_trunc.label("date"),
        func.count(models.ClassificationRecord.id).label("count"),
        func.coalesce(func.sum(models.ClassificationRecord.points_earned), 0).label("points")
    ).filter(
        and_(
            models.ClassificationRecord.created_at >= start,
            models.ClassificationRecord.created_at <= end + timedelta(days=1)
        )
    ).group_by(
        date_trunc
    ).order_by(
        date_trunc
    ).all()
    
    trend = [
        {
            "date": r.date.strftime("%Y-%m-%d") if hasattr(r.date, 'strftime') else str(r.date),
            "count": r.count,
            "points": int(r.points)
        }
        for r in results
    ]
    
    return {"trend": trend}


def get_stats_by_type(db: Session, start_date: str, end_date: str) -> dict:
    """按垃圾类型统计"""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    results = db.query(
        models.ClassificationRecord.garbage_type.label("type"),
        func.count(models.ClassificationRecord.id).label("count")
    ).filter(
        and_(
            models.ClassificationRecord.created_at >= start,
            models.ClassificationRecord.created_at <= end + timedelta(days=1)
        )
    ).group_by(
        models.ClassificationRecord.garbage_type
    ).all()
    
    total = sum(r.count for r in results)
    
    stats = [
        {
            "type": r.type or "其他",
            "count": r.count,
            "percentage": round(r.count / total * 100, 1) if total > 0 else 0
        }
        for r in results
    ]
    
    return {"stats": stats}


def get_stats_by_method(db: Session, start_date: str, end_date: str) -> dict:
    """按识别方式统计"""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    results = db.query(
        models.ClassificationRecord.recognition_method.label("method"),
        func.count(models.ClassificationRecord.id).label("count")
    ).filter(
        and_(
            models.ClassificationRecord.created_at >= start,
            models.ClassificationRecord.created_at <= end + timedelta(days=1)
        )
    ).group_by(
        models.ClassificationRecord.recognition_method
    ).all()
    
    total = sum(r.count for r in results)
    
    stats = [
        {
            "method": r.method or "其他",
            "count": r.count,
            "percentage": round(r.count / total * 100, 1) if total > 0 else 0
        }
        for r in results
    ]
    
    return {"stats": stats}


def get_stats_by_location(db: Session, start_date: str, end_date: str) -> dict:
    """按投放点统计（重点）"""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    results = db.query(
        models.ClassificationRecord.dustbin_name.label("dustbin_name"),
        models.ClassificationRecord.dustbin_lng.label("dustbin_lng"),
        models.ClassificationRecord.dustbin_lat.label("dustbin_lat"),
        func.count(models.ClassificationRecord.id).label("count")
    ).filter(
        and_(
            models.ClassificationRecord.created_at >= start,
            models.ClassificationRecord.created_at <= end + timedelta(days=1),
            models.ClassificationRecord.dustbin_name.isnot(None)
        )
    ).group_by(
        models.ClassificationRecord.dustbin_name,
        models.ClassificationRecord.dustbin_lng,
        models.ClassificationRecord.dustbin_lat
    ).order_by(
        func.count(models.ClassificationRecord.id).desc()
    ).all()
    
    total = sum(r.count for r in results)
    
    stats = [
        {
            "dustbin_name": r.dustbin_name or "未知",
            "dustbin_lng": r.dustbin_lng,
            "dustbin_lat": r.dustbin_lat,
            "count": r.count,
            "percentage": round(r.count / total * 100, 1) if total > 0 else 0
        }
        for r in results
    ]
    
    return {"stats": stats}


def get_leaderboard(db: Session, limit: int = 10) -> dict:
    """用户排行榜"""
    results = db.query(
        models.User.id.label("user_id"),
        models.User.username.label("username"),
        func.count(models.ClassificationRecord.id).label("total_classifications"),
        func.coalesce(func.sum(models.ClassificationRecord.points_earned), 0).label("total_points")
    ).outerjoin(
        models.ClassificationRecord,
        models.User.id == models.ClassificationRecord.user_id
    ).group_by(
        models.User.id,
        models.User.username
    ).order_by(
        func.count(models.ClassificationRecord.id).desc()
    ).limit(limit).all()
    
    users = [
        {
            "user_id": r.user_id,
            "username": r.username,
            "total_classifications": r.total_classifications,
            "total_points": int(r.total_points),
            "rank": idx + 1
        }
        for idx, r in enumerate(results)
    ]
    
    return {"users": users}


def export_stats_csv(db: Session, start_date: str, end_date: str) -> str:
    """导出 CSV 格式的统计数据"""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    results = db.query(
        models.ClassificationRecord
    ).filter(
        and_(
            models.ClassificationRecord.created_at >= start,
            models.ClassificationRecord.created_at <= end + timedelta(days=1)
        )
    ).order_by(
        models.ClassificationRecord.created_at.desc()
    ).all()
    
    # CSV 头部
    csv_lines = ["日期,时间,用户名,垃圾类型,识别方式,获得积分,投放站点,经度,纬度"]
    
    # 获取用户名映射
    user_cache = {u.id: u.username for u in db.query(models.User).all()}
    
    for r in results:
        created = r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
        username = user_cache.get(r.user_id, f"用户{r.user_id}")
        csv_lines.append(
            f"{created},{r.garbage_type or ''},{r.recognition_method or ''},"
            f"{r.points_earned},{r.dustbin_name or ''},"
            f"{r.dustbin_lng or ''},{r.dustbin_lat or ''}"
        )
    
    return "\n".join(csv_lines)
