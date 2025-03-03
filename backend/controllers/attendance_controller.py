import time
from zk import ZK
from extensions import mongo
import os
import platform

DEVICE_IPS = ['192.168.1.220']

# ✅ ใช้ Dictionary เก็บผล Ping เพื่อป้องกัน Ping ซ้ำ
ping_status = {}

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
    zk = ZK(ip, port=4370, timeout=0.3)  # ปรับ timeout ให้เร็วขึ้น
    try:
        conn = zk.connect()
        conn.disable_device()
        print(f"✅ Connected to ZKTeco at {ip}")
        return conn
    except Exception as e:
        print(f"⚠️ Error connecting to ZK device at {ip}: {e}")
        return None

# ฟังก์ชันดึงข้อมูล Attendance Logs
def fetch_attendance_logs(start_date=None, end_date=None):
    """ ✅ รองรับ `start_date` และ `end_date` ถ้ามี """
    all_logs = []
    for ip in DEVICE_IPS:
        print(f"🔍 Checking device at {ip}")  # เพิ่ม debug line
        if not is_device_reachable(ip):
            print(f"❌ Skipping {ip} due to ping failure. (fetch_attendance_logs)")
            continue  # ✅ ข้ามไปเลย ไม่ต้องเสียเวลาพยายามเชื่อมต่อ
        
        time.sleep(2)  # ✅ หน่วงเวลาก่อนเชื่อมต่อใหม่
        
        conn = connect_zk(ip)
        if conn:
            try:
                logs = conn.get_attendance()
                if logs:
                    print(f"✅ Fetched {len(logs)} attendance logs from {ip}.")
                    for log in logs:
                        all_logs.append({
                            'user_id': log.user_id,
                            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            'status': log.punch,
                            'device_ip': ip
                        })
                else:
                    print(f"⚠️ No attendance logs found on {ip}.")
            except Exception as e:
                print(f"⚠️ Error fetching logs from {ip}: {e}")
            finally:
                conn.enable_device()
                conn.disconnect()
                print(f"🔌 Disconnected from {ip}.")
        else:
            print(f"⚠️ Skipping {ip} due to connection issues. (fetch_attendance_logs)")

    # ✅ บันทึกใน MongoDB ถ้ามีข้อมูลใหม่
    try:
        attendance_collection = mongo.db.attendance
        if all_logs:
            attendance_collection.delete_many({})
            attendance_collection.insert_many(all_logs)
            print(f"✅ Inserted {len(all_logs)} logs into MongoDB.")

        # ✅ สร้าง Query ตาม `start_date` และ `end_date`
        query = {}
        if start_date and end_date:
            query["timestamp"] = {
                "$gte": f"{start_date} 00:00:00",
                "$lte": f"{end_date} 23:59:59"
            }
            print(f"📌 Filtering attendance between {start_date} and {end_date}")

        attendance_from_db = attendance_collection.find(query)

        response_data = [
            {
                "_id": str(att["_id"]),
                "user_id": att["user_id"],
                "timestamp": att["timestamp"],
                "status": att["status"],
                "device_ip": att.get("device_ip")
            }
            for att in attendance_from_db
        ]
        print(f"✅ Retrieved {len(response_data)} attendance logs from MongoDB.")
        return response_data, 200

    except Exception as e:
        print(f"❌ Error updating MongoDB: {e}")
        return {"error": str(e)}, 500

