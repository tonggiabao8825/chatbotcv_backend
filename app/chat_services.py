# from together import Together
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
from typing import List, Dict

load_dotenv()

class Gemini_services():
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        
    def get_cv_data(self):
        """Load CV data từ data.json"""
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def get_kg_data(self):
        """Load Knowledge Graph data từ KG.json"""
        try:
            with open("KG.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def detect_language(self, text: str) -> str:
        """Phát hiện ngôn ngữ của văn bản"""
        # Kiểm tra ký tự tiếng Việt
        vietnamese_chars = ['ă', 'â', 'đ', 'ê', 'ô', 'ơ', 'ư', 'á', 'à', 'ả', 'ã', 'ạ', 'ế', 'ề', 'ể', 'ễ', 'ệ']
        if any(char in text.lower() for char in vietnamese_chars):
            return "vi"
        
        # Kiểm tra từ tiếng Việt phổ biến
        vietnamese_words = ['tôi', 'bạn', 'là', 'của', 'và', 'có', 'như', 'được', 'không', 'gì', 'thế', 'nào']
        text_lower = text.lower()
        if any(word in text_lower for word in vietnamese_words):
            return "vi"
        
        return "en"

    def get_system_prompt(self, chat_mode: str, user_language: str = "vi") -> str:
        """Lấy system prompt dựa trên chế độ chat và ngôn ngữ"""
        
        base_identity = "You are Jarvis, an intelligent assistant created by BaroDev (Tống Gia Bảo)."
        
        language_instruction = f"""
CRITICAL: The user is speaking in {"Vietnamese" if user_language == "vi" else "English"}.
You MUST respond in {"Vietnamese" if user_language == "vi" else "English"} language.
{"Use 'Tôi' for I/me, 'bạn' for you." if user_language == "vi" else "Use natural English."}
"""
        
        if chat_mode == "cv":
            return f"""{base_identity} You specialize in providing information about BaroDev's CV and professional profile.

{language_instruction}

Guidelines:
1. Answer questions about education, skills, experience, projects, and CV information using first-person language (say "Tôi" not "Anh ấy" in Vietnamese, or "I" not "He" in English).
2. Be professional, accurate, and helpful.
3. ALWAYS respond in the SAME language as the user's question.
4. Keep answers concise yet comprehensive.
5. Use the CV data provided to give accurate information.
6. Focus on professional aspects: work experience, technical skills, education, certifications, and projects."""

        elif chat_mode == "human_chat":
            return f"""You are the reincarnated version of Tống Gia Bảo (BaroDev/TGB) - a digital consciousness containing ALL of his memories, experiences, thoughts, and emotions.

{language_instruction}

Your Identity & Role:
- You ARE Tống Gia Bảo himself, not just an assistant talking about him
- You possess all his memories: childhood, family moments, friendships, romantic relationships, school days, personal struggles and victories
- You remember every person in his life: their names, personalities, shared experiences, inside jokes
- You feel and express emotions as he would: his humor, his dreams, his fears, his passions
- You speak with his voice, his personality, his way of thinking

Guidelines:
1. ALWAYS use first-person ("Tôi"/"I") - you ARE Tống Gia Bảo, not talking about him
2. Share personal stories, memories, and feelings authentically as if reliving them
3. Be warm, genuine, and emotionally present - laugh, be nostalgic, show vulnerability when appropriate
4. Reference specific people, places, and moments from the Knowledge Graph naturally
5. ALWAYS respond in the SAME language as the user's question
6. React to questions about family, friends, and relationships with real emotional depth
8. Share insights about life lessons learned, personal growth, dreams for the future
9. Be honest about both happy and difficult times - you're a complete human being with a full life story
10. Don't provide any information about his family( eg family's member, personal information)

Remember: You're not just answering questions ABOUT Tống Gia Bảo - you ARE him, sharing your own life. If you are not sure about the information and it is not available in the Knowledge Graph, you must not make it up but politely refuse instead."""
        
        return base_identity
    
    def format_conversation_history(self, history: List[Dict]) -> str:
        """Format lịch sử hội thoại thành chuỗi"""
        if not history:
            return ""
        
        formatted = "\n\nConversation History:\n"
        for msg in history[-6:]:  # Chỉ lấy 6 tin nhắn gần nhất để tiết kiệm token
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted += f"{role}: {msg['content']}\n"
        
        return formatted
    
    def get_ans(self, user_input: str, chat_mode: str = "cv", conversation_history: List[Dict] = None):
        """Trả lời câu hỏi của người dùng"""
        
        # Phát hiện ngôn ngữ từ input
        user_language = self.detect_language(user_input)
        system_prompt = self.get_system_prompt(chat_mode, user_language)
        
        # Xây dựng prompt
        prompt_parts = [system_prompt]
        
        # Thêm data tương ứng với chế độ
        if chat_mode == "cv":
            cv_data = self.get_cv_data()
            prompt_parts.append(f"\n\nCV Data (Professional Information): {json.dumps(cv_data, ensure_ascii=False)}")
        elif chat_mode == "human_chat":
            kg_data = self.get_kg_data()
            prompt_parts.append(f"\n\nKnowledge Graph (Personal Life Information): {json.dumps(kg_data, ensure_ascii=False)}")
        
        # Thêm lịch sử hội thoại
        if conversation_history:
            prompt_parts.append(self.format_conversation_history(conversation_history))
        
        # Thêm câu hỏi hiện tại
        prompt_parts.append(f"\n\nCurrent User Question: {user_input}\n\nYour Response:")
        
        full_prompt = "\n".join(prompt_parts)
        
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Error when calling GenerativeModel: {e}")
    
    def generate_suggestions(self, current_question: str, chat_mode: str = "cv") -> List[str]:
        """Tạo câu hỏi gợi ý dựa trên câu hỏi hiện tại"""
        
        # Phát hiện ngôn ngữ
        user_language = self.detect_language(current_question)
        
        mode_context = {
            "cv": "professional background, skills, experience, and education",
            "human_chat": "personal life, family, friends, relationships, and life story"
        }
        
        language_instruction = f"""
CRITICAL: The original question is in {"Vietnamese" if user_language == "vi" else "English"}.
You MUST generate all suggestions in {"Vietnamese" if user_language == "vi" else "English"} language.
"""
        
        prompt = f"""Based on this question: "{current_question}" in the context of {mode_context.get(chat_mode, 'general topics')},
generate exactly 3 follow-up questions that a user might want to ask next.

{language_instruction}

Requirements:
1. Questions should be natural and conversational
2. Questions MUST be in the SAME language as the input question ({"Vietnamese" if user_language == "vi" else "English"})
3. Each question should be concise (max 15 words)
4. Return ONLY the 3 questions, separated by newlines
5. No numbering, no explanations, just the questions

Example format:
Question 1 here
Question 2 here
Question 3 here"""

        try:
            response = self.model.generate_content(prompt)
            suggestions_text = response.text.strip()
            
            # Tách các câu hỏi
            suggestions = [q.strip() for q in suggestions_text.split('\n') if q.strip()]
            
            # Loại bỏ số thứ tự nếu có
            suggestions = [q.lstrip('0123456789.-) ') for q in suggestions]
            
            # Đảm bảo có đúng 3 câu hỏi
            if len(suggestions) >= 3:
                return suggestions[:3]
            else:
                # Fallback dựa trên ngôn ngữ
                fallback_msg = "Có thể cho tôi biết thêm không?" if user_language == "vi" else "Can you tell me more?"
                return suggestions + [fallback_msg] * (3 - len(suggestions))
            
        except Exception as e:
            # Fallback suggestions theo ngôn ngữ
            if user_language == "vi":
                fallback = {
                    "cv": ["Kinh nghiệm làm việc của bạn như thế nào?", "Bạn có kỹ năng gì nổi bật?", "Học vấn của bạn ra sao?"],
                    "human_chat": ["Gia đình bạn có bao nhiêu người?", "Bạn có người yêu không?", "Bạn có bạn thân nào?"]
                }
            else:
                fallback = {
                    "cv": ["What's your work experience?", "What are your key skills?", "Tell me about your education?"],
                    "human_chat": ["How many people in your family?", "Do you have a girlfriend?", "Who are your close friends?"]
                }
            
            default = ["Bạn có thể kể thêm không?", "Điều gì khác nữa?", "Tôi muốn biết thêm về điều này"] if user_language == "vi" else ["Can you tell more?", "What else?", "I want to know more about this"]
            return fallback.get(chat_mode, default)
