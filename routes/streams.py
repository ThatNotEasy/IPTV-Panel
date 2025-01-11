from flasgger import swag_from
from modules.streams import STREAMS
from flask import Blueprint, request, jsonify, render_template, url_for
from flask_cors import cross_origin, CORS
from flask_jwt_extended import jwt_required

streams_bp = Blueprint('streams_bp', __name__)
CORS(streams_bp)

# ============================================================================================================================================ #

@streams_bp.route('/playlist_generator', methods=['POST'])
@cross_origin()
@jwt_required()
@swag_from('../templates/swagger/streams/playlist_generator.yml')
def playlist():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in the request"}), 400

    data = request.get_json()
    playlist_format = data.get('playlistFormatter')
    channel_name = data.get('name')
    channel_thumbnail = data.get('thumbnailUrl')
    channel_mpd = data.get('mpdUrl')
    genre_type = data.get('genreType')
    channel_group = data.get('groupName')
    kid = data.get('kid')
    key = data.get('key')
    referer = data.get('referer')

    if not all([playlist_format, channel_name, channel_thumbnail, channel_mpd, channel_group, genre_type, kid, key, referer]):
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        iptv = IPTV()
        iptv.channel_name = channel_name
        iptv.channel_thumbnail = channel_thumbnail
        iptv.mpd_url = channel_mpd
        iptv.channel_group = channel_group
        iptv.genre_type = genre_type
        iptv.referer = referer
        iptv.kid = kid
        iptv.key = key

        if playlist_format == "1":
            result = iptv._generate_format_1_playlist()
        elif playlist_format == "2":
            result = iptv._generate_format_2_playlist()
        else:
            return jsonify({"error": "Invalid playlist format specified"}), 400

        return jsonify(result)

    except Exception as e:
        logging.error(f"Internal server error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
    
# ============================================================================================================================================ #

@streams_bp.route('/downloadPlaylist', methods=['GET'])
@cross_origin()
@jwt_required()
def download_playlist():
    file_path = request.args.get('filePath')
    
    if not file_path:
        return jsonify({"error": "File path parameter is required"}), 400
    
    safe_file_name = os.path.basename(file_path)
    full_path = os.path.join('templates/generator', safe_file_name)
    
    if not os.path.exists(full_path):
        return jsonify({"error": "File not found"}), 404
    
    logging.info(f"File found and ready to be downloaded: {full_path}")
    return send_file(full_path, as_attachment=True, download_name=safe_file_name)

# ============================================================================================================================================ #

@streams_bp.route('/epg_generator', methods=['POST'])
@cross_origin()
@jwt_required()
@swag_from('../templates/swagger/streams/generate_epg.yml')
def generate_epg_api():
    data = request.json

    if not data or 'channels' not in data or 'programs' not in data:
        return jsonify({"error": "Missing channels or programs data"}), 400

    channels = data['channels']
    programs = data['programs']

    epg_generator = IPTV()

    output_file_name = 'epg.xml'
    output_file_path = os.path.join('templates/generator', output_file_name)
    
    epg_generator.output_file = output_file_path
    result = epg_generator.generate_epg(channels, programs)

    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(result['responseData'])

    if not os.path.exists(output_file_path):
        return jsonify({"error": "Failed to generate EPG file"}), 500

    logging.info(f"EPG file generated and ready to be downloaded: {output_file_path}")
    return send_file(output_file_path, as_attachment=True, download_name=os.path.basename(output_file_path))


@streams_bp.route('/get_streams', methods=['GET'])
@cross_origin()
@swag_from('../templates/swagger/streams/get_streams.yml')
def stream():
    streams = STREAMS()
    return streams.get_all_streams()

# ============================================================================================================================================ #

@streams_bp.route('/<stream_id>', methods=['GET'])
@cross_origin()
@swag_from('../templates/swagger/streams/get_single_streams.yml')
def get_single_stream(stream_id):
    if not stream_id:
        return jsonify({"responseData": "missing required field!"}), 400
    
    streams = STREAMS()
    streams.stream_id = stream_id
    return streams.get_single_streams()

# ============================================================================================================================================ #

@streams_bp.route('/<stream_id>', methods=['PUT'])
@cross_origin()
@swag_from('../templates/swagger/streams/manage_streams.yml')
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
@swag_from('../templates/swagger/streams/add_stream.yml')
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