# Chatbot CV Backend

Backend for a personal CV chatbot that answers questions about my professional profile and personal background.

## Tech Stack
- Python 3.9+
- FastAPI (API Framework)
- Google Gemini 2.0 Flash (LLM)
- ChromaDB (Vector Database)
- NetworkX (Knowledge Graph)

## Features
1. RAG (Retrieval-Augmented Generation)
   - Uses ChromaDB to store and retrieve CV information.
   - Embeds text using `sentence-transformers/all-MiniLM-L6-v2`.

2. Semantic Knowledge Graph
   - Combines NetworkX with Vector Search.
   - Allows querying personal relationships using natural language (e.g., finding connections without exact names).

3. AI Guardrail
   - Basic filter to block sensitive or harmful keywords before processing.

4. Hallucination Prevention
   - Stops execution if no relevant context is found in the database, preventing the AI from fabricating answers.

## Installation

1. Install dependencies:
   pip install -r requirements.txt

2. Configure Environment:
   Create a `.env` file and add your API key:
   GEMINI_API_KEY=your_api_key_here

3. Run the server:
   python -m uvicorn main:app --reload

## API Endpoints
- POST /chat: Main chat endpoint (CV Mode & Human Mode).
- POST /suggestions: Generates follow-up questions.
- POST /clear-session: Clears chat history.

## Project Structure
- `main.py`: Entry point and server configuration.
- `chat_router.py`: API route definitions.
- `chat_services.py`: Business logic and LLM integration.
- `rag_services.py`: Data retrieval logic (VectorDB & Graph).
- `data.json`: CV data source.
- `KG.json`: Knowledge Graph data source.
