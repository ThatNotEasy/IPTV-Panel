from flasgger import swag_from
from modules.users import USERS
from modules.config import setup_config
from flask import Blueprint, request, jsonify, render_template, url_for, Response, abort, redirect
from flask_cors import cross_origin, CORS
from routes.authorized import admin_password, AUTHORIZED
from modules.logging import setup_logging
from modules.bot import send_message
from base64 import urlsafe_b64encode
from hashlib import pbkdf2_hmac
from cryptography.fernet import Fernet
from modules.helper import detect_sniffing, get_external_ip, rate_limit, manage_ip_lists, BLACKLISTED_IPS, check_client_certificate, suspicious_headers, geoip_lookup, COUNTRY_CODE
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os

config = setup_config()
logging = setup_logging()

ADMIN_PASS = config["ADMIN"]["PASSWORD"]

users_bp = Blueprint('users_bp', __name__)
CORS(users_bp)


# ============================================================================================================================================ #

@users_bp.route('/add_user', methods=['POST'])
@cross_origin()
# @jwt_required()
# @admin_password()
@swag_from('../templates/swagger/users/add_user.yml')
def add_user():
    if not request.is_json:
        return jsonify({"responseData": "missing required field!"}), 400
    
    data = request.get_json()
    username = data.get('username', None)
    
    if not username:
        return jsonify({"responseData": "missing required field!"}), 400
    
    users = USERS()
    users.username = username
    return users.add_users()

# ============================================================================================================================================ #

@users_bp.route('/user_list', methods=['GET'])
@cross_origin()
@jwt_required()
@admin_password()
@swag_from('../templates/swagger/users/get_all_user.yml')
def get_all_user():
    users = USERS()
    return users.get_all_users()

# ============================================================================================================================================ #

@users_bp.route('/<user_id>', methods=['GET'])
@cross_origin()
@jwt_required()
@admin_password()
@swag_from('../templates/swagger/users/get_single_user.yml')
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
@swag_from('../templates/swagger/users/delete_single_user.yml')
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
@swag_from('../templates/swagger/users/update_single_user.yml')
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
@swag_from('../templates/swagger/users/get_playlist.yml')
@rate_limit
def get_playlist(user_id):
    # Log the initial request
    logging.info(f"Received request for playlist from User ID: {user_id}")

    user_agent = request.headers.get('User-Agent', '')
    encoding = request.headers.get('accept-encoding', '')

    client_ip = request.headers.get('X-Forwarded-For', request.headers.get('X-Real-IP', request.remote_addr))
    if client_ip and ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()

    # Check for blacklisted IP
    if client_ip in BLACKLISTED_IPS:
        logging.warning(f"Blocked access attempt from blacklisted IP: {client_ip}")
        return abort(403, description="Forbidden Ke? Kesian"), 403

    # Country Check
    country_code = geoip_lookup(client_ip)
    if country_code not in COUNTRY_CODE:
        logging.warning(f"Access denied for IP {client_ip}: Country {country_code} is not allowed.")
        send_message(
            f"🌟 User Activity Alert 🌟\n\n"
            f"🔹 User ID: {user_id}\n"
            f"🔹 IP Address: {client_ip}\n"
            f"🔹 User-Agent: {user_agent}\n"
            f"🔹 Encoding: {encoding}\n"
            f"🔹 Activity: Access denied for IP {client_ip}: Country {country_code} is not allowed."
        )
        return jsonify({'message': 'Access denied: Only Malaysian and Spanish IPs are allowed.'}), 403

    # Manage IP lists
    manage_ip_lists(client_ip)
    logging.info(f"User Access: User ID: {user_id} | Client IP: {client_ip} | User-Agent: {user_agent} | Encoding: {encoding}")

    # Check for sniffing
    if detect_sniffing(user_agent, client_ip):
        manage_ip_lists(client_ip, suspicious=True)
        logging.warning(f"Blocking suspicious request from {client_ip} with User-Agent: {user_agent}")
        return redirect(url_for('templates_bp.serve_pepes')), 301

    # User-Agent validation
    if not (user_agent.startswith("OTT") or user_agent.startswith("axios/1.6.2")):
        logging.info(f"Invalid User-Agent for user {user_id} from {client_ip}: {user_agent}")
        return redirect(url_for('templates_bp.serve_pepes')), 301

    # Check for missing user_id
    if not user_id:
        logging.error(f"Missing user_id in request from {client_ip}")
        return jsonify({"responseData": "Cari apa?"}), 400

    users = USERS()
    users.user_id = user_id
    users.ip_address = client_ip
    users.device = user_agent

    # Validate user ID
    if not users.check_user_id():
        logging.warning(f"User ID {user_id} not found for request from {client_ip}")
        return jsonify({"responseData": "Abuse eh?"}), 404

    active_session = users.get_active_session()
    
    if active_session is None:
        update_result = users.update_user_activity()
        if update_result["status"] == "error":
            logging.error(f"Error updating user activity for {user_id}: {update_result}")
            return jsonify({"responseData": update_result}), 500
        active_session = users.get_active_session()

    # Ensure active_session is not None before accessing it
    if active_session and (active_session['ip_address'] != client_ip or active_session['device'] != user_agent):
        logging.warning(f"Multiple login attempt detected for user {user_id} from {client_ip}. "
                        f"Active session IP: {active_session['ip_address']}, Device: {active_session['device']}")
        return jsonify({"responseData": "Multiple login attempts detected!"}), 403

    # Serve the playlist
    playlist_file_path = os.path.join("templates", "playlist.m3u")
    if not os.path.isfile(playlist_file_path):
        logging.error(f"Playlist file not found for user {user_id} from {client_ip}")
        return abort(404, description="Playlist not found")

    try:
        with open(playlist_file_path, 'r', encoding='utf-8') as file:
            playlist_content = file.read()
    except IOError as e:
        logging.error(f"Error reading playlist file for user {user_id} from {client_ip}: {e}")
        return abort(500, description="Internal Server Error")

    logging.info(f"Successfully served playlist to user {user_id} from {client_ip}")
    return Response(playlist_content, mimetype='text/plain; charset=utf-8')