from flask import Blueprint, request, jsonify
from controllers.salary_controller import get_users_with_salary_new, update_salary_in_new_db

salary_bp = Blueprint('salary', __name__, url_prefix='/api')

@salary_bp.route('/salaries', methods=['GET'])
def get_salaries():
    """ดึงข้อมูล users พร้อม salary"""
    data, status = get_users_with_salary_new()  # ใช้ฟังก์ชันใหม่สำหรับการรวมข้อมูล
    return jsonify(data), status


@salary_bp.route('/updateSalary', methods=['POST'])
def update_salaries():
    try:
        data = request.json
        print("Received data for salary update:", data)  # Debug ข้อมูลที่ได้รับ

        if not data or 'salaries' not in data:
            return jsonify({"error": "Invalid data format"}), 400

        for salary_data in data['salaries']:
            user_id = salary_data.get("user_id")
            salary_value = salary_data.get("salary")
            print(f"Updating salary for user_id={user_id}, salary={salary_value}")

            result, status = update_salary_in_new_db(user_id, salary_value)
            if status != 200:
                print(f"Failed to update salary for user_id {user_id}")

        return jsonify({"message": "Salaries updated successfully!"}), 200
    except Exception as e:
        print(f"Error in update_salaries: {e}")
        return jsonify({"error": str(e)}), 500
