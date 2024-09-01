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





    