from flasgger import swag_from
from modules.reseller import RESELLER
from modules.config import setup_config
from flask import Blueprint, request, jsonify, render_template, url_for
from flask_cors import cross_origin, CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

config = setup_config()
ADMIN_PASS = config["ADMIN"]["PASSWORD"]

reseller_bp = Blueprint('reseller_bp',  __name__, template_folder="templates", static_folder="templates/static", static_url_path="/static")
CORS(reseller_bp)

@reseller_bp.route('/reseller_list', methods=['GET'])
@cross_origin()
@jwt_required()
@swag_from('../templates/swagger/resellers/get_all_reseller.yml')
def get_all_reseller():
    reseller = RESELLER()
    return reseller.get_all_resellers()

# ============================================================================================================================================ #

@reseller_bp.route('/<reseller_id>', methods=['GET'])
@cross_origin()
@jwt_required()
@swag_from('../templates/swagger/resellers/get_single_reseller.yml')
def get_single_reseller(reseller_id):
    if not reseller_id:
        return jsonify({"status": "error", "message": "Reseller ID is required"}), 400
    
    reseller = RESELLER()
    reseller.user_id = reseller_id
    return reseller.get_single_resellers()

# ============================================================================================================================================ #

@reseller_bp.route('/<reseller_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
@swag_from('../templates/swagger/resellers/delete_single_reseller.yml')
def delete_single_user(reseller_id):
    if not reseller_id:
        return jsonify({"responseData": "missing required field!"}), 400
    
    reseller = RESELLER()
    reseller.user_id = reseller_id
    return reseller.delete_resellers()

# ============================================================================================================================================ #

@reseller_bp.route('/add_reseller', methods=['POST'])
@cross_origin()
@jwt_required()
@swag_from('../templates/swagger/resellers/add_new_reseller.yml')
def add_new_reseller():
    if not request.is_json:
        return jsonify({"responseData": "missing required field!"}), 400
    
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)
    
    if not username or not password:
        return jsonify({"responseData": "missing required field!"}), 400
    
    reseller = RESELLER()
    reseller.username = username
    reseller.password = password
    return reseller.add_new_resellers()