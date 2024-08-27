import requests, uuid, jwt, datetime
from flask import jsonify
from modules.sqlite import SQLITE

class STREAMS:
    def __init__(self):
        self.stream_id = None
        self.server = None
        self.speed = None
        self.max_connection = None
        self.manifest_url = None
        self.kid_key = None
        
# ============================================================================================================================================ #

    def get_all_streams(self):
        query = "SELECT * FROM streams;"
        db = SQLITE()
        try:
            result = db.query(sql=query)
            db.close()
            
            if result:
                response = {
                    "status": "success",
                    "message": "Successfully retrieved streams.",
                    "responseData": result
                }
            else:
                response = {
                    "status": "success",
                    "message": "No streams found.",
                    "responseData": []
                }
        except Exception as e:
            db.close()
            response = {
                "status": "error",
                "message": f"An error occurred while retrieving streams: {str(e)}"
            }

        return jsonify(response)

# ============================================================================================================================================ #

    def get_single_streams(self):

        query = "SELECT * FROM streams WHERE stream_id = ?;"
        db = SQLITE()
        try:
            result = db.query(sql=query, params=(self.stream_id,))
            db.close()
            
            if result:
                response = {
                    "status": "success",
                    "message": "Successfully retrieved the stream.",
                    "responseData": result
                }
            else:
                response = {
                    "status": "success",
                    "message": "No stream found with the provided stream_id.",
                    "responseData": []
                }
        except Exception as e:
            db.close()
            response = {
                "status": "error",
                "message": f"An error occurred while retrieving the stream: {str(e)}"
            }

        return jsonify(response)

# ============================================================================================================================================ #

    def manage_streams(self):
        query = "SELECT * FROM streams WHERE stream_id = ?;"
        db = SQLITE()
        
        try:
            # Check if the stream exists
            result = db.query(sql=query, args=(self.stream_id,))
            
            if not result:
                # Stream not found
                return jsonify({
                    "status": "error",
                    "message": "Stream not found.",
                    "responseData": None
                }), 404
            
            # Update the stream
            update_query = "UPDATE streams SET manifest_url = ?, kid_key = ? WHERE stream_id = ?;"
            db.execute(sql=update_query, args=(self.manifest_url, self.kid_key, self.stream_id))
            
            # Success response
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
            # Handle any exceptions
            return jsonify({
                "status": "error",
                "message": f"An error occurred while updating the stream: {str(e)}",
                "responseData": None
            }), 500
        
        finally:
            # Ensure the database connection is closed
            db.close()
        
# ============================================================================================================================================ #
