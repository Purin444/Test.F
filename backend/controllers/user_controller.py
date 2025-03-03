import time
from zk import ZK
from extensions import mongo
import os
import platform

# รายการ IP ของอุปกรณ์ ZKTeco
DEVICE_IPS = ['192.168.1.220']

ping_status = {}  # ✅ เก็บผลลัพธ์ Ping

# ฟังก์ชันเช็คว่าอุปกรณ์ ZKTeco เข้าถึงได้ไหม
def is_device_reachable(ip):
    if ip in ping_status:
        return ping_status[ip]  # ✅ ใช้ค่าที่เคย Ping แล้ว
    param = "-n 1" if platform.system().lower() == "windows" else "-c 1"
    response = os.system(f"ping {param} {ip} > nul 2>&1")
    ping_status[ip] = response == 0  # ✅ เก็บค่า Ping ไว้ใช้ซ้ำ
    return ping_status[ip]

# ฟังก์ชันเชื่อมต่อกับ ZKTeco
def connect_zk(ip):
    if not is_device_reachable(ip):  # ✅ เช็ค Ping ก่อนเชื่อมต่อ
        print(f"❌ Skipping {ip} due to ping failure. (connect_zk)")
        return None
    zk = ZK(ip, port=4370, timeout=1)  # ตั้งค่า Timeout ให้ต่ำสุด (1 วินาที)
    try:
        conn = zk.connect()
        conn.disable_device()
        print(f"✅ Connected to ZKTeco at {ip}")
        return conn
    except Exception as e:
        print(f"⚠️ Error connecting to ZK device at {ip}: {e}")
        return None

# ฟังก์ชันดึงข้อมูลผู้ใช้จาก ZKTeco
def fetch_users():
    all_users = []
    zk_connection_failed = True  # ✅ กำหนดค่าเริ่มต้นก่อนใช้ตัวแปรนี้

    for ip in DEVICE_IPS:
        if not is_device_reachable(ip):  # ✅ เช็ค Ping ก่อนเชื่อมต่อ
            print(f"❌ Skipping {ip} due to ping failure. (fetch_users)")
            continue  # ✅ ข้ามไปเลย ไม่ต้องเสียเวลาพยายามเชื่อมต่อ

        conn = connect_zk(ip)
        if conn:
            zk_connection_failed = False  # ถ้าต่อได้ ให้เปลี่ยนเป็น False
            try:
                users = conn.get_users()
                if users:
                    print(f"✅ Fetched {len(users)} users from {ip}.")
                    for user in users:
                        all_users.append({
                            'user_id': user.user_id,
                            'name': user.name or "Unnamed",
                            'device_ip': ip
                        })
                else:
                    print(f"⚠️ No users found on {ip}.")
            except Exception as e:
                print(f"⚠️ Error fetching users from {ip}: {e}")
            finally:
                conn.enable_device()
                conn.disconnect()
                print(f"🔌 Disconnected from {ip}.")
        else:
            print(f"⚠️ Skipping {ip} due to connection issues.")

    try:
        users_collection = mongo.db.users
        if all_users:
            for user in all_users:
                users_collection.update_one(
                    {"user_id": user["user_id"]}, 
                    {"$set": user}, 
                    upsert=True
                )
            print(f"✅ Updated {len(all_users)} users in MongoDB.")

        # ถ้า ZKTeco ไม่เชื่อมต่อ ใช้ข้อมูลจาก MongoDB ทันที
        if zk_connection_failed:
            print("⚠️ Using data from MongoDB due to ZKTeco connection issues.")
            users_from_db = users_collection.find()
            return [
                {
                    "_id": str(user["_id"]),
                    "user_id": user["user_id"],
                    "name": user["name"],
                    "device_ip": user.get("device_ip")
                }
                for user in users_from_db
            ], 200

        # ดึงข้อมูลจาก MongoDB
        users_from_db = users_collection.find()
        response_data = [
            {
                "_id": str(user["_id"]),
                "user_id": user["user_id"],
                "name": user["name"],
                "device_ip": user.get("device_ip")
            }
            for user in users_from_db
        ]

        print("✅ Users successfully fetched and serialized.")
        return response_data, 200

    except Exception as e:
        print(f"❌ Error updating MongoDB: {e}")
        return {"error": str(e)}, 500

