from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List
import os
import httpx

app = FastAPI(title="AI Chat Service", description="基于百度千帆的大模型聊天接口", version="0.1.0")

class QuestionRequest(BaseModel):
    question: str = Field(..., description="用户提问内容")
    conversation_id: str | None = Field(None, description="同一次对话传同一个ID，可衔接上下文")

ERROR_RESPONSE = {"error": "AI助手暂时无法回答，请稍后再试"}

# 简单内存会话存储: {conv_id: [message_dict, ...]}
_sessions: Dict[str, List[dict]] = {}

API_KEY = os.getenv("QIANFAN_API_KEY", "bce-v3/ALTAK-8cwq50N5qIVACwFSWMlb0/28a24fba32868aede440b5ad625c033f6556aa42")

@app.post("/ask-ai")
async def ask_ai(request: QuestionRequest):
    """与千帆大模型对话，返回 AI 回答"""
    api_key = API_KEY
    if not api_key:
        return JSONResponse(status_code=500, content=ERROR_RESPONSE)

    chat_url = "https://qianfan.baidubce.com/v2/chat/completions"
    system_prompt = (
        "你是一名严谨且友好的垃圾分类指导助手，只回答垃圾分类相关内容。请在回答中：1) 判断或说明垃圾所属类别；2) 给出具体的处理或回收建议；3) 以积极口吻鼓励用户坚持垃圾分类。若用户提问与垃圾分类无关，礼貌回复：‘很抱歉，我只能回答垃圾分类相关的问题。’  回复控制在 150 字以内。"
    )
    conv_id = request.conversation_id or "default"
    history = _sessions.get(conv_id, [])

    messages = [{"role": "system", "content": system_prompt}] + history + [
        {"role": "user", "content": request.question}
    ]

    payload = {
        "model": "ernie-3.5-8k",
        "messages": messages,
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

    # 更新会话历史，只保留最近 20 条，排除最前面的 system_prompt
    new_history = history + [
        {"role": "user", "content": request.question},
        {"role": "assistant", "content": answer},
    ]
    _sessions[conv_id] = new_history[-20:]

    return {"answer": answer}
