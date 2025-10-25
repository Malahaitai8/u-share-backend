from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import httpx

app = FastAPI(title="AI Chat Service", description="基于百度千帆的大模型聊天接口", version="0.1.0")

class QuestionRequest(BaseModel):
    question: str

ERROR_RESPONSE = {"error": "AI助手暂时无法回答，请稍后再试"}

API_KEY = os.getenv("QIANFAN_API_KEY", "bce-v3/ALTAK-8cwq50N5qIVACwFSWMlb0/28a24fba32868aede440b5ad625c033f6556aa42")

@app.post("/ask-ai")
async def ask_ai(request: QuestionRequest):
    """与千帆大模型对话，返回 AI 回答"""
    api_key = API_KEY
    if not api_key:
        return JSONResponse(status_code=500, content=ERROR_RESPONSE)

    chat_url = "https://qianfan.baidubce.com/v2/chat/completions"
    system_prompt = (
        "你是一个专业的垃圾分类指导助手，请根据用户的问题，准确地回答垃圾如何分类。如果问题与垃圾分类无关，请礼貌地拒绝回答。"
    )
    payload = {
        "model": "ernie-3.5-8k",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.question},
        ],
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(chat_url, headers=headers, json=payload)
            print("BAIDU_STATUS:", resp.status_code)
            print("BAIDU_BODY:", resp.text)
    except Exception:
        return JSONResponse(status_code=502, content=ERROR_RESPONSE)

    if resp.status_code != 200:
        return JSONResponse(status_code=502, content=ERROR_RESPONSE)

    try:
        data = resp.json()
        answer = data.get("result")
        if not answer and "choices" in data:
            answer = data["choices"][0]["message"]["content"]
    except Exception:
        answer = None
    if not answer:
        return JSONResponse(status_code=502, content=ERROR_RESPONSE)
    return {"answer": answer}
