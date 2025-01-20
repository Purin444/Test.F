from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
from models.user_model import create_user, find_user_by_username
import jwt
import datetime
from extensions import mongo
from bson.objectid import ObjectId  # สำหรับจัดการ ObjectId
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secret Key สำหรับ JWT
SECRET_KEY = "your_secret_key"

def register_user(data):
    """
    ฟังก์ชันสำหรับ Register ผู้ใช้ใหม่
    """
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"error": "Username and Password are required"}, 400

    # ตรวจสอบว่า Username ซ้ำหรือไม่
    if find_user_by_username(username):
        return {"error": "Username already exists"}, 400

    # Hash รหัสผ่านและบันทึกข้อมูล
    hashed_password = generate_password_hash(password)
    create_user(username, hashed_password)

    return {"message": "User registered successfully"}, 201


def login_user(data):
    username = data.get("username")
    password = data.get("password")

    # ค้นหาผู้ใช้จากฐานข้อมูล
    user = find_user_by_username(username)
    if not user:
        return {"error": "Invalid username or password"}, 401

    # ตรวจสอบรหัสผ่าน
    if not check_password_hash(user["password"], password):
        return {"error": "Invalid username or password"}, 401

    # หากสำเร็จ ให้ส่ง Token และ User ID กลับมา
    token = jwt.encode({
        "userId": str(user["_id"]),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

    return {
        "message": "Login successful",
        "token": token,
        "userId": str(user["_id"])
    }, 200



def validate_token(token):
    """
    ฟังก์ชันสำหรับตรวจสอบ JWT Token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"username": payload["username"], "valid": True}, 200
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}, 401
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}, 401


def find_user_by_id(_id):
    """
    ค้นหาข้อมูลผู้ใช้จาก _id
    """
    user_collection = mongo.db.auth_users
    try:
        return user_collection.find_one({"_id": ObjectId(_id)})  # ใช้ ObjectId เพื่อค้นหา
    except Exception as e:
        print(f"Error finding user by id: {e}")
        return None
    

def hash_password(password):
    return generate_password_hash(password)


def update_user_password(user_id, new_hashed_password):
    try:
        user_collection = mongo.db.auth_users
        result = user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password": new_hashed_password}}
        )
        if result.matched_count == 0:
            logger.warning(f"User not found in database for ID: {user_id}")
            raise Exception("User not found")
    except Exception as e:
        logger.error(f"Failed to update password for user ID {user_id}: {str(e)}")
        raise
