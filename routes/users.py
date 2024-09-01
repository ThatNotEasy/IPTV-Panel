from flasgger import swag_from
from modules.users import USERS
from modules.config import setup_config
from flask import Blueprint, request, jsonify, render_template, url_for, Response, abort, redirect
from flask_cors import cross_origin, CORS
from routes.authorized import admin_password
from modules.authorized import AUTHORIZED
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os

config = setup_config()
ADMIN_PASS = config["ADMIN"]["PASSWORD"]

users_bp = Blueprint('users_bp', __name__)
CORS(users_bp)


# ============================================================================================================================================ #

@users_bp.route('/add_user', methods=['POST'])
@cross_origin()
@jwt_required()
@admin_password()
@swag_from('../swagger/users/add_user.yml')
def add_user():
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
    return users.add_users()

# ============================================================================================================================================ #

@users_bp.route('/user_list', methods=['GET'])
@cross_origin()
@jwt_required()
@admin_password()
@swag_from('../swagger/users/get_all_user.yml')
def get_all_user():
    users = USERS()
    return users.get_all_users()

# ============================================================================================================================================ #

@users_bp.route('/<user_id>', methods=['GET'])
@cross_origin()
@jwt_required()
@admin_password()
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
@admin_password()
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
@admin_password()
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

@users_bp.route('/<user_id>/playlist', methods=['GET'])
@cross_origin()
# @jwt_required()
@swag_from('../swagger/users/get_playlist.yml')
def get_playlist(user_id):
    if not user_id:
        return jsonify({"responseData": "Missing required field!"}), 400

    users = USERS()
    users.user_id = user_id
    
    user_exists = users.check_user_id(user_id)
    if not user_exists:
        return jsonify({"responseData": "User ID not found!"}), 404

    # Detecting User-Agent and Client IP
    user_agent = request.headers.get('User-Agent')
    if "Mozilla/5.0" in user_agent:
        return redirect(url_for('static', filename='img/pepes.gif'))
        
    client_ip = request.remote_addr

    # Log or handle the detected User-Agent and IP address
    print(f"User-Agent: {user_agent}")
    print(f"Client IP: {client_ip}")

    # Optional: Log or restrict based on user-agent and IP
    # You can also store this information in logs or take specific actions based on it

    playlist_file_path = os.path.join("templates", "playlist.m3u")
    if not os.path.isfile(playlist_file_path):
        return abort(404, description="Playlist not found")

    with open(playlist_file_path, 'r') as file:
        playlist_content = file.read()

    return Response(playlist_content, mimetype='text/plain')