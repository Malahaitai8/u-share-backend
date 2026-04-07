# app/crud.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from . import models, schemas, security


def get_user_by_username(db: Session, username: str):
    """根据用户名查询用户"""
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    """创建新用户"""
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    user_points = models.UserPoints(user_id=db_user.id, current_points=0, total_points=0)
    db.add(user_points)
    db.commit()
    
    return db_user


def get_or_create_user_points(db: Session, user_id: int):
    """获取或创建用户积分记录"""
    user_points = db.query(models.UserPoints).filter(models.UserPoints.user_id == user_id).first()
    if not user_points:
        user_points = models.UserPoints(user_id=user_id, current_points=0, total_points=0)
        db.add(user_points)
        db.commit()
        db.refresh(user_points)
    return user_points


def add_classification_record(db: Session, user_id: int, garbage_type: str, recognition_method: str, points: int = 1):
    """添加分类记录并更新积分"""
    record = models.ClassificationRecord(
        user_id=user_id,
        garbage_type=garbage_type,
        recognition_method=recognition_method,
        points_earned=points
    )
    db.add(record)
    
    user_points = get_or_create_user_points(db, user_id)
    user_points.current_points += points
    user_points.total_points += points
    
    db.commit()
    db.refresh(record)
    return record


def get_user_stats(db: Session, user_id: int):
    """获取用户统计数据"""
    user_points = get_or_create_user_points(db, user_id)
    
    total_classifications = db.query(models.ClassificationRecord).filter(
        models.ClassificationRecord.user_id == user_id
    ).count()
    
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    week_classifications = db.query(models.ClassificationRecord).filter(
        models.ClassificationRecord.user_id == user_id,
        models.ClassificationRecord.created_at >= week_start
    ).count()
    
    week_points = db.query(func.coalesce(func.sum(models.ClassificationRecord.points_earned), 0)).filter(
        models.ClassificationRecord.user_id == user_id,
        models.ClassificationRecord.created_at >= week_start
    ).scalar()
    
    rank_percentile = get_user_rank_percentile(db, user_id)
    
    return {
        "current_points": user_points.current_points,
        "total_points": user_points.total_points,
        "total_classifications": total_classifications,
        "week_classifications": week_classifications,
        "week_points": int(week_points),
        "rank_percentile": rank_percentile
    }


def get_user_rank_percentile(db: Session, user_id: int):
    """计算用户积分超过全校用户的百分比"""
    user_points = get_or_create_user_points(db, user_id)
    user_total = user_points.total_points
    
    all_users = db.query(models.UserPoints).all()
    if not all_users:
        return 0.0
    
    users_below = sum(1 for up in all_users if up.total_points < user_total)
    percentile = (users_below / len(all_users)) * 100
    
    return round(percentile, 1)


def get_recent_classifications(db: Session, user_id: int, limit: int = 10):
    """获取用户最近的分类记录"""
    return db.query(models.ClassificationRecord).filter(
        models.ClassificationRecord.user_id == user_id
    ).order_by(models.ClassificationRecord.created_at.desc()).limit(limit).all()