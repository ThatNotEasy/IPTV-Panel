from flask import jsonify
from datetime import datetime, timedelta
from modules.sqlite import SQLITE
import os, json, random, string

class AUTHORIZED:
    def __init__(self,):
        self.user_id = None
        self.uuid = None
        self.username = None
        self.password = None
        self.original_url = None
        self.short_code = None
        self.playlist = None
        self.url_db = {}
        self.expired_at = None

    def calculate_expiration(self):
        now = datetime.now()
        one_month_later = now + timedelta(days=30)
        return one_month_later
        
    def generate_short_code(self, length=6):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def shorten_url_logic(self):
        if not self.original_url:
            return jsonify({"responseData": "Original URL not provided"}), 400
        
        short_code = self.generate_short_code()
        self.url_db[short_code] = self.original_url
        shortened_url = f"http://localhost:1337/dev/authorized/{short_code}"
        response = {"shorten": shortened_url}
        return jsonify({"responseData": response}), 200
    
    def get_original_url(self, short_code):
        return self.url_db.get(short_code, None)
    
# ==================================================================================================================================================== #

    def update_expiration(self):
        self.expired_at = self.calculate_expiration()
        try:
            db = SQLITE()  # Replace with your actual database connection
            query = """
                UPDATE users 
                SET expired_at = ?
                WHERE user_id = ?;
            """
            db.execute(sql=query, args=(self.expired_at, self.user_id))
            db.commit()
        
        except Exception as e:
            print(f"Error updating expiration: {str(e)}")
        
        finally:
            db.close()
            
# ==================================================================================================================================================== #

    def get_iptvs(self):
        
        self.playlist = f"http://127.0.0.1:1337/{self.user_id}/playlist.m3u"
        
        try:
            db = SQLITE()
            
            query = "SELECT user_id, username FROM users WHERE user_id = ?;"
            result = db.query(sql=query, args=(self.uuid,))
            
            if not result:
                response = {
                    "status": "error",
                    "message": "No IPTVs found for the provided UUID.",
                    "responseData": None
                }
                return jsonify(response), 404

            response = {
                "status": "success",
                "message": "IPTVs retrieved successfully.",
                "responseData": {
                    "playlist_url": self.playlist
                }
            }
            self.update_expiration()
            return jsonify(response), 200
        
        except Exception as e:
            response = {
                "status": "error",
                "message": f"Error retrieving IPTVs: {str(e)}",
                "responseData": None
            }
            return jsonify(response), 500
        
        finally:
            db.close()
            
    def check_user_id(self, user_id):
        query = "SELECT 1 FROM users WHERE user_id = ? LIMIT 1;"
        db = SQLITE()
        try:
            result = db.query(sql=query, args=(user_id,))
            return len(result) > 0
        except Exception as e:
            print(f"Error checking user_id: {str(e)}")
            return False
        finally:
            db.close()
        
# ==================================================================================================================================================== #


    