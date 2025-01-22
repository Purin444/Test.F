import re
import os
import logging
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from controllers.auth_controller import register_user, login_user, find_user_by_id, update_user_password

# กำหนด Blueprint สำหรับระบบ Login
auth_bp = Blueprint("auth", __name__, url_prefix="/api")

# ใช้ Master Key จาก environment
MASTER_KEY = os.getenv("MASTER_KEY", "123456")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Route สำหรับการลงทะเบียน
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    # ตรวจสอบข้อมูล
    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password are required"}), 400

    # ตรวจสอบ Master Key
    if "master_key" not in data or data["master_key"] != MASTER_KEY:
        return jsonify({"error": "Invalid Master Key"}), 403

    response, status = register_user(data)
    return jsonify(response), status

# Route สำหรับการล็อกอิน
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    # ตรวจสอบข้อมูล
    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password are required"}), 400

    response, status = login_user(data)
    if status == 200:
        logger.info(f"User {data['username']} logged in successfully")
    else:
        logger.warning(f"Failed login attempt for {data.get('username', 'unknown user')}")

    return jsonify(response), status

# Route สำหรับดึงข้อมูลผู้ใช้
@auth_bp.route("/auth_users/<_id>", methods=["GET"])
def get_user_by_id(_id):
    user = find_user_by_id(_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "_id": str(user.get("_id")),
        "username": user.get("username"),
        "created_at": user.get("created_at")
    }), 200


# ฟังก์ชันตรวจสอบความแข็งแรงของรหัสผ่าน
def is_password_strong(password):
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    if not re.search("[@#$%^&+=]", password):
        return False
    return True

# Route สำหรับการเปลี่ยนรหัสผ่าน
@auth_bp.route("/auth_users/<_id>/change_password", methods=["PUT"])
def change_password(_id):
    try:
        data = request.json
        old_password = data.get("oldPassword")
        new_password = data.get("newPassword")

        if not old_password or not new_password:
            logger.warning("Missing oldPassword or newPassword in request")
            return jsonify({"error": "Both old and new passwords are required"}), 400

        user = find_user_by_id(_id)
        if not user:
            logger.warning(f"User not found for ID: {_id}")
            return jsonify({"error": "User not found"}), 404

        if not check_password_hash(user["password"], old_password):
            logger.warning(f"Invalid old password for user ID: {_id}")
            return jsonify({"error": "Invalid old password"}), 400

        hashed_password = generate_password_hash(new_password)
        update_user_password(_id, hashed_password)
        logger.info(f"Password updated successfully for user ID: {_id}")
        return jsonify({"message": "Password changed successfully"}), 200
    except Exception as e:
        logger.error(f"Error in change_password for user ID {_id}: {str(e)}")
        return jsonify({"error": "Failed to update password"}), 500
