
# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from pydantic import BaseModel
# from chat import predict_intent
# from response_fetcher import get_response_by_tag
# from smart_chatbot_dynamic import WorkspaceChatbot

# from db import save_chat_to_db
# from langdetect import detect
# import uvicorn

# app = FastAPI(title="Chatbot API", description="Simple Chatbot with FastAPI")

# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")

# class ChatRequest(BaseModel):
#     message: str

# @app.get("/", response_class=HTMLResponse, tags=["Frontend"])
# async def chat_page(request: Request):
#     return templates.TemplateResponse("chat.html", {"request": request})

# @app.post("/api/chat", tags=["API"])
# async def chat_endpoint(chat_request: ChatRequest):
#     try:
#         user_message = chat_request.message
#         language = "ar" if detect(user_message) == "ar" else "en"
#         predicted_tag = predict_intent(user_message, language)
#         bot_response = get_response_by_tag(predicted_tag, language)
#         save_chat_to_db(user_message, bot_response, predicted_tag, language)
#         return JSONResponse(content={"response": bot_response})
#     except Exception as e:
#         print(f" Error: {e}")
#         return JSONResponse(
#             status_code=500,
#             content={"response": "حدث خطأ ما أثناء معالجة طلبك. الرجاء المحاولة لاحقاً."}
#         )

# @app.post("/api/chat", tags=["API"])
# async def chat_endpoint(chat_request: ChatRequest):
#     try:
#         user_message = chat_request.message
#         detected_lang = detect(user_message)
#         language = "ar" if detected_lang == "ar" else "en"

    
#         bot_response = WorkspaceChatbot(user_message)

    
#         if not bot_response or "لا توجد" in bot_response or "No matching" in bot_response:
#             predicted_tag = predict_intent(user_message, language)
#             bot_response = get_response_by_tag(predicted_tag, language)

        
#         save_chat_to_db(user_message, bot_response, "dynamic", language)

#         return JSONResponse(content={"response": bot_response})
    
#     class Query(BaseModel):
#      message: str

# @app.post("/query")
# async def process_query(query: Query):
#     intent = predict_intent(query.message)  # توقع الـ intent
#     response = chatbot.handle_query(query.message)  # نفّذ الاستعلام
#     return {"intent": intent, "response": response}

#     except Exception as e:
#         print(f"❌ Error: {e}")
#         return JSONResponse(
#             status_code=500,
#             content={"response": "حدث خطأ أثناء المعالجة. حاول مرة أخرى." if language == "ar" else "Sorry, an error occurred."}
#         )


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from langdetect import detect
from smart_chatbot_dynamic import WorkspaceChatbot
from chat import predict_intent, get_response_by_tag
import os
import logging
from pymongo import MongoClient
from datetime import datetime
import re

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Disable GPU
os.environ["CUDA_VISIBLE_DEVICES"] = ""

app = FastAPI(title="Chatbot API", description="Simple Chatbot with FastAPI")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Create instance of WorkspaceChatbot
chatbot = WorkspaceChatbot()

class ChatRequest(BaseModel):
    message: str
    
    
    

# دالة لاستخراج الاسم من العربية والإنجليزية
def extract_name(message: str):
    # عربي
    ar_match = re.search(r"اسمي\s+(\w+)", message)
    if ar_match:
        return ar_match.group(1), "ar"

    # إنجليزي
    en_match = re.search(r"my name is\s+(\w+)", message, re.IGNORECASE)
    if en_match:
        return en_match.group(1), "en"

    return None, None

@app.post("/api/name")
async def name_api(msg: ChatRequest):
    name, lang = extract_name(msg.message)

    if name:
        if lang == "ar":
            response = f"مرحباً بك يا {name}!"
        else:
            response = f"Hello {name}! Nice to meet you."
    else:
        response = "لم أستطع التعرف على اسمك. حاول مرة أخرى!" if "اسمي" in msg.message else "I couldn't detect your name."

    return JSONResponse(content={"response": response})    












def save_chat_to_db(user_message, bot_response, source, language):
    try:
        client = MongoClient("mongodb+srv://mohamedalibadawypr:AQpmE96i6p7O7Zpj@worklocate.ljup3kj.mongodb.net/workLocate?retryWrites=true&w=majority")
        db = client["workLocate"]
        db["chat_history"].insert_one({
            "user_message": user_message,
            "bot_response": bot_response,
            "source": source,
            "language": language,
            "timestamp": datetime.now()
        })
        logging.info("Chat saved to database")
    except Exception as e:
        logging.error(f"Error saving to chat history: {e}")

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/api/chat", tags=["API"])
async def chat_endpoint(chat_request: ChatRequest):
    user_message = chat_request.message
    language = "ar"  # default in case detection fails
    intent = "unknown"  # fallback intent

    try:
        logging.debug(f"Received message: {user_message}")
        detected_lang = detect(user_message)
        language = "ar" if detected_lang == "ar" else "en"
        logging.debug(f"Detected language: {language}")

        bot_response = chatbot.handle_query(user_message, language)
        logging.debug(f"handle_query response: {bot_response}, intent from dynamic: {intent if intent != 'unknown' else 'unknown'}")

        # يرجع لـ ML model بس لو الرد فاضي أو "عذرًا" بدون تفاصيل
        if not bot_response or ("عذرًا" in bot_response and "مساعدتك" in bot_response) or ("Sorry" in bot_response and "help" in bot_response):
            intent = predict_intent(user_message, language)
            logging.debug(f"Predicted intent: {intent}")
            bot_response = get_response_by_tag(intent, language)
            logging.info(f"Fallback to ML model, predicted intent: {intent}")
            if "عذرًا" in bot_response or "Sorry" in bot_response:
                bot_response = "من فضلك، وضح سؤالك أكثر وسأحاول مساعدتك!" if language == "ar" else "Please clarify your question, and I'll try to help!"

        save_chat_to_db(user_message, bot_response, intent, language)
        return JSONResponse(content={"response": bot_response})

    except Exception as e:
        logging.error(f"Error in chat_endpoint: {str(e)} with message: {user_message}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"response": f"حدث خطأ أثناء المعالجة: {str(e)}. حاول مرة أخرى." if language == "ar" else f"Sorry, an error occurred: {str(e)}."}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)