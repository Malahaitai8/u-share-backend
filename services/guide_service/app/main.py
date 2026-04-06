from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import os, httpx
import re
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="Garbage Guide Service", description="垃圾投放引导后端", version="0.1.0")

# 允许所有来源跨域，生产环境可限定具体域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AMAP_KEY = os.getenv("AMAP_API_KEY", "YOUR_AMAP_KEY")

# ------------------- 工具函数 ----------------------
from math import radians, sin, cos, sqrt, atan2


def _haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """计算两坐标间球面距离（米）"""
    R = 6371000.0  # 地球半径
    dlon = radians(lon2 - lon1)
    dlat = radians(lat2 - lat1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def _format_duration(seconds: int) -> str:
    """将秒转换为友好的时间显示格式"""
    if seconds < 60:
        return f"{seconds}秒"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if remaining_seconds == 0:
        return f"{minutes}分钟"
    else:
        return f"{minutes}分{remaining_seconds}秒"


def _build_bin_description(bin_types: dict) -> str:
    """根据垃圾桶类型生成描述（B风格：说明式）"""
    categories = []
    for cat in ["可回收", "厨余", "有害", "其他"]:
        count = bin_types.get(cat, 0)
        if count and count > 0:
            categories.append(cat)
    
    if not categories:
        return "无分类垃圾桶"
    
    if len(categories) >= 4:
        return "配有可回收、厨余、有害、其他垃圾桶"
    
    return "配有" + "、".join(categories) + "垃圾桶"

# ---------------- 加载 CSV / Excel 站点数据 --------------------
from pathlib import Path
import csv, pandas as pd

# 支持通过环境变量自定义路径
_default_xlsx = Path("/code/data/dustbins_with_types.xlsx")
env_path = os.getenv("DUSTBIN_CSV")
if env_path:
    DATA_PATH = Path(env_path)
else:
    DATA_PATH = _default_xlsx

# 正则与 _coord_to_decimal 定义（保持已存在代码）


def _coord_to_decimal(coord_str: str | float | int) -> float | None:
    """将经纬度字符串或数字转换为十进制度数
    优先处理十进制格式（表格中常用的格式）
    支持格式：
    1. 数字类型：直接返回（最常用）
    2. 十进制度数格式（字符串）："116.395645" 
    3. 度分秒格式：116°23′45″ 或 116°23′（兼容格式）
    """
    if coord_str is None:
        return None
    
    # 如果是数字类型，直接返回（最常见的情况）
    if isinstance(coord_str, (int, float)):
        return float(coord_str)
    
    # 转换为字符串
    coord_str = str(coord_str).strip()
    if not coord_str:
        return None
    
    # 优先尝试解析为十进制度数（表格中通常是这种格式）
    try:
        decimal = float(coord_str)
        return decimal
    except (ValueError, TypeError):
        pass
    
    # 如果十进制解析失败，尝试解析度分秒格式（兼容旧数据）
    # 度分秒格式：116°23′45″
    match = re.search(r"(\d{2,3})°(\d{2,3})′(\d{2,3})″", coord_str)
    if match:
        degrees = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        decimal = degrees + minutes / 60 + seconds / 3600
        return decimal
    
    # 度分格式：116°23′
    match = re.search(r"(\d{2,3})°(\d{2,3})′", coord_str)
    if match:
        degrees = int(match.group(1))
        minutes = int(match.group(2))
        decimal = degrees + minutes / 60
        return decimal
    
    # 如果都解析失败，返回None
    return None


def _load_dustbins() -> list[dict]:
    if not DATA_PATH.exists():
        logger.warning(f"数据文件不存在: {DATA_PATH}")
        return []
    
    logger.info(f"正在加载站点数据从: {DATA_PATH}")
    
    try:
        records = pd.read_excel(DATA_PATH).to_dict(orient="records")
    except Exception as e:
        logger.error(f"读取数据文件失败: {e}")
        return []

    bins: list[dict] = []
    skipped_count = 0
    
    for idx, row in enumerate(records):
        lng_raw = row.get("经度") or row.get("lng") or row.get("longitude")
        lat_raw = row.get("纬度") or row.get("lat") or row.get("latitude")
        
        lng = _coord_to_decimal(lng_raw)
        lat = _coord_to_decimal(lat_raw)
        
        if lng is not None and lat is not None and abs(lng) < abs(lat):
            lng, lat = lat, lng
        
        if lng is None or lat is None:
            skipped_count += 1
            continue
        
        name = row.get("站点名称") or row.get("name") or f"站点{len(bins)+1}"
        
        def safe_int(val):
            if val is None:
                return 0
            try:
                if pd.isna(val):
                    return 0
                return int(val)
            except (ValueError, TypeError):
                return 0

        bin_types = {
            "其他": safe_int(row.get("其他")),
            "可回收": safe_int(row.get("可回收")),
            "厨余": safe_int(row.get("厨余")),
            "有害": safe_int(row.get("有害")),
        }
        description = _build_bin_description(bin_types)
        
        bins.append({
            "name": name,
            "lng": lng,
            "lat": lat,
            "bin_types": bin_types,
            "description": description,
        })
    
    logger.info(f"站点数据加载完成: 成功加载 {len(bins)} 个站点，跳过 {skipped_count} 条无效记录")
    return bins


_DUSTBINS = _load_dustbins()

class Dustbin(BaseModel):
    name: str
    lng: float
    lat: float
    bin_types: dict
    description: str

@app.get("/dustbins", response_model=list[Dustbin])
async def list_dustbins():
    """返回校园内所有垃圾桶坐标(示例数据)"""
    return _DUSTBINS

class RouteResp(BaseModel):
    nearby: bool = Field(..., description="是否近距离无需导航")
    message: str | None = Field(None, description="提示信息")
    distance: float | None = Field(None, description="步行距离(米)")
    duration: int | None = Field(None, description="步行耗时(秒)")
    dustbin: Dustbin
    nav_url: str | None = Field(None, description="H5导航链接")
    deeplink: str | None = Field(None, description="高德App deeplink")

@app.get("/nearest", response_model=RouteResp)
async def nearest_dustbin(lng: float = Query(...), lat: float = Query(...)):
    """根据用户坐标，返回最近垃圾桶及步行距离时间"""
    logger.info(f"NEAREST called lng={lng} lat={lat} bins={len(_DUSTBINS)} key={'set' if AMAP_KEY!='YOUR_AMAP_KEY' else 'none'}")

    if not _DUSTBINS:
        raise HTTPException(status_code=500, detail="无可用垃圾桶数据")

    # 计算所有站点的直线距离并排序
    candidates = sorted(
        (
            (_haversine(lng, lat, db["lng"], db["lat"]), db)
            for db in _DUSTBINS
        ),
        key=lambda x: x[0],
    )

    # 获取最近的垃圾桶
    nearest_dist, nearest_db = candidates[0]
    logger.info(f"NEAREST_BIN name={nearest_db['name']} straight_dist={round(nearest_dist, 1)}m")

    # 如果直线距离小于10米，直接返回，不调用高德API
    if nearest_dist < 10:
        logger.info(f"NEARBY <10m, skip API call")
        return {
            "nearby": True,
            "message": f"您距离垃圾站「{nearest_db['name']}」不到10米，请就近投放",
            "distance": round(nearest_dist, 1),
            "duration": None,
            "dustbin": nearest_db,
            "nav_url": None,
            "deeplink": None,
        }

    # 距离>=10米，调用高德API获取步行路线（对前5个候选点）
    best = None
    if AMAP_KEY != "YOUR_AMAP_KEY":
        logger.info(f"DISTANCE >=10m, calling Amap API for top 5 candidates")
        try:
            # 增加超时时间到10秒，避免Swagger调用时因网络稍慢而超时
            async with httpx.AsyncClient(timeout=10.0) as client:
                async def fetch(db):
                    url = (
                        "https://restapi.amap.com/v3/direction/walking"
                        f"?origin={lng},{lat}&destination={db['lng']},{db['lat']}&key={AMAP_KEY}"
                    )
                    try:
                        r = await client.get(url)
                        logger.info(f"AMAP_REQ to={db['name']} status={r.status_code}")
                        if r.status_code != 200:
                            logger.error(f"AMAP_ERROR status={r.status_code} body={r.text[:200]}")
                            return db, None
                        json_data = r.json()
                        if json_data.get("status") != "1":
                            logger.error(f"AMAP_API_ERROR to={db['name']} info={json_data.get('info')} infocode={json_data.get('infocode')}")
                        return db, json_data
                    except httpx.TimeoutException as e:
                        logger.error(f"AMAP_TIMEOUT to={db['name']} error={e}")
                        return db, None
                    except Exception as e:
                        logger.error(f"AMAP_REQUEST_ERROR to={db['name']} error={type(e).__name__}: {e}")
                        return db, None

                # 只对前5个候选调用API
                top5_candidates = candidates[:5]
                results = await asyncio.gather(*(fetch(db) for _, db in top5_candidates))

                for db, data in results:
                    if not data or data.get("status") != "1":
                        continue
                    try:
                        route = data["route"]["paths"][0]
                        dist = float(route["distance"])
                        dur = float(route["duration"])
                        logger.info(f"AMAP_SUCCESS to={db['name']} dist={dist}m dur={dur}s")
                        if best is None or dist < best[0]:
                            best = (dist, dur, db)
                    except (KeyError, IndexError, ValueError) as e:
                        logger.error(f"AMAP_PARSE_ERROR db={db['name']} error={e} data={data}")
                        continue
        except Exception as e:
            logger.error(f"AMAP_FAIL {type(e).__name__}: {e}", exc_info=True)
            best = None

    if best is None:
        # 无高德结果，返回最近垃圾桶的直线距离估算
        logger.warning(f"NO_AMAP_RESULT, fallback to nearest bin")
        return {
            "nearby": False,
            "message": f"最近垃圾桶：{nearest_db['name']}（约{round(nearest_dist, 1)}米），暂无法获取步行路线，请就近投放。",
            "distance": round(nearest_dist, 1),
            "duration": None,
            "dustbin": nearest_db,
            "nav_url": None,
            "deeplink": None,
        }

    # 获取到高德API的结果
    dist_m = round(best[0], 1)
    dur_s = int(best[1])
    db = best[2]
    
    # 格式化时间显示
    duration_text = _format_duration(dur_s)
    
    nav_url = f"https://uri.amap.com/navigation?to={db['lng']},{db['lat']},{db['name']}&mode=walk&src=u-share"
    deeplink = (
        f"amapuri://route/plan/?dlat={db['lat']}&dlon={db['lng']}"
        f"&dname={db['name']}&t=1&sourceApplication=u-share"
    )
    
    logger.info(f"RETURN_ROUTE to={db['name']} dist={dist_m}m dur={dur_s}s ({duration_text})")
    return {
        "nearby": False,
        "message": f"步行至「{db['name']}」约{dist_m}米，需时{duration_text}",
        "distance": dist_m,
        "duration": dur_s,
        "dustbin": db,
        "nav_url": nav_url,
        "deeplink": deeplink,
    }



