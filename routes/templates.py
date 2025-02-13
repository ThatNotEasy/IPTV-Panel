from flasgger import swag_from
from flask import Blueprint, request, jsonify, render_template, url_for, send_from_directory
from flask_cors import cross_origin, CORS
from flask_jwt_extended import jwt_required

templates_bp = Blueprint('templates_bp', __name__, template_folder="templates", static_folder="templates/static", static_url_path="/static")
CORS(templates_bp)

@templates_bp.route('/', methods=['GET'])
@cross_origin()
def index():
    return render_template('index.html')

@templates_bp.route('/stream', methods=['GET'])
@cross_origin()
def streams():
    return render_template('index.html')

@templates_bp.route('/pepes', methods=['GET'])
@cross_origin()
def serve_pepes():
    response = send_from_directory('static/img', 'pepes.gif')
    if 'Content-Disposition' in response.headers:
        del response.headers['Content-Disposition']
    response.status_code = 301
    return response

@templates_bp.route('/', methods=['GET'])
@cross_origin()
def home():
    sections = [
        {"name": "Access Control", "description": "Manage blacklist and access control settings.", "emoji": "🔒"},
        {"name": "Authorized", "description": "View and manage authorized clients.", "emoji": "✅"},
        {"name": "Reseller", "description": "Manage reseller accounts and privileges.", "emoji": "🛍️"},
        {"name": "Stream", "description": "Monitor and manage active streams.", "emoji": "📡"},
        {"name": "User", "description": "View and manage user accounts.", "emoji": "👤"},
    ]
    return render_template("home.html", sections=sections)
