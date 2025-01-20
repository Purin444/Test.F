from flask import Blueprint, request, jsonify
from controllers.holiday_controller import get_holidays_from_db, save_holidays_to_db

holiday_bp = Blueprint('holiday', __name__, url_prefix='/api')

@holiday_bp.route('/holidays', methods=['GET'])
def get_holidays():
    """ ดึงข้อมูลวันหยุดจาก MongoDB """
    data, status = get_holidays_from_db()
    return jsonify(data), status

@holiday_bp.route('/saveAllHolidays', methods=['POST'])
def save_holidays():
    """ บันทึกข้อมูลวันหยุดทั้งหมดลง MongoDB """
    holidays = request.json
    if not holidays:
        return jsonify({"error": "No data provided"}), 400
    
    data, status = save_holidays_to_db(holidays)
    return jsonify(data), status
