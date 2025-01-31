from zk import ZK
from extensions import mongo

# รายการ IP ของอุปกรณ์ ZKTeco
DEVICE_IPS = [
    '192.168.1.220',
    # '192.168.1.221',
    # '192.168.1.222',
]

# ฟังก์ชันสำหรับเชื่อมต่อ ZKTeco แต่ละเครื่อง
def connect_zk(ip):
    zk = ZK(ip, port=4370, timeout=1)  # ลดเวลารอให้เหลือ 1 วินาที
    try:
        conn = zk.connect()
        conn.disable_device()
        print(f"Connected to ZKTeco at {ip} successfully.")
        return conn
    except Exception as e:
        print(f"Error connecting to ZK device at {ip}: {e}")
        return None

# ฟังก์ชันดึงข้อมูลจาก ZKTeco และอัปเดตเฉพาะข้อมูลใหม่
def fetch_users():
    all_users = []
    zk_connection_failed = True  # ตั้งค่าเริ่มต้นให้ถือว่าเชื่อมต่อไม่สำเร็จ

    for ip in DEVICE_IPS:
        conn = connect_zk(ip)
        if conn:
            zk_connection_failed = False  # แสดงว่าเชื่อมต่อสำเร็จ
            try:
                users = conn.get_users()
                if users:
                    print(f"Fetched {len(users)} users from ZKTeco at {ip}.")
                    for user in users:
                        all_users.append({
                            'user_id': user.user_id,
                            'name': user.name or "Unnamed",
                            'device_ip': ip
                        })
                else:
                    print(f"No users found on the device at {ip}.")
            except Exception as e:
                print(f"Error fetching users from device at {ip}: {e}")
            finally:
                conn.enable_device()
                conn.disconnect()
        else:
            print(f"Skipping device at {ip} due to connection issues.")

    try:
        users_collection = mongo.db.users

        # สร้าง Index เพื่อให้ Query เร็วขึ้น
        users_collection.create_index("user_id", unique=True)
        users_collection.create_index("device_ip")

        if all_users:
            for user in all_users:
                users_collection.update_one(
                    {"user_id": user["user_id"]}, 
                    {"$set": user}, 
                    upsert=True
                )
            print(f"Updated {len(all_users)} users in MongoDB.")
        else:
            print("No new users to update in MongoDB.")

        # ถ้า ZKTeco ไม่เชื่อมต่อ ใช้ข้อมูลจาก MongoDB
        if zk_connection_failed:
            print("Using data from MongoDB due to ZKTeco connection issues.")
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

        # ดึงข้อมูลทั้งหมดจาก MongoDB และแปลง ObjectId เป็น str
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

        print("Users successfully fetched and serialized.")
        return response_data, 200

    except Exception as e:
        print(f"Error updating MongoDB: {e}")
        return {"error": str(e)}, 500
