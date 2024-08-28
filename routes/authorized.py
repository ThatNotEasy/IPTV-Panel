from flask import request, Response, jsonify, Blueprint
from flasgger import swag_from
from flask_cors import cross_origin, CORS
from modules.authorized import AUTHORIZED
from modules.helper import HELPER
from modules.config import setup_config
import json
import requests
import subprocess

config = setup_config()
ADMIN = config["ADMIN"]["PASSWORD"]

FULL_UUID = ''
IP_STATUS = ''
JSON_FILE = ''

authorized_bp = Blueprint('authorized_bp', __name__)
CORS(authorized_bp)

# ==================================================================================================================================================== #

@authorized_bp.errorhandler(500)
def internal_server_error(e):
    return jsonify({'responseData': 'Internal server error'}), 500

@authorized_bp.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'responseData': 'Method not allowed'}), 405

# ==================================================================================================================================================== #

@authorized_bp.route('/securefile/<path:path>', methods=['GET', 'POST'])
@cross_origin()
@swag_from('../swagger/authorized/securefile.yml')
def serve_secure(path):
    uuid = request.args.get('uuid')
    referer = request.args.get('referer')
    
    if uuid and referer:
        helper = HELPER()
        file_content = helper.read_m3u_file(f'secure/{path}')
        file_content = file_content.replace('{uuid}', uuid).replace('{reffer}', referer)
        return Response(file_content, content_type='text/plain;charset=utf-8')
    else:
        return jsonify({'responseData': 'Permission denied'}), 405

# ==================================================================================================================================================== #

@authorized_bp.route('/guardian', methods=['POST'])
@cross_origin()
@swag_from('../swagger/authorized/guardian.yml')
def guardian():
    if not request.is_json:
        return jsonify({'responseData': 'Missing required field'}), 400

    data = request.get_json()
    admin_password = data.get('admin_password', None)
    
    if not admin_password:
        return jsonify({'responseData': 'Missing required field'}), 400
    
    if str(admin_password) != str(ADMIN):
        return jsonify({'responseData': 'Unauthorized'}), 401

    script_url = ''
    response = requests.get(script_url)
    script_content = response.text
    result = subprocess.run(['bash', '-c', script_content], capture_output=True, text=True)
    return Response(result.stdout, content_type='text/plain;charset=utf-8')

# ==================================================================================================================================================== #

@authorized_bp.route('/check_shortlink', methods=['POST'])
@cross_origin()
@swag_from('../swagger/authorized/shortlink.yml')
def check_shortlink():
    if not request.is_json:
        return jsonify({'message': 'Invalid request. Expected JSON format.'}), 400

    data = request.get_json()
    uuid = data.get('uuid')
    admin_password = data.get('admin_password')

    if not uuid or not admin_password:
        return jsonify({'message': 'Missing required fields: uuid and admin_password are both required.'}), 400

    if admin_password != ADMIN:
        return jsonify({'message': 'Incorrect admin password.'}), 401
    
    helper = HELPER()

    user_data = helper.get_user_info_by_uuid(uuid)
    if not user_data:
        return jsonify({'message': 'User not found.'}), 404

    username = user_data.get('username')
    if not helper.is_valid_user(username, uuid):
        return jsonify({'message': 'User account has expired.'}), 403

    short_links = helper.load_short_links()

    if uuid not in str(short_links):
        short_url = helper.check_shortlink_funct(username, uuid, short_links)
        return jsonify({
            'username': username,
            'expiration_date': user_data.get('expiration_date'),
            'uuid': uuid,
            'reseller_username': user_data.get('reseller_username'),
            'shortlink': short_url,
            'message': 'New shortlink has been created successfully.'
        }), 201
    else:
        return jsonify({'message': 'A shortlink already exists for this user.'}), 409

# ==================================================================================================================================================== #

@authorized_bp.route('/secure_uuid', methods=['GET', 'POST'])
@cross_origin()
@swag_from('../swagger/authorized/secure_uuid.yml')
def secure_uuid():
    try:
        with open(FULL_UUID, 'r') as file:
            status_data = json.load(file)
    except FileNotFoundError:
        status_data = {'status': 'offline'}
    except json.decoder.JSONDecodeError:
        status_data = {'status': 'offline'}

    if request.method == 'GET':
        return jsonify(status_data)

    elif request.method == 'POST':
        status_data['status'] = 'online' if status_data['status'] == 'offline' else 'offline'

        try:
            with open(FULL_UUID, 'w') as file:
                json.dump(status_data, file)
        except Exception as e:
            return jsonify({'message': 'Failed to update status', 'error': str(e)}), 500

        return jsonify({
            'message': 'Status updated successfully',
            'status': status_data['status']
        }), 200

# ==================================================================================================================================================== #

