from flask import Blueprint, jsonify
from controllers.attendance_controller import fetch_attendance_logs

# กำหนด Blueprint สำหรับ Attendance Routes
attendance_bp = Blueprint('attendance', __name__, url_prefix='/api')

@attendance_bp.route('/attendance', methods=['GET'])
def get_attendance():
    """ เรียก Controller เพื่อดึงข้อมูล Attendance """
    data, status = fetch_attendance_logs()
    return jsonify(data), status
