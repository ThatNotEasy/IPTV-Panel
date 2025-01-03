import requests, uuid, jwt, datetime, random, string
from flask import jsonify
from modules.logging import setup_logging
from datetime import datetime, timedelta
from modules.sqlite import SQLITE

logging = setup_logging()

class USERS:
    def __init__(self):
        self.user_id = None
        self.username = None
        self.password = None
        self.email = None
        self.role = None
        self.max_connection = None
        self.expired_at = None
        self.package_id = None
        self.package_name = None
        self.ip_address = None
        self.device = None
        self.active_sessions = {}
        
    def calculate_expiration(self):
        now = datetime.now()
        one_month_later = now + timedelta(days=30)
        return one_month_later
    
    def generate_short_code(self, length=6):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        
    def register(self):
        try:
            db = SQLITE()
            
            # Check if the username or password already exists
            result = db.query(
                sql="SELECT username FROM users WHERE username = ? OR password = ?",
                args=(self.username, self.password)
            )
            
            if result:
                # Username or password already exists
                response = {
                    "status": "error",
                    "message": "Username or password already exists.",
                    "responseData": None
                }
                return jsonify(response), 409
            
            db.execute(
                sql="INSERT INTO users (user_id, username, password, email, role) VALUES (?, ?, ?, ?, ?)",
                args=(str(uuid.uuid4()).replace("-", ""), self.username, self.password, self.email, 'user')
            )
            db.commit()
            
            response = {
                "status": "success",
                "message": "User registered successfully.",
                "username": self.username,
                "email": self.email
                }
            return jsonify({"responseData": response}), 201
        
        except Exception as e:
            response = {
                "status": "error",
                "message": f"Error registering user: {str(e)}"
            }
            return jsonify({"responseData": response}), 500
        
        finally:
            # Ensure the database connection is closed
            db.close()
            
# ============================================================================================================================================ #

    def add_users(self):
        db = SQLITE()
        self.user_id = str(uuid.uuid4()).replace("-", "")
            
        existing_user = db.query(sql="SELECT * FROM users WHERE username = ?", args=(self.username,))
        if existing_user:
            response = {"status": "error","message": "Username already exists."}
            return jsonify({"responseData": response}), 409
            
        db.execute(sql="INSERT INTO users (user_id, username, role, expired_at) VALUES (?, ?, ?, ?)", args=(self.user_id, self.username, 'NORMAL USER', self.calculate_expiration()))
        db.commit()
        db.close()
            
        playlist = f"http://127.0.0.1:1337/dev/users/{self.user_id}/playlist"
        create_shortner_response = requests.post("http://127.0.0.1:1337/dev/authorized/create_shortner", json={"url": playlist})
            
        if create_shortner_response.status_code == 200:
            create_shortner_data = create_shortner_response.json()["responseData"]
            shortner = create_shortner_data["shorten"]
                
            response = {"status": "success", "message": "User added successfully.", "user_id": self.user_id, "username": self.username, "iptv": shortner}
            return jsonify({"responseData": response}), 201
        else:
            response = {"status": "error", "message": f"Error from shortener service: {create_shortner_response.text}"}
            return jsonify({"responseData": response}), create_shortner_response.status_code

            
            
# ============================================================================================================================================ #

    def get_all_users(self):
        try:
            db = SQLITE()
            
            query = "SELECT user_id, role, created_at FROM users;"
            result = db.query(sql=query)
            
            # Successful response
            response = {
                "status": "success",
                "message": "Users retrieved successfully.",
                "responseData": result
            }
            return jsonify(response), 200
        
        except Exception as e:
            # Handle exceptions
            response = {
                "status": "error",
                "message": f"Error retrieving users: {str(e)}",
                "responseData": None
            }
            return jsonify(response), 500
        
        finally:
            # Ensure the database connection is closed
            db.close()
    
# ============================================================================================================================================ #

    def get_single_users(self):
        try:
            db = SQLITE()
            
            # Query to get a single user by user_id
            query = "SELECT username, user_id, role, created_at FROM users WHERE user_id = ?;"
            result = db.query(sql=query, args=(self.user_id,))
            
            if not result:
                # User not found
                response = {
                    "status": "error",
                    "message": "User not found.",
                    "responseData": None
                }
                return jsonify(response), 404
            
            # Successful retrieval
            response = {
                "status": "success",
                "message": "User retrieved successfully.",
                "responseData": result
            }
            return jsonify(response), 200
        
        except Exception as e:
            # Handle exceptions
            response = {
                "status": "error",
                "message": f"Error retrieving user: {str(e)}",
                "responseData": None
            }
            return jsonify(response), 500
        
        finally:
            # Ensure the database connection is closed
            db.close()
            
# ============================================================================================================================================ #

    def delete_single_users(self):
        try:
            db = SQLITE()
            
            # Query to delete a user by user_id
            query = "DELETE FROM users WHERE user_id = ?;"
            db.execute(sql=query, args=(self.user_id,))
            db.commit()
            
            # Successful deletion
            response = {
                "status": "success",
                "message": "User deleted successfully.",
                "responseData": None
            }
            return jsonify(response), 200
        
        except Exception as e:
            # Handle exceptions
            response = {
                "status": "error",
                "message": f"Error deleting user: {str(e)}",
                "responseData": None
            }
            return jsonify(response), 500
        
        finally:
            # Ensure the database connection is closed
            db.close()
            
# ============================================================================================================================================ #

    def update_single_users(self):
        try:
            db = SQLITE()
            
            # Query to update a user by user_id
            update_query = """
            UPDATE users
            SET username = ?, password = ?, email = ?, role = ?
            WHERE user_id = ?;
            """
            
            # Execute the update query
            db.execute(
                sql=update_query,
                args=(self.username, self.password, self.email, self.role, self.user_id)
            )
            db.commit()
            
            # Successful update
            response = {
                "status": "success",
                "message": "User updated successfully.",
                "responseData": None
            }
            return jsonify(response), 200
        
        except Exception as e:
            # Handle exceptions
            response = {
                "status": "error",
                "message": f"Error updating user: {str(e)}",
                "responseData": None
            }
            return jsonify(response), 500
        
        finally:
            # Ensure the database connection is closed
            db.close()

# ============================================================================================================================================ #

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
            
# ============================================================================================================================================ #

    def get_iptvs(self):
        
        self.playlist = f"http://127.0.0.1:1337/{self.user_id}/playlist.m3u"
        
        try:
            db = SQLITE()
            
            query = "SELECT user_id, username FROM users WHERE user_id = ?;"
            result = db.query(sql=query, args=(self.user_id,))
            
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
            
# ==================================================================================================================================================== #

    def check_user_id(self):
        query = "SELECT 1 FROM users WHERE user_id = ? LIMIT 1;"
        db = SQLITE()
        try:
            result = db.query(sql=query, args=(self.user_id,))
            return len(result) > 0
        except Exception as e:
            print(f"Error checking user_id: {str(e)}")
            return False
        finally:
            db.close()
        
# ==================================================================================================================================================== #

    def update_user_activity(self):
        if not self.ip_address or not self.device:
            logging.warning(f"Attempt to update user activity for user {self.user_id} with empty IP or device.")
            return {"status": "error", "message": "IP address and device cannot be empty."}
        
        query = """
            UPDATE users
            SET ip_address = ?, device = ?, last_login_date = ?, 
                login_date = CASE WHEN login_date IS NULL OR login_date = '' THEN ? ELSE login_date END
            WHERE user_id = ?;
        """
        current_time = datetime.utcnow()
        try:
            db = SQLITE()
            db.execute(
                sql=query,
                args=(self.ip_address, self.device, current_time, current_time, self.user_id)
            )
            db.commit()
            return {"status": "success", "message": "User activity updated successfully."}
        except Exception as e:
            logging.error(f"Error updating user activity for user {self.user_id}: {str(e)}")
            return {"status": "error", "message": f"Error updating user: {str(e)}"}
        finally:
            db.close()

# ==================================================================================================================================================== #

    def get_active_session(self):
        try:
            query = "SELECT ip_address, device FROM users WHERE user_id = ?"
            db = SQLITE()
            result = db.query(sql=query, args=(self.user_id,))
            if result and result[0]['ip_address'] and result[0]['device']:
                return result[0]
            else:
                update = self.update_user_activity()
                if update["status"] == "error":
                    logging.warning(f"Failed to update user activity for user {self.user_id} while getting active session.")
                return None
        except Exception as e:
            logging.error(f"Error fetching active session for user {self.user_id}: {str(e)}")
            return None
        finally:
            db.close()
