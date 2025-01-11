import requests, uuid, jwt, datetime
from flask import jsonify
from modules.sqlite import SQLITE

class ACCESS_CONTROL:
    def __init__(self,):
        self.ip_address = None
        self.asn_address = None
        self.user_agent = None
        
    def add_blacklists(self):
        try:
            db = SQLITE()
            db.execute(sql="INSERT INTO access_control (ip_address, asn_address, user_agent) VALUES (?, ?, ?)", args=(self.ip_address, self.asn_address, self.user_agent))
            db.commit()
            db.close()
            return jsonify({"responseData": "has been added to the blacklist"}), 200
        except Exception as e:
            return jsonify({"responseData": "internal error"}), 500
        
    def get_blacklists(self):
        try:
            db = SQLITE()
            result = db.query(sql="SELECT * FROM access_control")
            db.close()
            return jsonify({"responseData": result}), 200
        except Exception as e:
            return jsonify({"responseData": "internal error"}), 500