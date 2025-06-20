from pymongo import MongoClient
from datetime import datetime, timedelta
import re
from bson import ObjectId

# MongoDB connection
uri = "mongodb+srv://mohamedalibadawypr:AQpmE96i6p7O7Zpj@worklocate.ljup3kj.mongodb.net/workLocate?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client["workLocate"]

class WorkspaceChatbot:
    def __init__(self):
        self.current_date = datetime.now().replace(tzinfo=None)  # EEST assumed
        self.user_id = ObjectId("000000000000000000000001")  # Placeholder for testing

    def detect_intent(self, message):
        msg = message.lower().strip()
        
        # Intent patterns for all questions
        intent_patterns = {
            # Workingspaces
            "find_workspace_by_location": [
                r"مساحات.*متاحة.*(القاهرة|cairo|تجمع|tagamoa|جيزة|giza|شيخ زايد|sheikh zayed|أكتوبر|october|معادي|maadi)",
                r"available.*(cairo|tagamoa|giza|sheikh zayed|october|maadi)",
                r"open spaces.*(tagamoa|sheikh zayed)",
                r"فيه.*(تجمع|شيخ زايد|معادي)",
            ],
            "get_cheapest_workspace": [r"أرخص.*(جيزة|giza|أكتوبر|october)", r"cheapest.*(giza|october)"],
            "count_workspaces": [r"عدد المساحات", r"how many spaces", r"كم مساحة"],
            "count_by_capacity": [r"سعتها.*فوق.*(\d+)", r"fit more than.*(\d+)"],
            "shared_workspaces": [r"مشتركة.*(أكتوبر|october)", r"shared.*october"],
            "workspace_with_wifi": [r"واي فاي|wifi|internet access"],
            "book_workspace": [r"احجزيلي.*(smartzone|معادي|maadi)", r"book.*(smartzone|maadi)"],
            "private_space": [r"مساحة.*خاصة.*(شيخ زايد|sheikh zayed|تجمع|tagamoa)", r"private space.*(sheikh zayed|tagamoa)"],
            "workspaces_with_projector": [r"بروجكتور|projector"],
            "available_spaces_friday": [r"متاحة.*الجمعة|available.*friday"],

            # Reservations
            "bookings_today": [r"حجز.*النهاردة|bookings.*today"],
            "most_active_user": [r"أكتر.*حجوزات|most reservations|most active user"],
            "reservations_last_week": [r"حجوزات.*الأسبوع|reservations.*last week"],
            "book_maadi_3pm": [r"احجزيلي.*معادي.*3|book.*maadi.*3pm"],
            "smartzone_saturday": [r"smartzone.*السبت|saturday"],
            "cancel_reservation": [r"احذف.*حجز|cancel.*reservation"],
            "last_reservation": [r"آخر مرة حجزت|last booking"],
            "monthly_booking_stats": [r"إحصائيات.*الحجوزات|monthly booking statistics"],
            "workspaces_booked_today": [r"مساحات.*اتحجزت.*النهاردة|workspaces.*booked.*today"],
            "bookings_tomorrow": [r"حجوزات.*بكرة|bookings.*tomorrow"],

            # Users
            "users_from_location": [r"مستخدم.*(جيزة|giza|القاهرة|cairo)", r"users.*(giza|cairo)"],
            "get_user_email": [r"إيميل.*أحمد محمد|email.*ahmed mohamed"],
            "user_stats": [r"عدد المستخدمين|total.*users", r"female users|بنت.*مسجلين", r"users.*no bookings"],
            "new_users_week": [r"مسجلين.*الأسبوع|new users.*week"],
            "who_booked_today": [r"مين حجز.*النهاردة|who booked.*today"],
            "user_info": [r"بيانات.*مستخدم.*(\d+)|info.*user.*(\d+)"],

            # Rooms
            "available_rooms": [r"قاعات.*متاحة|rooms.*available"],
            "private_rooms": [r"قاعات.*خاصة.*(تجمع|tagamoa)|private rooms.*tagamoa"],
            "large_rooms": [r"قاعة.*كبيرة|large rooms"],
            "who_booked_meeting_room": [r"مين حجز.*اجتماعات|who booked.*meeting room"],
            "rooms_tomorrow_10am": [r"قاعات.*بكرة.*10|rooms.*tomorrow.*10am"],
            "private_room_capacity": [r"غرفة.*خاصة.*(\d+)|private room.*(\d+)"],
            "rooms_with_projector": [r"قاعات.*بروجكتور|rooms.*projector"],
            "total_available_rooms": [r"عدد الغرف.*متاحة|total rooms.*available"],
            "two_rooms_today": [r"غرفتين.*النهاردة|two.*rooms.*today"],
            "conference_room_hours": [r"أوقات.*مؤتمرات|conference room.*hours"],

            # Price Policies / Payments
            "current_discounts": [r"خصومات|discounts"],
            "hourly_rate": [r"سعر.*الساعة|hourly rate"],
            "price_policy": [r"سياسات.*الدفع|price policy"],
            "extra_fees": [r"رسوم.*إضافية|extra fees"],
            "price_by_location": [r"أسعار.*موقع|price.*location"],
            "payment_methods": [r"دفع.*كاش|دفع.*إلكتروني|credit card|payment methods"],
            "monthly_plans": [r"باقات.*شهرية|monthly plans"],
            "last_payment": [r"دفعت.*آخر|last payment"],
            "change_payment_option": [r"أغير.*دفع|change.*payment"],
        }

        for intent, patterns in intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, msg, re.IGNORECASE):
                    return intent
        return "unknown"

    def extract_entities(self, message):
        entities = {}
        message = message.replace("؟", "").replace("?", "").lower()

        # Location translation dictionary
        location_map = {
            "القاهرة": "cairo",
            "تجمع": "tagamoa",
            "جيزة": "giza",
            "شيخ زايد": "sheikh zayed",
            "أكتوبر": "october",
            "معادي": "maadi",
            "cairo": "cairo",
            "tagamoa": "tagamoa",
            "giza": "giza",
            "sheikh zayed": "sheikh zayed",
            "october": "october",
            "maadi": "maadi"
        }

        # Location
        for loc_ar, loc_en in location_map.items():
            if loc_ar in message or loc_en in message:
                entities["location"] = loc_en  # Use English for consistency in queries
                break

        # Price
        price_match = re.search(r"أقل من\s+(\d+)|less than\s+(\d+)", message)
        if price_match:
            entities["max_price"] = int(price_match.group(1) or price_match.group(2))

        # Capacity
        cap_match = re.search(r"سعتها\s+(\d+)|fit more than\s+(\d+)|لـ\s+(\d+)", message)
        if cap_match:
            entities["min_capacity"] = int(cap_match.group(1) or cap_match.group(2) or cap_match.group(3))

        # Time
        time_match = re.search(r"(\d+)(pm|am)|الساعة\s+(\d+)", message)
        if time_match:
            entities["time"] = time_match.group(1) or time_match.group(3)

        # Date
        if "الجمعة" in message or "friday" in message:
            entities["date"] = "friday"
        elif "السبت" in message or "saturday" in message:
            entities["date"] = "saturday"
        elif "النهاردة" in message or "today" in message:
            entities["date"] = "today"
        elif "بكرة" in message or "tomorrow" in message:
            entities["date"] = "tomorrow"

        # Workspace name
        if "smartzone" in message:
            entities["workspace_name"] = "smartzone"

        # User ID
        user_match = re.search(r"مستخدم\s+(\d+)|user\s+(\d+)", message)
        if user_match:
            entities["user_id"] = user_match.group(1) or user_match.group(2)

        return entities

    def handle_cheapest_workspace(self, entities, language="en"):
        location = entities.get("location", "cairo")  # Default to Cairo
        query = {"location": {"$regex": location, "$options": "i"}, "availability": True}
        print(f"[Debug] Cheapest workspace query: {query}")
        workspaces = list(db["workingspaces"].find(query))  # Convert to list
        print(f"[Debug] Cheapest workspace results: {workspaces}")
        if workspaces:
            cheapest = min(workspaces, key=lambda x: x.get("price", float('inf')))
            return f"The cheapest workspace in {location.capitalize()} is {cheapest['name']} at {cheapest['price']} EGP." if language == "en" else f"أرخص مساحة في {location.capitalize()} هي {cheapest['name']} بـ {cheapest['price']} جنيه."
        return f"No available workspaces found in {location.capitalize()}." if language == "en" else f"لا توجد مساحات متاحة في {location.capitalize()}."

    def handle_workspaces_with_projector(self, entities, language="en"):
        query = {"availability": True}
        if "location" in entities:
            query["location"] = {"$regex": entities["location"], "$options": "i"}
        query["features"] = {"$regex": "projector", "$options": "i"}
        print(f"[Debug] Workspaces with projector query: {query}")
        results = list(db["workingspaces"].find(query).limit(5))  # Convert to list
        print(f"[Debug] Workspaces with projector results: {results}")
        response = [f"- {r['name']} (Location: {r['location']})" for r in results]
        return "\n".join(response) or (f"No workspaces with projector available in {entities.get('location', 'the area').capitalize()}." if language == "en" else f"لا توجد مساحات بها بروجكتور في {entities.get('location', 'المنطقة').capitalize()}.")

    def handle_query(self, message, language="en"):
        try:
            intent = self.detect_intent(message)
            entities = self.extract_entities(message)
            print(f"[Intent]: {intent} | [Entities]: {entities}")

            if intent == "unknown":
                if "cheapest" in message.lower() or "أرخص" in message:
                    return self.handle_cheapest_workspace(entities, language)
                elif "available" in message.lower() or "متاحة" in message:
                    location = entities.get("location", "cairo")
                    query = {"location": {"$regex": location, "$options": "i"}, "availability": True}
                    print(f"[Debug] Available workspaces query: {query}")
                    workspaces = list(db["workingspaces"].find(query))
                    print(f"[Debug] Available workspaces results: {workspaces}")
                    count = len(workspaces)
                    if count > 0:
                        names = [w["name"] for w in workspaces]
                        return f"Available workspaces in {location.capitalize()} are: {', '.join(names)}." if language == "en" else f"المساحات المتاحة في {location.capitalize()} هي: {', '.join(names)}."
                    return f"No available workspaces found in {location.capitalize()}." if language == "en" else f"لا توجد مساحات متاحة في {location.capitalize()}."
                return None  # Trigger ML model fallback for unknown intents

            # Workingspaces
            if intent == "find_workspace_by_location":
                query = {"availability": True}
                if "location" in entities:
                    query["location"] = {"$regex": entities["location"], "$options": "i"}
                print(f"[Debug] Find by location query: {query}")
                results = list(db["workingspaces"].find(query).limit(5))
                print(f"[Debug] Find by location results: {results}")
                response = [f"- {r.get('name')} (Location: {r.get('location')}, Capacity: {r.get('capacity')})" for r in results]
                return "\n".join(response) or ("No available workspaces found." if language == "en" else "لا توجد مساحات متاحة.")

            elif intent == "get_cheapest_workspace":
                return self.handle_cheapest_workspace(entities, language)

            elif intent == "count_workspaces":
                count = db["workingspaces"].count_documents({"availability": True})
                return f"Number of available workspaces: {count}." if language == "en" else f"عدد المساحات المتاحة: {count}."

            elif intent == "count_by_capacity":
                cap = entities.get("min_capacity", 10)
                count = db["workingspaces"].count_documents({"capacity": {"$gt": cap}, "availability": True})
                return f"Number of workspaces with capacity over {cap}: {count}." if language == "en" else f"عدد المساحات التي سعتها أكثر من {cap}: {count}."

            elif intent == "shared_workspaces":
                query = {"type": "shared", "availability": True}
                if "location" in entities:
                    query["location"] = {"$regex": entities["location"], "$options": "i"}
                print(f"[Debug] Shared workspaces query: {query}")
                results = list(db["workingspaces"].find(query).limit(5))
                print(f"[Debug] Shared workspaces results: {results}")
                response = [f"- {r['name']} (Price: {r['price']} EGP/hour)" for r in results]
                return "\n".join(response) or ("No shared workspaces available." if language == "en" else "لا توجد مساحات مشتركة متاحة.")

            elif intent == "workspace_with_wifi":
                results = list(db["workingspaces"].find({"features": {"$regex": "wifi", "$options": "i"}, "availability": True}).limit(5))
                print(f"[Debug] Wi-Fi workspaces results: {results}")
                response = [f"- {r['name']} (Location: {r['location']})" for r in results]
                return "\n".join(response) or ("No workspaces with Wi-Fi available." if language == "en" else "لا توجد مساحات بها واي فاي.")

            elif intent == "book_workspace":
                workspace_name = entities.get("workspace_name", "any")
                query = {"availability": True}
                if workspace_name != "any":
                    query["name"] = {"$regex": workspace_name, "$options": "i"}
                elif "location" in entities:
                    query["location"] = {"$regex": entities["location"], "$options": "i"}
                print(f"[Debug] Book workspace query: {query}")
                workspace = db["workingspaces"].find_one(query)
                if workspace:
                    reservation = {
                        "workspace_id": workspace["_id"],
                        "user_id": self.user_id,
                        "start_time": self.current_date,
                        "end_time": self.current_date + timedelta(hours=1),
                        "booking_date": self.current_date
                    }
                    db["reservations"].insert_one(reservation)
                    return f"Successfully booked {workspace['name']}." if language == "en" else f"تم حجز {workspace['name']} بنجاح."
                return "No workspaces available for booking." if language == "en" else "لا توجد مساحات متاحة للحجز."

            elif intent == "private_space":
                query = {"type": "private", "availability": True}
                if "location" in entities:
                    query["location"] = {"$regex": entities["location"], "$options": "i"}
                print(f"[Debug] Private space query: {query}")
                results = list(db["workingspaces"].find(query).limit(5))
                print(f"[Debug] Private space results: {results}")
                response = [f"- {r['name']} (Location: {r['location']}, Capacity: {r['capacity']})" for r in results]
                return "\n".join(response) or ("No private workspaces available." if language == "en" else "لا توجد مساحات خاصة متاحة.")

            elif intent == "workspaces_with_projector":
                return self.handle_workspaces_with_projector(entities, language)

            elif intent == "available_spaces_friday":
                next_friday = self.current_date + timedelta(days=(4 - self.current_date.weekday() + 7) % 7)
                results = list(db["workingspaces"].find({"availability": True}).limit(5))
                print(f"[Debug] Friday spaces results: {results}")
                response = [f"- {r['name']} (Location: {r['location']})" for r in results]
                return "\n".join(response) or ("No workspaces available on Friday." if language == "en" else "لا توجد مساحات متاحة يوم الجمعة.")

            # Reservations (remaining intents can be similarly refactored into functions if needed)
            elif intent == "bookings_today":
                count = db["reservations"].count_documents({"booking_date": {"$gte": self.current_date, "$lt": self.current_date + timedelta(days=1)}})
                return f"Number of bookings today: {count}." if language == "en" else f"عدد الحجوزات اليوم: {count}."

            elif intent == "most_active_user":
                pipeline = [
                    {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 1},
                    {"$lookup": {"from": "users", "localField": "_id", "foreignField": "_id", "as": "user"}}
                ]
                result = db["reservations"].aggregate(pipeline).next()
                user = result["user"][0]
                return f"Most active user: {user['name']} ({result['count']} bookings)." if language == "en" else f"أكثر مستخدم حجز: {user['name']} ({result['count']} حجوزات)."

            # Add other intents as needed with similar refactoring

            else:
                return "Sorry, I didn't understand your request." if language == "en" else "عذرًا، لم أفهم سؤالك. حاول مرة أخرى."

        except Exception as e:
            print(f"Error in handle_query: {e}")
            return None  # Allow fallback to ML model

# Example Usage
if __name__ == "__main__":
    chatbot = WorkspaceChatbot()
    questions = [
        "إيه المساحات المتاحة في القاهرة؟",
        "What’s the cheapest workspace in Giza?",
        "كام حجز تم النهاردة؟",
        "احجزيلي في SmartZone",
        "كام مستخدم من الجيزة؟",
        "القاعات اللي فيها بروجكتور؟",
        "في خصومات حالية؟",
    ]
    for q in questions:
        print(f"Q: {q}")
        print(f"A: {chatbot.handle_query(q, 'ar' if 'ة' in q else 'en')}\n")