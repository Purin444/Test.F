from extensions import mongo

def get_holidays_from_db():
    """ ดึงข้อมูลวันหยุดจาก MongoDB """
    try:
        holidays_collection = mongo.db.holidays
        holidays_from_db = holidays_collection.find()

        response_data = [
            {
                "title": holiday.get("name") or holiday.get("title"),
                "start": holiday.get("date") or holiday.get("start"),
                "backgroundColor": holiday.get("color") or holiday.get("backgroundColor", "#f39c12"),
                "textColor": holiday.get("textColor", "#fff")
            }
            for holiday in holidays_from_db
        ]
        return response_data, 200
    except Exception as e:
        return {"error": str(e)}, 500

def save_holidays_to_db(holidays):
    """ บันทึกข้อมูลวันหยุดทั้งหมดลง MongoDB """
    try:
        holidays_collection = mongo.db.holidays

        for holiday in holidays:
            name = holiday.get("name")
            date = holiday.get("date")

            if not name or not date:
                print(f"Skipping invalid event: {holiday}")
                continue

            holidays_collection.update_one(
                {"name": name, "date": date},
                {"$set": {
                    "name": name,
                    "date": date,
                    "color": holiday.get("backgroundColor", "#f39c12")
                }},
                upsert=True
            )

        return {"message": "All holidays saved successfully!"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
