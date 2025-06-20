# import json
# import pickle
# import random
# import numpy as np
# import nltk
# from nltk.stem import WordNetLemmatizer
# from nltk.tokenize import word_tokenize
# import tensorflow as tf
# from tensorflow import keras

# nltk.download("punkt")
# lemmatizer = WordNetLemmatizer()

# data = {"intents": []}

# for filename in ["intents(modified) (1).json", "new_arabic_intents.json"]:
#     with open(filename, encoding="utf-8") as f:
#         file_data = json.load(f)
    
#         if isinstance(file_data, dict) and "intents" in file_data:
#             data["intents"].extend(file_data["intents"])
#         else:
#             print(f"Warning: Unrecognized format in {filename}")

# print(f"Total intents loaded: {len(data['intents'])}")

# words, labels, docs_x, docs_y = [], [], [], []

# for intent in data["intents"]:
#     for pattern in intent["patterns"]:
#         wrds = word_tokenize(pattern)
#         words.extend(wrds)
#         docs_x.append(wrds)
#         docs_y.append(intent["tag"])
#     if intent["tag"] not in labels:
#         labels.append(intent["tag"])

# words = sorted(set([lemmatizer.lemmatize(w.lower()) for w in words if w not in ["?", ".", "!"]]))

# training, output = [], []
# out_empty = [0] * len(labels)

# for x, doc in enumerate(docs_x):
#     bag = [1 if w in [lemmatizer.lemmatize(word.lower()) for word in doc] else 0 for w in words]
#     output_row = out_empty[:]
#     output_row[labels.index(docs_y[x])] = 1
#     training.append(bag)
#     output.append(output_row)

# training, output = np.array(training), np.array(output)

# model = keras.Sequential([
#     keras.layers.Dense(8, activation='relu', input_shape=(len(training[0]),)),
#     keras.layers.Dense(8, activation='relu'),
#     keras.layers.Dense(len(output[0]), activation='softmax')
# ])

# model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
# model.fit(training, output, epochs=100, batch_size=8, verbose=1)

# model.save("chatbot_model.h5")
# pickle.dump((words, labels), open("chatbot_data.pkl", "wb"))

# print(" Training complete. Model saved to chatbot_model.h5 and data to chatbot_data.pkl")


import json
import nltk
import numpy as np
import pickle
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD
from preprocessing import tokenize, bag_of_words


training_configs = [
    {"language": "ar", "file": "ar.json"},
    {"language": "en", "file": "intents(modified) (1).json"}
]


for config in training_configs:
    language = config["language"]
    intents_file = config["file"]

    print(f"\n Training model for language: {language.upper()}")

    with open(intents_file, encoding="utf-8") as f:
        data = json.load(f)

    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = tokenize(pattern, language)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = sorted(set(words))
    labels = sorted(set(labels))

    training = []
    output = []

    out_empty = [0] * len(labels)

    for x, doc in enumerate(docs_x):
        bow = bag_of_words(doc, words, language)
        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bow)
        output.append(output_row)

    training = np.array(training)
    output = np.array(output)

    
    model = Sequential()
    model.add(Dense(128, input_shape=(len(training[0]),), activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(len(output[0]), activation="softmax"))

    sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
    model.compile(loss="categorical_crossentropy", optimizer=sgd, metrics=["accuracy"])

    model.fit(training, output, epochs=300, batch_size=5, verbose=1)

   
    model.save(f"model_{language}.h5")
    with open(f"{language}_data.pkl", "wb") as f:
        pickle.dump((words, labels, training, output), f)

    print(f"\u2705 Model for '{language}' saved as model_{language}.h5")



