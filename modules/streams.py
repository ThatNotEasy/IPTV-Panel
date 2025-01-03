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
