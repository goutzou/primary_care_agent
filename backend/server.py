from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .agent import run_agent
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list
    stage: int

class ChatResponse(BaseModel):
    reply: str
    history: list
    stage: int

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    reply, new_stage = run_agent(req.history, req.message, req.stage)
    req.history.append({"role": "assistant", "content": reply})
    
    return ChatResponse(
        reply=reply,
        history=req.history,
        stage=new_stage
    )
