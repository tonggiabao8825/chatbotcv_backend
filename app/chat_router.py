from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict
from chat_services import Gemini_services

router = APIRouter()
chat_service = Gemini_services()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    chat_mode: str = "cv"
    conversation_history: List[Dict] = []

class SuggestionsRequest(BaseModel):
    current_question: str
    chat_mode: str = "cv"

@router.post("/chat")
async def chat(chat_req: ChatRequest):
    try:
        session_id = chat_req.session_id
        chat_sessions = chat_service.rag.get_session_history(session_id)
        
        user_message = {"role": "user", "content": chat_req.message}
        chat_sessions.append(user_message)
        
        recent_history = chat_sessions[-10:]
        
        answer = chat_service.get_ans(
            user_input=chat_req.message,
            chat_mode=chat_req.chat_mode,
            conversation_history=recent_history
        )
        
        assistant_message = {"role": "assistant", "content": answer}
        chat_sessions.append(assistant_message)
        
        chat_service.rag.save_session_history(session_id, chat_sessions)
        
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
    chat_service.rag.clear_session(session_id)
    return {"message": "Session cleared"}
