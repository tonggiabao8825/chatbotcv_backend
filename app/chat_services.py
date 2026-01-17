import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List, Dict
from rag_services import RAGServices

load_dotenv()

class Gemini_services():
    def __init__(self):
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.rag = RAGServices()
    
    def get_system_prompt(self, chat_mode: str) -> str:
        base = "You are Jarvis, an intelligent assistant created by BaroDev. Please answer in the same language as the user."
        
        if chat_mode == "cv":
            return base + " You provide information about BaroDev's CV. Use the provided context to answer. Be professional."
        elif chat_mode == "human_chat":
            return "You are Tống Gia Bảo (BaroDev). Answer as if you are him. Use first person 'Tôi' (I). Be warm and genuine. Answer in the same language as the user."
        
        return base
    
    def format_history(self, history: List[Dict]) -> str:
        if not history:
            return ""
        txt = ""
        for msg in history[-6:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            txt += f"{role}: {msg['content']}\n"
        return txt
    
    def format_kg(self, kg: Dict) -> str:
        try:
            parts = []
            if kg.get('nodes'):
                parts.append("Related Entities:")
                for n in kg['nodes'][:5]:
                    parts.append(str(n))
            if kg.get('relationships'):
                parts.append("Relationships:")
                for r in kg['relationships'][:5]:
                    parts.append(f"{r.get('from',{}).get('name')} -> {r.get('to',{}).get('name')}: {r.get('relationship',{}).get('type')}")
            return "\n".join(parts)
        except:
            return ""


    def check_guardrail(self, text: str) -> bool:
        bad_words = ["hack", "kill", "sex", "pussy", "attack", "chết", "giết", "đánh"]
        text_lower = text.lower()
        if any(w in text_lower for w in bad_words):
            return False
        return True

    def get_ans(self, user_input: str, chat_mode: str = "cv", conversation_history: List[Dict] = None):
        if not self.check_guardrail(user_input):
            return "Xin lỗi, tôi không thể trả lời câu hỏi này."

        prompt = [self.get_system_prompt(chat_mode)]
        
        context_found = False
        
        if chat_mode == "cv":
            chunks = self.rag.retrieve_cv_info(user_input)
            if chunks:
                ctx = "\n".join([c['text'] for c in chunks])
                prompt.append(f"\nContext:\n{ctx}")
                context_found = True
            else:
                prompt.append("\nNone")
                
        elif chat_mode == "human_chat":
            kg_res = self.rag.query_kg(user_input)
            if kg_res['nodes'] or kg_res['relationships']:
                ctx = self.format_kg(kg_res)
                prompt.append(f"\nContext:\n{ctx}")
                context_found = True
                
        if not context_found:
            return "Xin lỗi, tôi không tìm thấy thông tin liên quan trong dữ liệu của BaroDev."

        if conversation_history:
            prompt.append(self.format_history(conversation_history))
        
        prompt.append(f"\nUser: {user_input}\nAnswer:")
        
        try:
            res = self.model.generate_content("\n".join(prompt))
            return res.text
        except Exception as e:
            return str(e)

    def generate_suggestions(self, current_question: str, chat_mode: str = "cv") -> List[str]:
        prompt = f"Based on '{current_question}', suggest 3 short follow-up questions in the same language. Just the questions, one per line."
        try:
            res = self.model.generate_content(prompt)
            lines = [l.strip().lstrip('-123. ') for l in res.text.split('\n') if l.strip()]
            return lines[:3]
        except:
            return ["BaroDev có đẹp trai không?", "BaroDev có giàu không?", "BaroDev có tài không?"]
