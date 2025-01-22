from flask_pymongo import PyMongo
from bson import ObjectId

class AttendanceModel:
    def __init__(self, mongo):
        self.attendance_collection = mongo.db.attendance

    # ฟังก์ชันสำหรับสร้าง (Create) ข้อมูลใหม่
    def create_attendance(self, user_id, timestamp, status):
        attendance_entry = {
            "user_id": user_id,
            "timestamp": timestamp,
            "status": status
        }
        result = self.attendance_collection.insert_one(attendance_entry)
        return str(result.inserted_id)

    # ฟังก์ชันสำหรับดึงข้อมูล (Read)
    def get_all_attendance(self):
        attendance_logs = self.attendance_collection.find()
        return [
            {
                "_id": str(log["_id"]),
                "user_id": log["user_id"],
                "timestamp": log["timestamp"],
                "status": log["status"]
            }
            for log in attendance_logs
        ]

    # ฟังก์ชันสำหรับลบข้อมูล (Delete)
    def delete_all_attendance(self):
        result = self.attendance_collection.delete_many({})
        return result.deleted_count

    # ฟังก์ชันสำหรับอัปเดตข้อมูล (Update)
    def update_attendance(self, record_id, updated_data):
        query = {"_id": ObjectId(record_id)}
        new_values = {"$set": updated_data}
        result = self.attendance_collection.update_one(query, new_values)
        return result.modified_count
