from flask import Blueprint, jsonify
from controllers.user_controller import fetch_users

user_bp = Blueprint('user', __name__, url_prefix='/api')

@user_bp.route('/users', methods=['GET'])
def get_users():
    data, status = fetch_users()
    return jsonify(data), status
