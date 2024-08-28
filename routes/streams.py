from flasgger import swag_from
from modules.streams import STREAMS
from flask import Blueprint, request, jsonify, render_template, url_for
from flask_cors import cross_origin, CORS
from flask_jwt_extended import jwt_required

streams_bp = Blueprint('streams_bp', __name__)
CORS(streams_bp)

@streams_bp.route('/get_streams', methods=['GET'])
@cross_origin()
@swag_from('../swagger/streams/get_streams.yml')
def stream():
    streams = STREAMS()
    return streams.get_streams()

@streams_bp.route('/manage_streams/<stream_id>', methods=['POST'])
@cross_origin()
@swag_from('../swagger/streams/manage_streams.yml')
def manage_stream(stream_id):
    if not stream_id:
        return jsonify({"responseData": "missing required field!"}), 400
    
    if not request.is_json:
        return jsonify({"responseData": "missing required field!"}), 400
    
    data = request.get_json()
    manifest_url = data.get('manifest_url', None)
    kid_key = data.get('kid_key', None)
    
    streams = STREAMS()
    streams.manifest_url = manifest_url
    streams.kid_key = kid_key
    return streams.manage_streams()