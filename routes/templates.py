from flasgger import swag_from
from flask import Blueprint, request, jsonify, render_template, url_for
from flask_cors import cross_origin, CORS
from flask_jwt_extended import jwt_required

templates_bp = Blueprint('templates_bp', __name__)
CORS(templates_bp)

@templates_bp.route('/stream', methods=['GET'])
@cross_origin()
def streams():
    return render_template('index.html')