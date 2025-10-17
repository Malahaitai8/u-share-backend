from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import time
import base64
import asyncio
import requests
from dotenv import load_dotenv

load_dotenv()

BAIDU_API_KEY = os.getenv("BAIDU_API_KEY")
BAIDU_SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")
TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
# 使用标准 REST 接口，比 pro_api 权限要求低，避免 3302 无权限错误
ASR_URL = "http://vop.baidu.com/server_api"

app = FastAPI(title="NLP Service", description="语音识别 & 文本分类（Mock）", version="0.1.0")

auth_cache = {"token": None, "expire_at": 0.0}

async def get_baidu_token() -> str:
    """获取或复用百度 access_token"""
    if not BAIDU_API_KEY or not BAIDU_SECRET_KEY:
        raise HTTPException(status_code=500, detail="百度语音 API Key 未配置")
    # 提前 60 秒刷新
    if auth_cache["token"] and time.time() < auth_cache["expire_at"] - 60:
        return auth_cache["token"]

    def _request_token():
        params = {
            "grant_type": "client_credentials",
            "client_id": BAIDU_API_KEY,
            "client_secret": BAIDU_SECRET_KEY,
        }
        resp = requests.post(TOKEN_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if "access_token" not in data:
            raise RuntimeError(f"获取百度token失败: {data}")
        return data

    try:
        data = await asyncio.to_thread(_request_token)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    auth_cache["token"] = data["access_token"]
    auth_cache["expire_at"] = time.time() + int(data.get("expires_in", 0))
    return auth_cache["token"]

class TextInput(BaseModel):
    text: str

# ------- 垃圾分类（示例规则） --------------------------------------------------
# 真实项目可替换为数据库 / 模型查询，这里用简单关键词映射和模糊匹配演示
_CATEGORY_RULES = {
    "可回收物": ["瓶", "易拉罐", "塑料", "玻璃", "纸", "金属"],
    "厨余垃圾": ["剩饭", "菜叶", "果皮", "蛋壳", "茶叶"],
    "有害垃圾": ["电池", "灯管", "油漆", "药品"],
    "其他垃圾": [],  # 兜底
}

def classify_text(text: str) -> str:
    """根据关键词做简单垃圾分类，返回类别字符串"""
    text = text.strip().lower()
    for category, keywords in _CATEGORY_RULES.items():
        for kw in keywords:
            if kw in text:
                return category
    return "其他垃圾"

@app.post("/recognize/voice")
async def recognize_voice(file: UploadFile = File(...)):
    """调用百度 ASR 进行语音识别"""
    try:
        audio_bytes = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="读取音频文件失败")

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="文件内容为空")

    token = await get_baidu_token()

    speech_base64 = base64.b64encode(audio_bytes).decode()
    payload = {
        "format": file.filename.split('.')[-1],
        "rate": 16000,
        "dev_pid": 1537,  # 普通话
        "speech": speech_base64,
        "len": len(audio_bytes),
        "channel": 1,
        "token": token,
        "cuid": "nlp_service_demo",
    }

    def _call_asr():
        resp = requests.post(ASR_URL, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()

    try:
        result = await asyncio.to_thread(_call_asr)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"百度ASR接口调用失败: {e}")

    if result.get("err_no", 0) != 0:
        raise HTTPException(status_code=502, detail=f"识别失败: {result}")

    text = "".join(result.get("result", []))
    category = classify_text(text)
    return {"result": text, "category": category}

@app.post("/recognize/text")
async def recognize_text(body: TextInput):
    """Mock 文本分类接口"""
    category = classify_text(body.text)
    return {"input_text": body.text, "category": category}
