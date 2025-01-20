from extensions import mongo
from bson import ObjectId

def get_ot_requests_from_db():
    """ ดึงข้อมูล OT Requests ทั้งหมดจาก MongoDB """
    try:
        ot_collection = mongo.db.ot_requests
        ot_requests = ot_collection.find()

        response_data = [
            {
                "employee_id": ot.get("employee_id"),
                "employee_name": ot.get("employee_name"),
                "date": ot.get("date"),
                "reason": ot.get("reason")
            }
            for ot in ot_requests
        ]
        return response_data, 200
    except Exception as e:
        return {"error": str(e)}, 500

def save_ot_request_to_db(ot_data):
    """ บันทึกข้อมูล OT Request ลง MongoDB """
    try:
        ot_collection = mongo.db.ot_requests

        employee_id = ot_data.get("employee_id")
        employee_name = ot_data.get("employee_name")
        date = ot_data.get("date")
        reason = ot_data.get("reason")

        if not employee_id or not date or not reason:
            return {"error": "Missing required fields"}, 400

        ot_collection.insert_one({
            "employee_id": employee_id,
            "employee_name": employee_name,
            "date": date,
            "reason": reason
        })

        return {"message": "OT Request saved successfully!"}, 201
    except Exception as e:
        return {"error": str(e)}, 500

def save_accepted_ot_request_to_db(ot_data):
    """ บันทึกข้อมูล Accepted OT Request ลง MongoDB และลบข้อมูลออกจาก ot_requests """
    try:
        # บันทึกข้อมูลใน accepted_ot_requests
        accepted_ot_collection = mongo.db.accepted_ot_requests
        accepted_ot_collection.insert_one(ot_data)

        # ลบข้อมูลจาก ot_requests
        ot_collection = mongo.db.ot_requests
        delete_result = ot_collection.delete_one({
            "employee_name": ot_data.get("employee_name"),
            "date": ot_data.get("date"),
            "reason": ot_data.get("reason")
        })

        if delete_result.deleted_count == 0:
            return {"error": "Failed to delete OT Request from ot_requests"}, 500

        return {"message": "OT Request accepted and saved successfully!"}, 201
    except Exception as e:
        return {"error": str(e)}, 500

    
    
def delete_accepted_ot_request_from_db(ot_data):
    """ ลบข้อมูลจาก Accepted OT Requests """
    try:
        accepted_ot_collection = mongo.db.accepted_ot_requests
        result = accepted_ot_collection.delete_one({
            "employee_name": ot_data.get("employee_name"),
            "date": ot_data.get("date"),
            "reason": ot_data.get("reason")
        })
        if result.deleted_count == 1:
            return {"message": "Accepted OT Request deleted successfully"}, 200
        else:
            return {"error": "Accepted OT Request not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500
   

def get_accepted_ot_requests_from_db():
    """ ดึงข้อมูล Accepted OT Requests จาก MongoDB """
    try:
        accepted_ot_collection = mongo.db.accepted_ot_requests
        ot_requests = accepted_ot_collection.find()
        response_data = [
            {
                "employee_name": ot.get("employee_name"),
                "date": ot.get("date"),
                "reason": ot.get("reason")
            }
            for ot in ot_requests
        ]
        return response_data, 200
    except Exception as e:
        return {"error": str(e)}, 500
    
# ฟังก์ชันดึงข้อมูล Accepted OT Requests
def get_accepted_ot_requests_from_db():
    """ ดึงข้อมูลทั้งหมดจาก Collection accepted_ot_requests """
    try:
        accepted_ot_collection = mongo.db.accepted_ot_requests
        data = list(accepted_ot_collection.find())
        for item in data:
            item['_id'] = str(item['_id'])  # แปลง ObjectId เป็น string
        return data, 200
    except Exception as e:
        return {"error": str(e)}, 500

# ฟังก์ชันลบข้อมูลที่เลือกจาก Accepted OT Requests
def delete_accepted_ot_requests_from_db(ids):
    """ ลบข้อมูลที่เลือกใน Collection accepted_ot_requests """
    try:
        if not ids:
            return {"error": "No IDs provided"}, 400

        accepted_ot_collection = mongo.db.accepted_ot_requests
        result = accepted_ot_collection.delete_many({"_id": {"$in": [ObjectId(id) for id in ids]}})
        return {"message": f"Deleted {result.deleted_count} records successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
