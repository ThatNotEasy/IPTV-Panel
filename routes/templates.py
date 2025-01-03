from flasgger import swag_from
from flask import Blueprint, request, jsonify, render_template, url_for, send_from_directory
from flask_cors import cross_origin, CORS
from flask_jwt_extended import jwt_required

templates_bp = Blueprint('templates_bp', __name__)
CORS(templates_bp)

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
