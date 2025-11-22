import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_llm_response(history_messages: list, user_message: str, context_text: str = "") -> str:
    """
    1. Constructs System Prompt (Slide 16)
    2. Appends Context (RAG)
    3. Calls Gemini
    """
    
    system_instruction = "You are a helpful corporate assistant named BOT GPT."
    
    if context_text:
        system_instruction += f"\n\nCONTEXT FROM DOCUMENTS:\n{context_text}\n\nAnswer based ONLY on the context above."

    gemini_history = []
    for msg in history_messages:
        role = "user" if msg.sent_by == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg.text]})

    gemini_history = gemini_history[-10:]

    chat = model.start_chat(history=gemini_history)
    
    full_prompt = f"{system_instruction}\n\nUser: {user_message}" if context_text else user_message
    
    try:
        response = chat.send_message(full_prompt)
        return response.text
    except Exception as e:
        return f"I encountered an error processing your request: {str(e)}"