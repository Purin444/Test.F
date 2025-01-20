from flask import Blueprint, jsonify, request
from extensions import mongo

department_bp = Blueprint('department', __name__, url_prefix='/api')

@department_bp.route('/departments', methods=['GET'])
def get_departments():
    try:
        users_collection = mongo.db.users
        departments_collection = mongo.db.departments  # สมมติว่าคุณมีคอลเลกชันนี้
        users = list(users_collection.find())

        response_data = [
            {
                "user_id": user.get("user_id"),
                "name": user.get("name"),
                "department": departments_collection.find_one({"user_id": user.get("user_id")}).get("department", "N/A") if departments_collection.find_one({"user_id": user.get("user_id")}) else "N/A"
            }
            for user in users
        ]
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@department_bp.route('/updateDepartment', methods=['POST'])
def update_departments():
    try:
        data = request.json.get('departments', [])
        departments_collection = mongo.db.departments

        for department in data:
            user_id = department.get("user_id")
            department_name = department.get("department")
            departments_collection.update_one(
                {"user_id": user_id},
                {"$set": {"department": department_name}},
                upsert=True
            )
        return jsonify({"message": "Departments updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@department_bp.route('/departments-list', methods=['GET'])
def get_department_list():
    try:
        departments_collection = mongo.db.departments
        department_list = list(departments_collection.find({"name": {"$exists": True, "$ne": ""}}, {"_id": 0, "name": 1}))
        return jsonify(department_list), 200
    except Exception as e:
        print(f"Error fetching department list: {e}")
        return jsonify({"error": str(e)}), 500


@department_bp.route('/addDepartment', methods=['POST'])
def add_department():
    try:
        # รับข้อมูลชื่อแผนกจาก request body
        department_name = request.json.get('name')  
        
        # ตรวจสอบว่ามีชื่อแผนกหรือไม่
        if not department_name:
            return jsonify({"error": "Department name is required"}), 400

        departments_collection = mongo.db.departments

        # เพิ่มแผนกใหม่ในฐานข้อมูล
        departments_collection.insert_one({"name": department_name})

        return jsonify({"message": "Department added successfully!"}), 200
    except Exception as e:
        print(f"Error adding department: {e}")
        return jsonify({"error": str(e)}), 500
