from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

import httpx
from pydantic import BaseModel
from typing import Optional
import os
import time
import base64
import asyncio
import requests
from dotenv import load_dotenv
import tempfile
import logging
from pydub import AudioSegment

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def convert_audio_to_wav(audio_bytes: bytes, source_format: str) -> tuple[bytes, int]:
    """
    将音频转换为 WAV 格式（百度 ASR 支持的格式）
    返回: (wav_bytes, sample_rate)
    """
    temp_input = None
    temp_output = None
    
    try:
        # 创建临时文件保存原始音频
        with tempfile.NamedTemporaryFile(suffix=f'.{source_format}', delete=False) as tmp_input:
            tmp_input.write(audio_bytes)
            temp_input = tmp_input.name
        
        # 加载音频（pydub会自动检测格式）
        logger.info(f"正在转换音频格式: {source_format} -> wav")
        audio = AudioSegment.from_file(temp_input, format=source_format)
        
        # 设置参数：单声道，16kHz采样率，16位深度
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        audio = audio.set_sample_width(2)  # 16位 = 2字节
        
        # 导出为 WAV
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_output:
            temp_output = tmp_output.name
        
        audio.export(temp_output, format='wav')
        
        # 读取转换后的 WAV 文件
        with open(temp_output, 'rb') as f:
            wav_bytes = f.read()
        
        logger.info(f"音频转换成功: 原始大小={len(audio_bytes)}, WAV大小={len(wav_bytes)}")
        return wav_bytes, 16000
        
    except Exception as e:
        logger.error(f"音频转换失败: {e}")
        raise HTTPException(status_code=400, detail=f"音频格式转换失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if temp_input and os.path.exists(temp_input):
            try:
                os.unlink(temp_input)
            except Exception as e:
                logger.warning(f"清理临时文件失败: {e}")
        if temp_output and os.path.exists(temp_output):
            try:
                os.unlink(temp_output)
            except Exception as e:
                logger.warning(f"清理临时文件失败: {e}")


@app.post("/recognize/voice")
async def recognize_voice(file: UploadFile = File(...)):
    """调用百度 ASR 进行语音识别，支持多种音频格式"""
    try:
        audio_bytes = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="读取音频文件失败")

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="文件内容为空")

    # 获取文件格式
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else 'webm'
    content_type = file.content_type or ''
    
    logger.info(f"收到音频文件: filename={file.filename}, content_type={content_type}, size={len(audio_bytes)}")
    
    # 确定音频格式
    if 'webm' in content_type or file_extension == 'webm':
        source_format = 'webm'
    elif 'ogg' in content_type or file_extension == 'ogg':
        source_format = 'ogg'
    elif 'mp3' in content_type or file_extension == 'mp3':
        source_format = 'mp3'
    elif 'wav' in content_type or file_extension == 'wav':
        source_format = 'wav'
    elif 'mp4' in content_type or file_extension in ['m4a', 'mp4']:
        source_format = 'mp4'
    else:
        source_format = file_extension
    
    # 百度 ASR 支持的格式: pcm, wav, amr, m4a
    # 如果是 webm, ogg, mp3 等格式，需要转换为 wav
    need_conversion = source_format in ['webm', 'ogg', 'mp3', 'opus']
    
    if need_conversion:
        logger.info(f"检测到 {source_format} 格式，需要转换为 WAV")
        audio_bytes, sample_rate = convert_audio_to_wav(audio_bytes, source_format)
        format_for_baidu = 'wav'
    else:
        format_for_baidu = source_format
        sample_rate = 16000  # 默认采样率

    token = await get_baidu_token()

    speech_base64 = base64.b64encode(audio_bytes).decode()
    payload = {
        "format": format_for_baidu,
        "rate": sample_rate,
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
        logger.error(f"百度ASR调用失败: {e}")
        raise HTTPException(status_code=502, detail=f"百度ASR接口调用失败: {e}")

    if result.get("err_no", 0) != 0:
        error_msg = result.get("err_msg", "未知错误")
        logger.error(f"百度ASR识别失败: err_no={result.get('err_no')}, err_msg={error_msg}")
        raise HTTPException(status_code=502, detail=f"语音识别失败: {error_msg}")

    text = "".join(result.get("result", []))
    logger.info(f"识别成功: {text}")
    
    category = classify_text(text)
    return {"result": text, "category": category}

@app.post("/recognize/text")
async def recognize_text(body: TextInput):
    """Mock 文本分类接口"""
    category = classify_text(body.text)
    return {"input_text": body.text, "category": category}

# ----------------------------------------------------------------------------
#       大模型（百度千帆）问答接口
# ----------------------------------------------------------------------------

class QuestionRequest(BaseModel):
    question: str


@app.post("/ask-ai-direct")
async def ask_ai_direct_about_garbage(request: QuestionRequest):
    """调用百度千帆大模型进行垃圾分类问答"""

    # 1. 获取凭证
    ak = os.getenv("QIANFAN_AK")
    sk = os.getenv("QIANFAN_SK")
    if not ak or not sk:
        return JSONResponse(status_code=500, content={"error": "AI助手暂时无法回答，请稍后再试"})

    # 2. 获取 access_token
    token_url = "https://aip.baidubce.com/oauth/2.0/token"
    token_params = {
        "grant_type": "client_credentials",
        "client_id": ak,
        "client_secret": sk,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            token_resp = await client.post(token_url, params=token_params)
    except Exception:
        return JSONResponse(status_code=502, content={"error": "AI助手暂时无法回答，请稍后再试"})

    if token_resp.status_code != 200:
        return JSONResponse(status_code=502, content={"error": "AI助手暂时无法回答，请稍后再试"})

    try:
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
    except Exception:
        access_token = None

    if not access_token:
        return JSONResponse(status_code=502, content={"error": "AI助手暂时无法回答，请稍后再试"})

    # 3. 调用聊天 API
    chat_url = f"https://qianfan.baidubce.com/v2/chat/completions?access_token={access_token}"
    system_prompt = "你是一个专业的垃圾分类指导助手，请根据用户的问题，准确地回答垃圾如何分类。如果问题与垃圾分类无关，请礼貌地拒绝回答。"

    payload = {
        "model": "ERNIE-Bot-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.question},
        ],
    }

    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            chat_resp = await client.post(chat_url, headers=headers, json=payload)
    except Exception:
        return JSONResponse(status_code=502, content={"error": "AI助手暂时无法回答，请稍后再试"})

    if chat_resp.status_code != 200:
        return JSONResponse(status_code=502, content={"error": "AI助手暂时无法回答，请稍后再试"})

    try:
        chat_json = chat_resp.json()
        # 尝试多种路径拿回答
        answer = chat_json.get("result")
        if not answer and "choices" in chat_json:
            answer = chat_json["choices"][0]["message"]["content"]
    except Exception:
        answer = None

    if not answer:
        return JSONResponse(status_code=502, content={"error": "AI助手暂时无法回答，请稍后再试"})

    # 成功
    return {"answer": answer}

# -----------------------------------------------------------------------------
#                      诊断 / 健康检查接口
# -----------------------------------------------------------------------------

@app.get("/diagnose")
async def diagnose_service():
    """一次性检查常见的依赖与外部连通性。

    返回示例::
        {
            "baidu_token": "ok",          # 或 token_error / timeout
            "ffmpeg": "6.1.0",            # 版本号，或 not_found
        }
    """

    # 1. 检查百度鉴权
    try:
        _ = await get_baidu_token()
        token_status = "ok"
    except HTTPException as he:
        token_status = f"token_error: {he.detail}"
    except Exception as e:
        token_status = f"token_error: {str(e)}"

    # 2. 检查 ffmpeg 是否存在
    import shutil, subprocess

    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg", "-version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            first_line = stdout.decode(errors="ignore").split("\n", 1)[0]
            ffmpeg_status = first_line.strip()
        except Exception as e:
            ffmpeg_status = f"ffmpeg_error: {e}"
    else:
        ffmpeg_status = "not_found"

    return {
        "baidu_token": token_status,
        "ffmpeg": ffmpeg_status,
    }
