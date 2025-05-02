from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from chat_router import router as chat_router

app = FastAPI(
    title="BaroDev Chat API",
    description="CV chatbot",
    version="1.0.0"
)

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  
    allow_headers=["*"],  
)

app.include_router(chat_router)

@app.get("/")
async def root():
    return {
        "Conn is ok"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000)) 
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)



