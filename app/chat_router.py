from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import sys
import os
from chat_services import Together_service


router = APIRouter()
chat_service = Together_service()

@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_quest = data.get("message")
    answer = chat_service.get_ans(user_quest)
    return {"answer": answer}

