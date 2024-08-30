import requests, uuid, jwt, datetime
from flask import jsonify
from modules.sqlite import SQLITE

class RESELLER:
    def __init__(self):
        self.user_id = None
        self.username = None
        self.password = None
        self.email = None
        self.role = None
        self.max_connection = None
        self.expired_date = None
        self.package_id = None
        self.package_name = None

# ============================================================================================================================================ #

    def get_all_resellers(self):
        try:
            db = SQLITE()
            
            result = db.query(
                sql="SELECT * FROM users WHERE role = ?",
                args=('RESELLER',)
            )
            
            if result:
                response = {
                    "status": "success",
                    "message": "Resellers retrieved successfully.",
                    "responseData": result
                }
                return jsonify(response), 200
            else:
                response = {
                    "status": "error",
                    "message": "No resellers found.",
                    "responseData": None
                }
                return jsonify(response), 404
        
        except Exception as e:
            response = {
                "status": "error",
                "message": f"Error retrieving resellers: {str(e)}",
                "responseData": None
            }
            return jsonify(response), 500
        
        finally:
            db.close()
            
# ============================================================================================================================================ #

    def get_single_resellers(self):
        try:
            db = SQLITE()
            
            result = db.query(
                sql="SELECT * FROM users WHERE user_id = ? AND role = ?",
                args=(self.user_id, 'RESELLER')
            )
            
            if result:
                response = {
                    "status": "success",
                    "message": "Reseller retrieved successfully.",
                    "responseData": result[0]
                }
                return jsonify(response), 200
            else:
                response = {
                    "status": "error",
                    "message": "Reseller not found.",
                    "responseData": None
                }
                return jsonify(response), 404
        
        except Exception as e:
            # Handle exceptions
            response = {
                "status": "error",
                "message": f"Error retrieving reseller: {str(e)}",
                "responseData": None
            }
            return jsonify(response), 500
        
        finally:
            db.close()
            
# ============================================================================================================================================ #

    def delete_resellers(self):
        try:
            db = SQLITE()
            
            result = db.query(
                sql="SELECT * FROM users WHERE user_id = ? AND role = ?",
                args=(self.user_id, 'RESELLER')
            )
            
            if not result:
                response = {
                    "status": "error",
                    "message": "Reseller not found.",
                    "responseData": None
                }
                return jsonify(response), 404
            
            db.execute(
                sql="DELETE FROM users WHERE user_id = ? AND role = ?",
                args=(self.user_id, 'RESELLER')
            )
            db.commit()
            
            response = {
                "status": "success",
                "message": "Reseller deleted successfully.",
                "responseData": {
                    "reseller_uuid": self.user_id
                }
            }
            return jsonify(response), 200
        
        except Exception as e:
            response = {
                "status": "error",
                "message": f"Error deleting reseller: {str(e)}",
                "responseData": None
            }
            return jsonify(response), 500
        
        finally:
            db.close()
            
# ============================================================================================================================================ #

    def add_new_resellers(self):
        try:
            db = SQLITE()
            reseller_uuid = str(uuid.uuid4()).replace("-", "")
            
            existing_user = db.query(
                sql="SELECT * FROM users WHERE username = ? OR email = ?",
                args=(self.username, self.email)
            )
            
            if existing_user:
                response = {
                    "status": "error",
                    "message": "Username or email already exists.",
                    "responseData": None
                }
                return jsonify(response), 409
            
            db.execute(
                sql="INSERT INTO users (user_id, username, password, email, role) VALUES (?, ?, ?, ?, ?)",
                args=(reseller_uuid, self.username, self.password, self.email, 'RESELLER')
            )
            db.commit()
            
            response = {
                "status": "success",
                "message": "Reseller added successfully.",
                "responseData": {
                    "user_id": reseller_uuid,
                    "username": self.username,
                    "email": self.email
                }
            }
            return jsonify(response), 201
        
        except Exception as e:
            response = {
                "status": "error",
                "message": f"Error adding reseller: {str(e)}",
                "responseData": None
            }
            return jsonify(response), 500
        
        finally:
            db.close()

# ============================================================================================================================================ #
