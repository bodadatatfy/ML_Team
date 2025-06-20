# from pymongo import MongoClient
# from datetime import datetime

# uri = "mongodb+srv://mohamedalibadawypr:AQpmE96i6p7O7Zpj@worklocate.ljup3kj.mongodb.net/workLocate?retryWrites=true&w=majority"
# client = MongoClient(uri)
# db = client["workLocate"]

# def save_chat_to_db(user_input, bot_response, tag, language):
#     collection = db["arabicchats"] if language == "ar" else db["englishchats"]
#     try:
#         collection.insert_one({
#             "user_input": user_input,
#             "bot_response": bot_response,
#             "tag": tag,
#             "timestamp": datetime.utcnow()
#         })
#     except Exception as e:
#         print(f"Error saving to database: {e}")

from pymongo import MongoClient
from datetime import datetime

uri = "mongodb+srv://mohamedalibadawypr:AQpmE96i6p7O7Zpj@worklocate.ljup3kj.mongodb.net/workLocate?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client["workLocate"]

def save_chat_to_db(user_input, bot_response, tag, language):
    collection = db["arabicchats"] if language == "ar" else db["englishchats"]
    try:
        collection.insert_one({
            "user_input": user_input,
            "bot_response": bot_response,
            "tag": tag,
            "language": language,
            "timestamp": datetime.utcnow()
        })
    except Exception as e:
        print(f"Error saving to database: {e}")


