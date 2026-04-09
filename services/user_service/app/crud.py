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


def get_mall_items():
    """返回积分商城商品（示例数据，可替换为数据库读取）"""
    items = [
        {
            "id": "cafeteria-voucher-1",
            "category": "校内餐饮",
            "title": "1元代金券",
            "subtitle": "校内餐饮通用",
            "points_cost": 10,
            "stock_total": 500,
            "stock_remaining": 360,
            "image_url": "/mall-images/yiyuan-daijinquan.png",
            "image_name": "yiyuan-daijinquan"
        },
        {
            "id": "cafeteria-voucher-2",
            "category": "校内餐饮",
            "title": "2元代金券",
            "subtitle": "校内餐饮通用",
            "points_cost": 20,
            "stock_total": 420,
            "stock_remaining": 288,
            "image_url": "/mall-images/eryuan-daijinquan.png",
            "image_name": "eryuan-daijinquan"
        },
        {
            "id": "cafeteria-voucher-3",
            "category": "校内餐饮",
            "title": "3元代金券",
            "subtitle": "校内餐饮通用",
            "points_cost": 30,
            "stock_total": 360,
            "stock_remaining": 241,
            "image_url": "/mall-images/sanyuan-daijinquan.png",
            "image_name": "sanyuan-daijinquan"
        },
        {
            "id": "cafeteria-voucher-4",
            "category": "校内餐饮",
            "title": "4元代金券",
            "subtitle": "校内餐饮通用",
            "points_cost": 40,
            "stock_total": 320,
            "stock_remaining": 190,
            "image_url": "/mall-images/siyuan-daijinquan.png",
            "image_name": "siyuan-daijinquan"
        },
        {
            "id": "cafeteria-voucher-5",
            "category": "校内餐饮",
            "title": "5元代金券",
            "subtitle": "校内餐饮通用",
            "points_cost": 50,
            "stock_total": 260,
            "stock_remaining": 136,
            "image_url": "/mall-images/wuyuan-daijinquan.png",
            "image_name": "wuyuan-daijinquan"
        },
        {
            "id": "culture-keychain",
            "category": "文创",
            "title": "钥匙扣",
            "subtitle": "北交主题文创",
            "points_cost": 45,
            "stock_total": 260,
            "stock_remaining": 173,
            "image_url": "/mall-images/yaoshikou.png",
            "image_name": "yaoshikou"
        },
        {
            "id": "culture-badge",
            "category": "文创",
            "title": "校徽胸针",
            "subtitle": "北交主题文创",
            "points_cost": 60,
            "stock_total": 220,
            "stock_remaining": 138,
            "image_url": "/mall-images/xiaohui-xiongzhen.png",
            "image_name": "xiaohui-xiongzhen"
        },
        {
            "id": "culture-notebook-basic",
            "category": "文创",
            "title": "笔记本",
            "subtitle": "北交主题文创",
            "points_cost": 70,
            "stock_total": 240,
            "stock_remaining": 166,
            "image_url": "/mall-images/bijiben.png",
            "image_name": "bijiben"
        },
        {
            "id": "culture-nail-clipper",
            "category": "文创",
            "title": "指甲剪",
            "subtitle": "北交主题文创",
            "points_cost": 55,
            "stock_total": 180,
            "stock_remaining": 119,
            "image_url": "/mall-images/zhijiajian.png",
            "image_name": "zhijiajian"
        },
        {
            "id": "culture-card-holder",
            "category": "文创",
            "title": "卡套",
            "subtitle": "北交主题文创",
            "points_cost": 50,
            "stock_total": 210,
            "stock_remaining": 144,
            "image_url": "/mall-images/katao.png",
            "image_name": "katao"
        },
        {
            "id": "culture-notebook-premium",
            "category": "文创",
            "title": "精致笔记本",
            "subtitle": "北交主题文创",
            "points_cost": 120,
            "stock_total": 160,
            "stock_remaining": 92,
            "image_url": "/mall-images/jingzhi-bijiben.png",
            "image_name": "jingzhi-bijiben"
        },
        {
            "id": "culture-bookmark",
            "category": "文创",
            "title": "书签",
            "subtitle": "北交主题文创",
            "points_cost": 35,
            "stock_total": 280,
            "stock_remaining": 207,
            "image_url": "/mall-images/shuqian.png",
            "image_name": "shuqian"
        },
        {
            "id": "culture-figure",
            "category": "文创",
            "title": "小公仔",
            "subtitle": "北交主题文创",
            "points_cost": 150,
            "stock_total": 140,
            "stock_remaining": 71,
            "image_url": "/mall-images/xiao-gongzai.png",
            "image_name": "xiao-gongzai"
        },
        {
            "id": "culture-fridge-magnet",
            "category": "文创",
            "title": "冰箱贴",
            "subtitle": "北交主题文创",
            "points_cost": 65,
            "stock_total": 230,
            "stock_remaining": 158,
            "image_url": "/mall-images/bingxiangtie.png",
            "image_name": "bingxiangtie"
        },
        {
            "id": "volunteer-half-hour",
            "category": "其他",
            "title": "志愿时长",
            "subtitle": "100分/0.5小时，提交后进入学校审核流程",
            "points_cost": 100,
            "stock_total": 9999,
            "stock_remaining": 9999,
            "image_url": "/mall-images/zhiyuan-shizhang.png",
            "image_name": "zhiyuan-shizhang"
        }
    ]

    categories = ["校内餐饮", "文创", "其他"]
    return {"categories": categories, "items": items}


def convert_points_to_hours(db: Session, user_id: int, points_to_convert: int):
    """
    每100积分可发起一次工时申请：
    - 可整倍数兑换
    - 每100积分兑换0.5小时
    - 写入 volunteer_hour_requests，状态 pending_school_review
    """
    if points_to_convert < 100 or points_to_convert % 100 != 0:
        raise ValueError("每次兑换积分必须为100的整数倍")

    user_points = get_or_create_user_points(db, user_id)
    if user_points.current_points < points_to_convert:
        raise ValueError("积分不足，无法发起工时兑换")

    hours_requested = (points_to_convert / 100) * 0.5

    user_points.current_points -= points_to_convert

    req = models.VolunteerHourRequest(
        user_id=user_id,
        points_spent=points_to_convert,
        hours_requested=hours_requested,
        status="pending_school_review"
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    return req


def get_volunteer_overview(db: Session, user_id: int):
    stats = get_user_stats(db, user_id)
    convertible_hours = round((stats["current_points"] // 100) * 0.5, 1)
    consumed_points = max(0, stats["total_points"] - stats["current_points"])
    return {
        "current_points": stats["current_points"],
        "total_points": stats["total_points"],
        "consumed_points": consumed_points,
        "total_classifications": stats["total_classifications"],
        "convertible_hours": convertible_hours,
        "conversion_ratio": "每100积分可申请0.5小时志愿工时"
    }


def _title_by_score(score: int):
    if score < 30:
        return "环保萌新"
    if score < 120:
        return "红果园卫士"
    return "知行环保大师"


def get_leaderboard_data(db: Session, board_type: str = "personal"):
    board_type = "dormitory" if board_type == "dormitory" else "personal"

    if board_type == "personal":
        rows = db.query(
            models.User.id,
            models.User.username,
            func.coalesce(func.count(models.ClassificationRecord.id), 0).label("score")
        ).outerjoin(
            models.ClassificationRecord,
            models.User.id == models.ClassificationRecord.user_id
        ).group_by(models.User.id, models.User.username).order_by(func.coalesce(func.count(models.ClassificationRecord.id), 0).desc()).limit(20).all()

        entries = []
        for idx, row in enumerate(rows, start=1):
            badge = "北交环保之星" if idx <= 3 else None
            entries.append({
                "rank": idx,
                "name": row.username,
                "score": int(row.score),
                "title": _title_by_score(int(row.score)),
                "is_top_three": idx <= 3,
                "badge": badge
            })
        return {"board_type": "personal", "entries": entries}

    dorm_map = {}
    users = db.query(models.User.id, models.User.username).all()
    for u in users:
        dorm_name = f"{(u.id % 8) + 1}号楼-{(u.id % 6) + 101}寝室"
        if dorm_name not in dorm_map:
            dorm_map[dorm_name] = 0
        score = db.query(func.coalesce(func.count(models.ClassificationRecord.id), 0)).filter(models.ClassificationRecord.user_id == u.id).scalar()
        dorm_map[dorm_name] += int(score or 0)

    sorted_dorms = sorted(dorm_map.items(), key=lambda x: x[1], reverse=True)[:20]
    entries = []
    for idx, (dorm, score) in enumerate(sorted_dorms, start=1):
        badge = "北交环保之星" if idx <= 3 else None
        entries.append({
            "rank": idx,
            "name": dorm,
            "score": score,
            "title": _title_by_score(score),
            "is_top_three": idx <= 3,
            "badge": badge
        })

    return {"board_type": "dormitory", "entries": entries}
