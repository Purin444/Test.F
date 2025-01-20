from extensions import mongo

def update_salary_in_new_db(user_id, salary):
    """อัปเดต salary ในคอลเลกชันใหม่"""
    try:
        salary_collection = mongo.db.user_salary

        result = salary_collection.update_one(
            {"user_id": user_id},  # ค้นหาด้วย user_id
            {"$set": {"salary": salary}},  # อัปเดตฟิลด์ salary
            upsert=True  # ถ้าไม่มี user_id ให้เพิ่มเอกสารใหม่
        )

        if result.matched_count > 0 or result.upserted_id:
            print(f"Update successful for user_id {user_id}")
            return {"message": "Salary updated successfully!"}, 200
        else:
            print(f"No changes made for user_id {user_id}")
            return {"message": "No changes made"}, 200
    except Exception as e:
        print(f"Error updating salary in new DB: {e}")
        return {"error": str(e)}, 500


def get_users_with_salary_new():
    """ดึงข้อมูลผู้ใช้งานพร้อม salary จากสองคอลเลกชัน"""
    try:
        users_collection = mongo.db.users
        salary_collection = mongo.db.user_salary

        # ดึงข้อมูล users
        users = list(users_collection.find())
        user_salary_map = {
            entry["user_id"]: entry.get("salary", 0)
            for entry in salary_collection.find()
        }

        # รวมข้อมูล
        response_data = [
            {
                "user_id": user.get("user_id"),
                "name": user.get("name"),
                "salary": user_salary_map.get(user.get("user_id"), 0)
            }
            for user in users
        ]

        return response_data, 200
    except Exception as e:
        print(f"Error fetching users with salary from two collections: {e}")
        return {"error": str(e)}, 500
