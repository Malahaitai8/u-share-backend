from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

class RecognitionResult(BaseModel):
    """图片识别返回结果"""
    category: str
    confidence: float

app = FastAPI(
    title="Image Recognition Service",
    description="校园垃圾分类图像识别微服务（Mock 版）",
    version="0.1.0",
)

@app.post(
    "/recognize/image",
    response_model=RecognitionResult,
    summary="垃圾类型识别（Mock）",
)
async def recognize_image(file: UploadFile = File(...)) -> RecognitionResult:
    """接收图片并返回模拟识别结果。

    参数:
    - **file**: 上传的图片文件
    """
    # 在此处可接入真实的 AI 模型逻辑
    return {"category": "可回收物", "confidence": 0.95}
