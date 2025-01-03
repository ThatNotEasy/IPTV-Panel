from flasgger import swag_from
from modules.streams import STREAMS
from flask import Blueprint, request, jsonify, render_template, url_for
from flask_cors import cross_origin, CORS
from flask_jwt_extended import jwt_required

streams_bp = Blueprint('streams_bp', __name__)
CORS(streams_bp)

# ============================================================================================================================================ #

@streams_bp.route('/get_streams', methods=['GET'])
@cross_origin()
@swag_from('../swagger/streams/get_streams.yml')
def stream():
    streams = STREAMS()
    return streams.get_all_streams()

# ============================================================================================================================================ #

@streams_bp.route('/<stream_id>', methods=['GET'])
@cross_origin()
@swag_from('../swagger/streams/get_single_streams.yml')
def get_single_stream(stream_id):
    if not stream_id:
        return jsonify({"responseData": "missing required field!"}), 400
    
    streams = STREAMS()
    streams.stream_id = stream_id
    return streams.get_single_streams()

# ============================================================================================================================================ #

@streams_bp.route('/<stream_id>', methods=['PUT'])
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

# ============================================================================================================================================ #

@streams_bp.route('/add_stream', methods=['POST'])
@cross_origin()
@swag_from('../swagger/streams/add_stream.yml')
def add_stream():
    if not request.is_json:
        return jsonify({"responseData": "missing required field!"}), 400
    
    data = request.get_json()
    manifest_url = data.get('manifest_url', None)
    kid_key = data.get('kid_key', None)
    stream_name = data.get('stream_name', None)
    stream_thumbnail = data.get('stream_thumbnail', None)
    
    streams = STREAMS()
    streams.manifest_url = manifest_url
    streams.kid_key = kid_key
    streams.stream_name = stream_name
    streams.stream_thumbnail = stream_thumbnail
    return streams.add_streams()