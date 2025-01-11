import requests, uuid, jwt, datetime
from flask import jsonify
from modules.helper import generate_stream_id
from modules.logging import setup_logging
from modules.sqlite import SQLITE

class STREAMS:
    def __init__(self):
        self.stream_id = None
        self.stream_name = None
        self.stream_thumbnail = None
        self.manifest_url = None
        self.kid_key = None
        self.server = None
        self.speed = None
        self.max_connection = None
        self.logging = setup_logging()
        
# ============================================================================================================================================ #

    def get_all_streams(self):
        query = "SELECT * FROM streams;"
        db = SQLITE()
        result = db.query(sql=query)
        db.close()
        if result:
            return jsonify({"responseData": result}), 200
        else:
            response_data = {"status": "success", "message": "No streams found."}
            return jsonify({"responseData": response_data}), 400

# ============================================================================================================================================ #

    def get_single_streams(self):
        query = "SELECT * FROM streams WHERE stream_id = ?;"
        db = SQLITE()
        result = db.query(sql=query, args=(self.stream_id,))
        db.close()
        if result:
            return jsonify({"responseData": result}), 200
        else:
            response_data = {"status": "success", "message": "No streams found."}
            return jsonify({"responseData": response_data}), 400

# ============================================================================================================================================ #

    def add_streams(self):
        db = SQLITE()
        try:
            self.stream_id = generate_stream_id()
            query_check = "SELECT * FROM streams WHERE stream_id = ?;"
            result = db.query(sql=query_check, args=(self.stream_id,))
            if not result:
                query_insert = """
                    INSERT INTO streams 
                    (stream_id, manifest_url, kid_key, stream_name, stream_thumbnail) 
                    VALUES (?, ?, ?, ?, ?);
                """
                db.execute(sql=query_insert, args=(self.stream_id, self.manifest_url, self.kid_key, self.stream_name, self.stream_thumbnail))
                db.commit()
                response_data = {"status": "success", "message": "Stream added successfully."}
                return jsonify({"responseData": response_data}), 200
            else:
                response_data = {"status": "error", "message": "Stream already exists."}
                return jsonify({"responseData": response_data}), 400
        except Exception as e:
            self.logging.debug(e)
            response_data = {"status": "error", "message": "internal server error."},
            return jsonify({"responseData": response_data}), 500
        finally:
            db.close()

# ============================================================================================================================================ #

    def delete_stream(self):
        db = SQLITE()
        try:
            query_check = "SELECT * FROM streams WHERE stream_id = ?;"
            result = db.query(sql=query_check, args=(self.stream_id,))

            if result:
                query_delete = "DELETE FROM streams WHERE stream_id = ?;"
                db.execute(sql=query_delete, args=(self.stream_id,))
                db.commit()

                response = {
                    "status": "success",
                    "message": "Successfully deleted the stream.",
                    "responseData": {"stream_id": self.stream_id}
                }
            else:
                response = {
                    "status": "error",
                    "message": "No stream found with the provided stream_id.",
                    "responseData": None
                }
        except Exception as e:
            response = {
                "status": "error",
                "message": f"An error occurred while deleting the stream: {str(e)}",
                "responseData": None
            }
        finally:
            db.close()
            
        return jsonify(response)

# ============================================================================================================================================ #

    def manage_streams(self):
        query = "SELECT * FROM streams WHERE stream_id = ?;"
        db = SQLITE()
        
        try:
            result = db.query(sql=query, args=(self.stream_id,))
            
            if not result:
                # Stream not found
                return jsonify({
                    "status": "error",
                    "message": "Stream not found.",
                    "responseData": None
                }), 404
            
            update_query = "UPDATE streams SET manifest_url = ?, kid_key = ? WHERE stream_id = ?;"
            db.execute(sql=update_query, args=(self.manifest_url, self.kid_key, self.stream_id))
            
            return jsonify({
                "status": "success",
                "message": "Stream updated successfully.",
                "responseData": {
                    "stream_id": self.stream_id,
                    "manifest_url": self.manifest_url,
                    "kid_key": self.kid_key
                }
            })
        
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"An error occurred while updating the stream: {str(e)}",
                "responseData": None
            }), 500
        
        finally:
            db.close()
        
# ============================================================================================================================================ #

    def playlists(self):
        if self.playlist_format == "1":
            return self._generate_format_1_playlist()
        elif self.playlist_format == "2":
            return self._generate_format_2_playlist()
        else:
            return {"error": "Invalid playlist format specified"}, 400

    def _generate_format_1_playlist(self):
        self.logging.info("Generating Format 1 playlist")
        headers_str = f"#EXTHTTP:{{\"User-Agent\":\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36\",\"Referer\":\"{self.referer}\"}}\n"
        additional_lines = [
            '#KODIPROP:inputstreamaddon=inputstream.adaptive',
            '#KODIPROP:inputstream.adaptive.manifest_type=dash',
            '#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey',
        ]
        if self.key and self.kid:
            additional_lines.append(f'''#KODIPROP:inputstream.adaptive.license_key={{"keys":[{{"kty":"oct","kid":"{self.kid}","k":"{self.key}"}}],"type":"temporary"}}''')

        playlist_content = headers_str
        for line in additional_lines:
            playlist_content += line + '\n'

        playlist_entry = f"#EXTINF:-1 type=\"{self.genre_type}\" group-title=\"{self.channel_group}\" tvg-logo=\"{self.channel_thumbnail}\",{self.channel_name}\n"
        playlist_entry += f"{self.mpd_url}\n\n"
        playlist_content += playlist_entry

        output_file = f"templates/generator/{self.content_id}.m3u"
        try:
            with open(output_file, "w") as f:
                f.write("#EXTM3U\n")
                f.write(playlist_content)
        except Exception as e:
            return {"error": "Error generating playlist"}, 500
        return {"responseData": playlist_content, "filePath": f"{self.content_id}.m3u"}

    def _generate_format_2_playlist(self):
        self.logging.info("Generating Format 2 playlist")
        headers_str = f"#EXTHTTP:{{\"User-Agent\":\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36\",\"Referer\":\"{self.referer}\"}}\n"
        
        # Define other playlist content
        license_key = f"{self.kid}:{self.key}"
        entry_str = f"#EXTINF:-1 type=\"{self.genre_type}\" group-title=\"{self.channel_group}\" tvg-logo=\"{self.channel_thumbnail}\",{self.channel_name}\n"
        entry_str += "#KODIPROP:inputstreamaddon=inputstream.adaptive\n"
        entry_str += "#KODIPROP:inputstream.adaptive.manifest_type=dash\n"
        entry_str += "#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey\n"
        entry_str += f"#KODIPROP:inputstream.adaptive.license_key={license_key}\n"
        entry_str += headers_str  # Add headers here
        entry_str += f"{self.mpd_url}\n\n"
        
        playlist_content = entry_str
        output_file = f"templates/generator/{self.content_id}.m3u"
        try:
            with open(output_file, "w") as f:
                f.write("#EXTM3U\n")
                f.write(playlist_content)
        except Exception as e:
            return {"error": "Error generating playlist"}, 500
        
        return {"responseData": playlist_content, "filePath": f"{self.content_id}.m3u"}
    
    def generate_epg(self, channels, programs):
        root = ET.Element("tv")
        for channel in channels:
            channel_elem = ET.SubElement(root, "channel", id=channel['id'])
            ET.SubElement(channel_elem, "display-name").text = channel['name']

        for program in programs:
            program_elem = ET.SubElement(root, "programme", channel=program['channel'], start=program['start'], stop=program['end'])
            ET.SubElement(program_elem, "title").text = program['title']
            if 'desc' in program:
                ET.SubElement(program_elem, "desc").text = program['desc']

        tree = ET.ElementTree(root)
        with open(self.output_file, 'wb') as file:
            tree.write(file, encoding='utf-8', xml_declaration=True)
        
        return {"responseData": self.get_epg_content(), "filePath": self.output_file}

    def get_epg_content(self):
        with open(self.output_file, 'r', encoding='utf-8') as file:
            return file.read()

    def _generate_format_3_playlist(self):
        data = {
            "name": f"Updated: {self.name}",
            "category": f"Updated: {self.category}",
            "info": {
                "poster": self.poster,
                "bg": self.bg,
                "plot": self.plot,
                "backdrop": self.backdrop,
                "director": self.director.split(','),
                "cast": self.cast.split(','),
                "year": self.year
            },
            "video": self.video
        }
        return json.dumps(data, indent=4)
