from extensions import mongo

def update_department_in_db(user_id, department):
    """อัปเดต department ในคอลเลกชันใหม่"""
    try:
        department_collection = mongo.db.user_department

        result = department_collection.update_one(
            {"user_id": user_id},  # ค้นหาด้วย user_id
            {"$set": {"department": department}},  # อัปเดตฟิลด์ department
            upsert=True  # ถ้าไม่มี user_id ให้เพิ่มเอกสารใหม่
        )

        if result.matched_count > 0 or result.upserted_id:
            print(f"Update successful for user_id {user_id}")
            return {"message": "Department updated successfully!"}, 200
        else:
            print(f"No changes made for user_id {user_id}")
            return {"message": "No changes made"}, 200
    except Exception as e:
        print(f"Error updating department in DB: {e}")
        return {"error": str(e)}, 500


def get_users_with_department():
    """ดึงข้อมูลผู้ใช้งานพร้อม department จากสองคอลเลกชัน"""
    try:
        users_collection = mongo.db.users
        department_collection = mongo.db.user_department

        # ดึงข้อมูล users
        users = list(users_collection.find())
        user_department_map = {
            entry["user_id"]: entry.get("department", "N/A")
            for entry in department_collection.find()
        }

        # รวมข้อมูล
        response_data = [
            {
                "user_id": user.get("user_id"),
                "name": user.get("name"),
                "department": user_department_map.get(user.get("user_id"), "N/A")
            }
            for user in users
        ]

        return response_data, 200
    except Exception as e:
        print(f"Error fetching users with department from two collections: {e}")
        return {"error": str(e)}, 500
