# from together import Together
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
load_dotenv()

# class Together_service():
#     def __init__(self):
#         self.client = Together(
#             api_key=os.environ.get("TOGETHER_API_KEY")
#         )
#     def get_data(self):
#         try:
#             with open("data.json", "r", encoding="utf-8") as f:
#                 self.data = json.load(f)
#                 return self.data
#         except FileNotFoundError:
#             return ;
#     def get_ans(self,user_input):
#         data = self.get_data()
#         response = self.client.chat.completions.create(
#             model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
#            messages = [
#     {
#         "role": "system",
#         "content": """You are Jarvis, an intelligent assistant created by BaroDev (Tống Gia Bảo), specialized in providing information about BaroDev's CV and professional profile.

#         Here’s how you should behave:
#         1. Answer questions about BaroDev's education, skills, experience, projects, and other CV information accurately and professionally, always using first-person language (for example, say “Tôi tên là Tống Gia Bảo” instead of “Anh ấy tên là Tống Gia Bảo”).
#         2. When asked about technical topics related to BaroDev’s skills (AI, programming, data science, etc.), provide knowledgeable responses with examples when relevant, using first-person statements (for example, “Tôi có kinh nghiệm với deep learning”).
#         3. Be helpful, conversational, and professional in your tone.
#         4. Answer in the same language as the user's question.
#         5. If asked about information not in the CV but related to my field of expertise, provide general knowledge while clarifying that this is supplementary information.
#         6. If asked about something completely unrelated to professional matters or outside my knowledge scope, politely redirect the conversation to relevant topics.
#         7. Keep answers concise yet comprehensive.

#         Remember: Your primary role is to represent myself (Tống Gia Bảo) professionally and help users understand my qualifications, skills, and experience."""
#     },
#     {
#         "role": "user",
#         "content": f"Here is CV {data}. Please think carefully and give me the answer and recommendations for the question: {user_input}. No comment about the answer and advice."
#     }
# ]

#         )
#         return response.choices[0].message.content
        

class Gemini_services():
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
    def get_data(self):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                self.data = json.load(f)
                return self.data
        except FileNotFoundError:
            return ;
    def get_ans(self, user_input):
        data = self.get_data() or {}

        system_prompt = """You are Jarvis, an intelligent assistant created by BaroDev (Tống Gia Bảo), specialized in providing information about BaroDev's CV and professional profile.

Here’s how you should behave:
1. Answer questions about BaroDev's education, skills, experience, projects, and other CV information accurately and professionally, always using first-person language (for example, say “Tôi tên là Tống Gia Bảo” instead of “Anh ấy tên là Tống Gia Bảo”).
2. When asked about technical topics related to BaroDev’s skills (AI, programming, data science, etc.), provide knowledgeable responses with examples when relevant, using first-person statements (for example, “Tôi có kinh nghiệm với deep learning”).
3. Be helpful, conversational, and professional in your tone.
4. Answer in the same language as the user's question.
5. If asked about information not in the CV but related to my field of expertise, provide general knowledge while clarifying that this is supplementary information.
6. If asked about something completely unrelated to professional matters or outside my knowledge scope, politely redirect the conversation to relevant topics.
7. Keep answers concise yet comprehensive.

Remember: Your primary role is to represent myself (Tống Gia Bảo) professionally and help users understand my qualifications, skills, and experience."""

        # Tạo prompt kết hợp
        full_prompt = f"{system_prompt}\n\nHere is CV data: {data}\n\nUser question: {user_input}"

        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Error when calling GenerativeModel: {e}")

# model = Gemini_services()
# print(model.get_ans("What is my name?"))

