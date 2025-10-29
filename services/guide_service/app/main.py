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

# ---------------- 加载 CSV / Excel 站点数据 --------------------
from pathlib import Path
import csv, pandas as pd

# 支持通过环境变量自定义路径；若默认 CSV 不存在则尝试同名 .xlsx
_default_csv = Path("/code/data/dustbins.csv")
_default_xlsx = Path("/code/data/dustbins.xlsx")
env_path = os.getenv("DUSTBIN_CSV")
if env_path:
    DATA_PATH = Path(env_path)
else:
    DATA_PATH = _default_csv if _default_csv.exists() else _default_xlsx

# 正则与 _coord_to_decimal 定义（保持已存在代码）


def _coord_to_decimal(coord_str: str) -> float | None:
    """将经纬度字符串转换为十进制度数"""
    if not coord_str:
        return None
    match = re.search(r"(\d{2,3})°(\d{2,3})′(\d{2,3})″", coord_str)
    if match:
        degrees = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        decimal = degrees + minutes / 60 + seconds / 3600
        return decimal
    match = re.search(r"(\d{2,3})°(\d{2,3})′", coord_str)
    if match:
        degrees = int(match.group(1))
        minutes = int(match.group(2))
        decimal = degrees + minutes / 60
        return decimal
    match = re.search(r"(\d{2,3})°(\d{2,3})′(\d{2,3})″", coord_str)
    if match:
        degrees = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        decimal = degrees + minutes / 60 + seconds / 3600
        return decimal
    return None


def _load_dustbins() -> list[dict]:
    if not DATA_PATH.exists():
        return []
    # 读取文件
    if DATA_PATH.suffix.lower() == ".xlsx":
        records = pd.read_excel(DATA_PATH).to_dict(orient="records")
    else:
        with DATA_PATH.open("r", encoding="utf-8") as f:
            records = list(csv.DictReader(f))

    bins: list[dict] = []
    for row in records:
        lng = _coord_to_decimal(row.get("经度") or row.get("lng"))
        lat = _coord_to_decimal(row.get("纬度") or row.get("lat"))
        # 若经纬度疑似颠倒（经度应绝对值>纬度），自动交换
        if lng is not None and lat is not None and abs(lng) < abs(lat):
            lng, lat = lat, lng
        if lng is None or lat is None:
            continue
        bins.append({
            "name": row.get("站点名称") or row.get("name") or "未知站点",
            "lng": lng,
            "lat": lat,
        })
    return bins


_DUSTBINS = _load_dustbins()

class Dustbin(BaseModel):
    name: str
    lng: float
    lat: float

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

    # 预计算所有站点的直线距离并按升序取前5
    candidates = sorted(
        (
            (_haversine(lng, lat, db["lng"], db["lat"]), db)
            for db in _DUSTBINS
        ),
        key=lambda x: x[0],
    )[:5]

    best = None

    # 如果配置了高德 Key，则仅对前 5 个候选站点调用外部接口，减少耗时
    if AMAP_KEY != "YOUR_AMAP_KEY":
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                async def fetch(db):
                    url = (
                        "https://restapi.amap.com/v3/direction/walking"
                        f"?origin={lng},{lat}&destination={db['lng']},{db['lat']}&key={AMAP_KEY}"
                    )
                    try:
                        r = await client.get(url)
                        logger.info(f"AMAP_REQ {url} status={r.status_code}")
                        return db, r.json()
                    except Exception:
                        return db, None

                results = await asyncio.gather(*(fetch(db) for _, db in candidates))

                for db, data in results:
                    if not data or data.get("status") != "1":
                        continue
                    route = data["route"]["paths"][0]
                    dist = float(route["distance"])
                    dur = float(route["duration"])
                    if best is None or dist < best[0]:
                        best = (dist, dur, db)
        except Exception as e:
            logger.warning(f"AMAP_FAIL {e}")
            best = None

    if best is None:
        # 无高德结果，直接提示最近垃圾桶
        db = candidates[0][1]
        return {
            "nearby": False,
            "message": f"最近垃圾桶：{db['name']}，暂无法获取步行路线，请就近投放。",
            "dustbin": db,
        }

    dist_m = round(best[0], 1)
    dur_s = int(best[1])
    db = best[2]
    if dist_m <= 10:
        return {
            "nearby": True,
            "message": f"垃圾桶就在\"{db['name']}\"附近",
            "dustbin": db,
        }

    nav_url = f"https://uri.amap.com/navigation?to={db['lng']},{db['lat']},{db['name']}&mode=walk&src=ust-share"
    deeplink = (
        f"amapuri://route/plan/?dlat={db['lat']}&dlon={db['lng']}"
        f"&dname={db['name']}&t=1&sourceApplication=u-share"
    )
    return {
        "nearby": False,
        "distance": dist_m,
        "duration": dur_s,
        "dustbin": db,
        "nav_url": nav_url,
        "deeplink": deeplink,
    }



