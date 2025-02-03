from flask import Blueprint, jsonify, request
from controllers.attendance_controller import fetch_attendance_logs

attendance_bp = Blueprint('attendance', __name__, url_prefix='/api')

@attendance_bp.route('/attendance', methods=['GET'])
def get_attendance():
    """ ✅ รองรับทั้งแบบมีและไม่มี Start/End Date """
    start_date = request.args.get('start')  # 📌 จะเป็น None ถ้าไม่มีการส่ง Query
    end_date = request.args.get('end')

    if not start_date or not end_date:
        print("📌 No start_date or end_date provided. Fetching all attendance logs.")

    data, status = fetch_attendance_logs(start_date, end_date)
    return jsonify(data), status
