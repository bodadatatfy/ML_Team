# import pickle
# import numpy as np
# import json
# from tensorflow.keras.models import load_model
# from preprocessing import tokenize, bag_of_words

# model_en = load_model("chatbot_model.h5")
# words_en = pickle.load(open("chatbot_data.pkl", "rb"))[0]
# classes_en = pickle.load(open("chatbot_data.pkl", "rb"))[1]

# model_ar = load_model("chatbot_model.h5")
# words_ar = pickle.load(open("chatbot_data.pkl", "rb"))[0]
# classes_ar = pickle.load(open("chatbot_data.pkl", "rb"))[1]


# def predict_intent(sentence, language):
#     if language == "ar":
#         model, words, classes = model_ar, words_ar, classes_ar
#     else:
#         model, words, classes = model_en, words_en, classes_en

#     tokens = tokenize(sentence, language)  
#     bow = bag_of_words(tokens, words)
#     res = model.predict(np.array([bow]))[0]
#     threshold = 0.25
#     results = [(i, r) for i, r in enumerate(res) if r > threshold]

#     if results:
#         results.sort(key=lambda x: x[1], reverse=True)
#         return classes[results[0][0]]
#     return "noanswer"


# with open("ar.json", encoding="utf-8") as f:
#     intents_ar = json.load(f)

# with open("intents(modified) (1).json", encoding="utf-8") as f:
#     intents_en = json.load(f)


# def get_response(message, language='en'):
#     intent = predict_intent(message, language)
#     if language == "ar":
#         intents = intents_ar
#     else:
#         intents = intents_en

#     for i in intents["intents"]:
#         if i["tag"] == intent:
#             return np.random.choice(i["responses"])

#     return "أنا آسف، لم أفهم قصدك." if language == "ar" else "Sorry, I didn't understand that."

# import pickle
# import numpy as np
# import json
# from tensorflow.keras.models import load_model
# from preprocessing import tokenize, bag_of_words

# # Load Arabic model and data
# model_ar = load_model("model_ar.h5")
# with open("ar_data.pkl", "rb") as f:
#     words_ar, classes_ar, *_ = pickle.load(f)

# # Load English model and data
# model_en = load_model("model_en.h5")
# with open("en_data.pkl", "rb") as f:
#     words_en, classes_en, *_ = pickle.load(f)

# def predict_intent(sentence, language):
#     if language == "ar":
#         model, words, classes = model_ar, words_ar, classes_ar
#     else:
#         model, words, classes = model_en, words_en, classes_en

#     tokens = tokenize(sentence, language)
#     bow = bag_of_words(tokens, words, language)
#     res = model.predict(np.array([bow]))[0]
#     threshold = 0.25
#     results = [(i, r) for i, r in enumerate(res) if r > threshold]

#     if results:
#         results.sort(key=lambda x: x[1], reverse=True)
#         return classes[results[0][0]]
#     return "noanswer"


import os
import pickle
import numpy as np
from tensorflow.keras.models import load_model
from preprocessing import tokenize, bag_of_words
import logging
import random
from pymongo import MongoClient

# Setup logging
logging.basicConfig(level=logging.INFO)

# MongoDB connection
uri = "mongodb+srv://mohamedalibadawypr:AQpmE96i6p7O7Zpj@worklocate.ljup3kj.mongodb.net/workLocate?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client["workLocate"]

def load_model_safe(model_path):
    try:
        model = load_model(model_path)
        logging.info(f"Model {model_path} loaded successfully")
        return model
    except Exception as e:
        logging.error(f"Failed to load model {model_path}: {e}")
        raise

# Load models
try:
    model_ar = load_model_safe("model_ar.h5")
    model_en = load_model_safe("model_en.h5")
except Exception as e:
    logging.error(f"Error loading models: {e}")
    raise

# Load data
try:
    with open("ar_data.pkl", "rb") as f:
        words_ar, classes_ar, *_ = pickle.load(f)
    with open("en_data.pkl", "rb") as f:
        words_en, classes_en, *_ = pickle.load(f)
    logging.info("Data files loaded successfully")
except Exception as e:
    logging.error(f"Error loading data files: {e}")
    raise

def predict_intent(sentence, language):
    try:
        logging.debug(f"Predicting intent for: {sentence}, language: {language}")
        if language == "ar":
            model, words, classes = model_ar, words_ar, classes_ar
        else:
            model, words, classes = model_en, words_en, classes_en

        tokens = tokenize(sentence, language)
        if not tokens:
            logging.warning(f"No tokens generated for: {sentence}")
            return "noanswer"

        bow = bag_of_words(tokens, words, language)
        if not bow.any():
            logging.warning(f"Empty bag of words for: {sentence}")
            return "noanswer"

        res = model.predict(np.array([bow]), verbose=0)[0]
        logging.debug(f"Model prediction: {res}")
        threshold = 0.7  # Increased threshold for better accuracy
        results = [(i, r) for i, r in enumerate(res) if r > threshold]

        if results:
            results.sort(key=lambda x: x[1], reverse=True)
            intent = classes[results[0][0]]
            confidence = results[0][1]
            logging.debug(f"Predicted intent: {intent} with confidence: {confidence}")
            return intent
        logging.warning(f"No intent predicted above threshold for: {sentence}")
        return "noanswer"

    except ValueError as ve:
        logging.error(f"ValueError in predict_intent: {str(ve)}")
        return "noanswer"
    except Exception as e:
        logging.error(f"Unexpected error in predict_intent: {str(e)}", exc_info=True)
        return "noanswer"

def get_response_by_tag(tag, language):
    try:
        collection = db["arabicintents"] if language == "ar" else db["englishintents"]
        intent_data = collection.find_one({"tag": tag})
        if intent_data and "responses" in intent_data:
            # Randomly select a response for variety
            response = random.choice(intent_data["responses"])
            logging.debug(f"Response for tag {tag}: {response}")
            return response
        logging.warning(f"No response found for tag: {tag}")
        return "عذرًا، لم أفهم طلبك." if language == "ar" else "Sorry, I didn't understand that."
    except Exception as e:
        logging.error(f"Error in get_response_by_tag: {str(e)}")
        return "عذرًا، لم أفهم طلبك." if language == "ar" else "Sorry, I didn't understand that."