from flasgger import swag_from
from modules.users import USERS
from modules.config import setup_config
from flask import Blueprint, request, jsonify, render_template, url_for
from flask_cors import cross_origin, CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

config = setup_config()
ADMIN_PASS = config["ADMIN"]["PASSWORD"]

users_bp = Blueprint('users_bp', __name__)
CORS(users_bp)

@users_bp.route('/register', methods=['POST'])
@cross_origin()
@jwt_required()
@swag_from('../swagger/users/signup.yml')
def user_signup():
    if not request.is_json:
        return jsonify({"responseData": "missing required field!"}), 400
    
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)
    email = data.get('email', None)
    
    if not username or not password or not email:
        return jsonify({"responseData": "missing required field!"}), 400
    
    users = USERS()
    users.username = username
    users.password = password
    users.email = email
    return users.register()


# ============================================================================================================================================ #

@users_bp.route('/login', methods=['POST'])
@cross_origin()
# @jwt_required()
@swag_from('../swagger/users/login.yml')
def user_login():
    if not request.is_json:
        return jsonify({"responseData": "missing required field!"}), 400
    
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)
    
    if not username or not password:
        return jsonify({"responseData": "missing required field!"}), 400
    
    users = USERS()
    users.username = username
    users.password = password
    return users.login()

# ============================================================================================================================================ #

@users_bp.route('/user_list', methods=['GET'])
@cross_origin()
@jwt_required()
@swag_from('../swagger/users/get_all_user.yml')
def get_all_user():
    users = USERS()
    return users.get_all_users()

# ============================================================================================================================================ #

@users_bp.route('/<user_id>', methods=['GET'])
@cross_origin()
@jwt_required()
@swag_from('../swagger/users/get_single_user.yml')
def get_single_user(user_id):
    if not user_id:
        return jsonify({"responseData": "missing required field!"}), 400
    
    users = USERS()
    users.user_id = user_id
    return users.get_single_users()

# ============================================================================================================================================ #

@users_bp.route('/<user_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
@swag_from('../swagger/users/delete_single_user.yml')
def delete_single_user(user_id):
    if not user_id:
        return jsonify({"responseData": "missing required field!"}), 400
    
    users = USERS()
    users.user_id = user_id
    return users.delete_single_users()

# ============================================================================================================================================ #

@users_bp.route('/<user_id>', methods=['PUT'])
@cross_origin()
@jwt_required()
@swag_from('../swagger/users/update_single_user.yml')
def update_single_user(user_id):
    if not user_id:
        return jsonify({"responseData": "missing required field!"}), 400
    
    if not request.is_json:
        return jsonify({"responseData": "missing required field!"}), 400
    
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)
    email = data.get('email', None)
    role = data.get('role', None)
    
    if not username or not password or not email or not role:
        return jsonify({"responseData": "missing required field!"}), 400
    
    users = USERS()
    users.user_id = user_id
    users.username = username
    users.password = password
    users.email = email
    users.role = role
    return users.update_single_users()

# ============================================================================================================================================ #

# @users_bp.route('/user/<user_id>', methods=['PUT'])
# @cross_origin()
# @jwt_required()
# @swag_from('/swagger/users/update_single_user.yml')
# def update_user_data(user_id):
#     uuid = request.args.get('uuid')
#     password = request.args.get('password')

#     if not uuid or not password:
#         return jsonify({'error': 'Both uuid and password are required.'}), 400

#     if password != ADMIN_PASS:
#         return jsonify({'error': 'Incorrect password.'}), 400

#     user_data = get_user_status(uuid)

#     if user_data:
#         return jsonify(user_data)
    
#     return jsonify({'error': 'User not found.'}), 404