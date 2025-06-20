# from pymongo import MongoClient

# uri = "mongodb+srv://mohamedalibadawypr:AQpmE96i6p7O7Zpj@worklocate.ljup3kj.mongodb.net/workLocate?retryWrites=true&w=majority"
# client = MongoClient(uri)
# db = client["workLocate"]

# def get_response_by_tag(tag, language):
#     collection = db["arabicintents"] if language == "ar" else db["englishintents"]
#     intent_data = collection.find_one({"tag": tag})
#     if intent_data and "responses" in intent_data:
#         return intent_data["responses"][0]  
#     return "عذرًا، لم أفهم طلبك." if language == "ar" else "Sorry, I didn't understand that."

from pymongo import MongoClient

uri = "mongodb+srv://mohamedalibadawypr:AQpmE96i6p7O7Zpj@worklocate.ljup3kj.mongodb.net/workLocate?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client["workLocate"]

def get_response_by_tag(tag, language):
    collection = db["arabicintents"] if language == "ar" else db["englishintents"]
    intent_data = collection.find_one({"tag": tag})
    if intent_data and "responses" in intent_data:
        return intent_data["responses"][0]  # ممكن تطويره لاحقًا لاختيار عشوائي
    return "عذرًا، لم أفهم طلبك." if language == "ar" else "Sorry, I didn't understand that."
