from flasgger import swag_from
from modules.reseller import RESELLER
from modules.config import setup_config
from flask import Blueprint, request, jsonify, render_template, url_for
from flask_cors import cross_origin, CORS
from modules.access_control import ACCESS_CONTROL
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

config = setup_config()
ADMIN_PASS = config["ADMIN"]["PASSWORD"]

access_control_bp = Blueprint('access_control_bp', __name__, template_folder="templates", static_folder="templates/static", static_url_path="/static")
CORS(access_control_bp)

@access_control_bp.route('/blacklist', methods=['GET'])
@cross_origin()
@jwt_required()
@swag_from('../templates/swagger/access_control/blacklist.yml')
def blacklist():
    access_control = ACCESS_CONTROL()
    return access_control.get_blacklist()

@access_control_bp.route('/blacklist', methods=['POST'])
@cross_origin()
@jwt_required()
@swag_from('../templates/swagger/access_control/add_blacklist.yml')
def add_blacklist():
    if not request.is_json:
        return jsonify({"responseData": "missing required field!"}), 400
    
    data = request.get_json()
    ip_address = data.get('ip_address', None)
    asn_address = data.get('asn_address', None)
    agent = data.get('user_agent', None)
    
    if not ip_address or not asn_address or not agent:
        return jsonify({"responseData": "missing required field!"}), 400
    
    access_control = ACCESS_CONTROL()
    access_control.ip_address = ip_address
    access_control.asn_address = asn_address
    access_control.user_agent = agent
    return access_control.add_blacklists()