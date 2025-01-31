from zk import ZK
from extensions import mongo

# รายการ IP ของอุปกรณ์ ZKTeco
DEVICE_IPS = [
    '192.168.1.220',
    # '192.168.1.221',  # เพิ่ม IP อุปกรณ์ที่สอง
    # '192.168.1.222',  # เพิ่ม IP อุปกรณ์ที่สาม
]

def connect_zk(ip):
    """ เชื่อมต่อ ZKTeco """
    zk = ZK(ip, port=4370, timeout=1)  # ลดเวลารอให้เหลือ 1 วินาที
    try:
        conn = zk.connect()
        conn.disable_device()
        print(f"Connected to ZKTeco device at {ip}")
        return conn
    except Exception as e:
        print(f"Error connecting to ZK device at {ip}: {e}")
        return None

def fetch_attendance_logs():
    """ ดึงข้อมูล Attendance สดจากหลาย ZKTeco และบันทึกลง MongoDB """
    all_logs = []
    for ip in DEVICE_IPS:
        conn = connect_zk(ip)
        if conn:
            try:
                # ดึงข้อมูล Attendance จากอุปกรณ์
                logs = conn.get_attendance()
                if not logs:
                    print(f"No attendance logs found on device at {ip}.")
                else:
                    print(f"Fetched {len(logs)} attendance logs from device at {ip}.")
                    for log in logs:
                        all_logs.append({
                            'user_id': log.user_id,
                            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            'status': log.punch,
                            'device_ip': ip  # เพิ่ม IP ของอุปกรณ์ในข้อมูล
                        })
            except Exception as e:
                print(f"Error fetching logs from device at {ip}: {e}")
            finally:
                conn.enable_device()
                conn.disconnect()
                print(f"Disconnected from ZKTeco device at {ip}.")
        else:
            print(f"Skipping device at {ip} due to connection issues.")

    # บันทึกข้อมูลลง MongoDB
    try:
        attendance_collection = mongo.db.attendance
        
        if all_logs:
            attendance_collection.delete_many({})
            attendance_collection.insert_many(all_logs)
            print(f"Inserted {len(all_logs)} attendance logs into MongoDB.")

        # แปลง ObjectId และดึงข้อมูลคืนจาก MongoDB
        attendance_from_db = attendance_collection.find()
        response_data = [
            {
                "_id": str(att["_id"]),
                "user_id": att["user_id"],
                "timestamp": att["timestamp"],
                "status": att["status"],
                "device_ip": att.get("device_ip")  # เพิ่ม IP ของอุปกรณ์ในผลลัพธ์
            }
            for att in attendance_from_db
        ]
        return response_data, 200
    except Exception as e:
        print(f"Error updating MongoDB: {e}")
        return {"error": str(e)}, 500
