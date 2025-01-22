from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from controllers.ot_request_controller import (
    get_ot_requests_from_db,
    save_ot_request_to_db,
    save_accepted_ot_request_to_db,
    get_accepted_ot_requests_from_db,
    delete_accepted_ot_requests_from_db  # ฟังก์ชันที่สามารถใช้งานได้
)

# สร้าง Blueprint สำหรับ OT Request
ot_request_bp = Blueprint('ot_request', __name__, url_prefix='/api/ot-requests')
accepted_ot_bp = Blueprint('accepted_ot_requests', __name__, url_prefix='/api/accepted_ot_requests')

@ot_request_bp.route('/', methods=['GET'])
def get_ot_requests():
    """ ดึงข้อมูล OT Requests ทั้งหมด """
    data, status = get_ot_requests_from_db()
    return jsonify(data), status

@ot_request_bp.route('/', methods=['POST'])
def save_ot_request():
    """ บันทึกข้อมูล OT Request """
    ot_data = request.json
    response, status = save_ot_request_to_db(ot_data)
    return jsonify(response), status

@ot_request_bp.route('/accept', methods=['POST'])
def accept_ot_request():
    """ ย้ายข้อมูล OT Request ไปยัง Accepted OT Requests """
    ot_data = request.json
    try:
        # บันทึกข้อมูลลง Collection Accepted
        accepted_response, accepted_status = save_accepted_ot_request_to_db(ot_data)
        if accepted_status != 201:
            return jsonify({"error": "Failed to save to accepted requests"}), 500

        return jsonify({"message": "OT Request accepted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@accepted_ot_bp.route('/', methods=['GET'])
def get_all_accepted_ot_requests():
    """ ดึงข้อมูลทั้งหมดจาก Collection accepted_ot_requests """
    data, status = get_accepted_ot_requests_from_db()
    return jsonify(data), status

@accepted_ot_bp.route('/', methods=['DELETE'])
def delete_selected_accepted_ot_requests():
    """ ลบข้อมูลที่เลือกใน Collection accepted_ot_requests """
    try:
        data = request.json
        ids = data.get("ids", [])
        response, status = delete_accepted_ot_requests_from_db(ids)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# เพิ่มการตั้งค่า CORS
app = Flask(__name__)
CORS(app)

# ลงทะเบียน Blueprint
app.register_blueprint(ot_request_bp)
app.register_blueprint(accepted_ot_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
