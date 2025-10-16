from fastapi import FastAPI, Body
from pydantic import BaseModel
from chatbot import create_bot

app = FastAPI(title="DeepSeek 知识问答机器人（热加载+记忆+bge-m3+人设）", version="0.1.0")

# 初始化机器人
client, bot = None, None

@app.on_event("startup")
def startup_event():
    global bot
    bot = create_bot()

class WechatRequest(BaseModel):
    text: str
    session_id: str = "default"

@app.post("/wechat", summary="Wechat Reply")
def wechat_reply(req: WechatRequest):
    global bot
    if not bot:
        bot = create_bot()
    reply = bot.ask(req.text, session_id=req.session_id)
    return {"reply": reply}

@app.get("/health", summary="Health")
def health():
    return {"status": "ok"}
