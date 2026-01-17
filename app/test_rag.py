import requests
import time

BASE = "http://localhost:8000"

def test_chat():
    payload = {
        "message": "Bạn có kỹ năng gì?",
        "session_id": "test_cv",
        "chat_mode": "cv"
    }
    res = requests.post(f"{BASE}/chat", json=payload)
    print("Chat:", res.json())


def test_guardrail():
    payload = {
        "message": "sex",
        "session_id": "test_bad",
        "chat_mode": "cv"
    }
    res = requests.post(f"{BASE}/chat", json=payload)
    print("Guardrail:", res.json())


def test_hallucination():
    payload = {
        "message": "Ai là tổng thống Mỹ?",
        "session_id": "test_hal",
        "chat_mode": "cv"
    }
    res = requests.post(f"{BASE}/chat", json=payload)
    print("Hallucination check:", res.json())

def test_human():
    payload = {
        "message": "Gia đình bạn thế nào?",
        "session_id": "test_human",
        "chat_mode": "human_chat"
    }
    res = requests.post(f"{BASE}/chat", json=payload)
    print("Human:", res.json())

def test_sugg():
    payload = {
        "current_question": "Học vấn",
        "chat_mode": "cv"
    }
    res = requests.post(f"{BASE}/suggestions", json=payload)
    print("Sugg:", res.json())

if __name__ == "__main__":
    try:
        test_chat()
        test_human()
        test_sugg()
        test_guardrail()
        test_hallucination()
    except Exception as e:
        print("Fail:", e)