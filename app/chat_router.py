from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import sys
import os
from typing import List, Dict
# from chat_services import Together_service
from chat_services import Gemini_services


router = APIRouter()
chat_service = Gemini_services()

# Lưu trữ session chat (trong production nên dùng Redis hoặc database)
chat_sessions: Dict[str, List[Dict]] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    chat_mode: str = "cv"  # cv, human_chat
    conversation_history: List[Dict] = []

class SuggestionsRequest(BaseModel):
    current_question: str
    chat_mode: str = "cv"

@router.post("/chat")
async def chat(chat_req: ChatRequest):
    try:
        # Lấy hoặc tạo session
        session_id = chat_req.session_id
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
        
        # Thêm tin nhắn người dùng vào lịch sử
        user_message = {"role": "user", "content": chat_req.message}
        chat_sessions[session_id].append(user_message)
        
        # Giới hạn bộ nhớ ngắn hạn (10 tin nhắn gần nhất)
        recent_history = chat_sessions[session_id][-10:]
        
        # Lấy câu trả lời từ AI
        answer = chat_service.get_ans(
            user_input=chat_req.message,
            chat_mode=chat_req.chat_mode,
            conversation_history=recent_history
        )
        
        # Thêm câu trả lời vào lịch sử
        assistant_message = {"role": "assistant", "content": answer}
        chat_sessions[session_id].append(assistant_message)
        
        return {
            "answer": answer,
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggestions")
async def get_suggestions(req: SuggestionsRequest):
    try:
        suggestions = chat_service.generate_suggestions(
            current_question=req.current_question,
            chat_mode=req.chat_mode
        )
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-session")
async def clear_session(request: Request):
    data = await request.json()
    session_id = data.get("session_id", "default")
    if session_id in chat_sessions:
        chat_sessions[session_id] = []
    return {"message": "Session cleared"}

