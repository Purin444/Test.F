from zk import ZK
from extensions import mongo

# รายการ IP ของอุปกรณ์ ZKTeco
DEVICE_IPS = [
    '192.168.1.220',
    # '192.168.1.221',  # เพิ่ม IP อุปกรณ์ที่สอง
    # '192.168.1.222',  # เพิ่ม IP อุปกรณ์ที่สาม
]

# ฟังก์ชันสำหรับเชื่อมต่อ ZKTeco แต่ละเครื่อง
def connect_zk(ip):
    zk = ZK(ip, port=4370, timeout=5)
    try:
        conn = zk.connect()
        conn.disable_device()
        print(f"Connected to ZKTeco at {ip} successfully.")
        return conn
    except Exception as e:
        print(f"Error connecting to ZK device at {ip}: {e}")
        return None

# ฟังก์ชันดึงข้อมูลผู้ใช้งานจากหลายเครื่องและบันทึกใน MongoDB
def fetch_users():
    all_users = []
    for ip in DEVICE_IPS:
        conn = connect_zk(ip)  # เชื่อมต่อกับอุปกรณ์แต่ละเครื่อง
        if conn:
            try:
                users = conn.get_users()
                if not users:
                    print(f"No users found on the device at {ip}.")
                else:
                    print(f"Fetched {len(users)} users from ZKTeco at {ip}.")
                    for user in users:
                        all_users.append({
                            'user_id': user.user_id,
                            'name': user.name or "Unnamed",
                            'device_ip': ip  # เพิ่มข้อมูล IP ของอุปกรณ์
                        })
            except Exception as e:
                print(f"Error fetching users from device at {ip}: {e}")
            finally:
                conn.enable_device()
                conn.disconnect()
                print(f"Disconnected from ZKTeco at {ip}.")
        else:
            print(f"Skipping device at {ip} due to connection issues.")

    # อัปเดตข้อมูลใน MongoDB
    try:
        users_collection = mongo.db.users
        users_collection.delete_many({})  # ลบข้อมูลเก่า
        if all_users:
            users_collection.insert_many(all_users)
            print(f"Inserted {len(all_users)} users into MongoDB.")

        # ดึงข้อมูลทั้งหมดจาก MongoDB และแปลง ObjectId เป็น str
        users_from_db = users_collection.find()
        response_data = [
            {
                "_id": str(user["_id"]),
                "user_id": user["user_id"],
                "name": user["name"],
                "device_ip": user.get("device_ip")  # เพิ่ม IP ของอุปกรณ์ในผลลัพธ์
            }
            for user in users_from_db
        ]

        print("Users successfully fetched and serialized.")
        return response_data, 200
    except Exception as e:
        print(f"Error updating MongoDB: {e}")
        return {"error": str(e)}, 500
