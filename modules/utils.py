from flask import request, jsonify, redirect
import json
from urllib.parse import urlparse
from datetime import datetime, timedelta
import random
import string
import os
import requests
import sys
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import binascii
from modules.config import setup_config
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import sam_enc

config = setup_config()

m3u_base = config.get('m3u_base', '')
m3u_host = urlparse(m3u_base).netloc
admin_pass = config.get('admin_pass', '')
redirect_url = config.get('redirect_url', '')
TELEGRAM_BOT_TOKEN = config.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_ADMIN_ID = config.get('TELEGRAM_ADMIN_ID', '')
TELEGRAM_CHANNEL_ID = config.get('TELEGRAM_CHANNEL_ID', '')
USER_IPTV_FILE = config.get('USER_IPTV_FILE', '')
USER_LOG_FILE = config.get('USER_LOG_FILE', '')
RESELLER_FILE = config.get('RESELLER_FILE', '')
AGENT_FILE = config.get('AGENT_FILE', '')
SNIFFER_DATA_FILE = config.get('SNIFFER_DATA_FILE', '')
MULTILOGIN_DATA_FILE = config.get('MULTILOGIN_DATA_FILE', '')
SECURE_SHORT_FILE = config.get('SECURE_SHORT_FILE', '')
SECURE_REDIRECT = config.get('SECURE_REDIRECT', '')
OTT_FILE = config.get('OTT_FILE', '')
EXPIRED_FILE = config.get('EXPIRED_FILE', '')
BANNED_FILE = config.get('BANNED_FILE', '')
STORAGE_FILE = config.get('STORAGE_FILE', '')
EXPIRED_DATA = config.get('EXPIRED_DATA', '')
SAFE_LOGIN = config.get('SAFE_LOGIN', '')
CRITICAL_LOGIN = config.get('CRITICAL_LOGIN', '')
DURATION_LOG = config.get('DURATION_LOG', '')
package_info = config.get('package_info', { })
SHORT_STATE = config.get('SHORT_STATE', '')
SHORT_LINK = config.get('SHORT_LINK', '')
tele_api_url = f'''https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'''

def encrypt_string(original_string, secret_key):
    secret_key = pad(secret_key.encode('utf-8'), AES.block_size)
    cipher = AES.new(secret_key, AES.MODE_ECB)
    ct_bytes = cipher.encrypt(pad(original_string.encode('utf-8'), AES.block_size))
    ct_hex = binascii.hexlify(ct_bytes).decode('utf-8')
    return ct_hex

def decrypt_string(encrypted_string, secret_key):
    try:
        secret_key = pad(secret_key.encode('utf-8'), AES.block_size)
        ct_bytes = binascii.unhexlify(encrypted_string)
        cipher = AES.new(secret_key, AES.MODE_ECB)
        pt = unpad(cipher.decrypt(ct_bytes), AES.block_size)
        return pt.decode('utf-8')
    except (binascii.Error, ValueError, KeyError, TypeError):
        return None

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def is_string_in_file(file_path, target_string):
    with open(file_path, 'r') as file:
        file_contents = file.read()
        return target_string in file_contents

def get_unique_random_string(file_path, length, max_attempts=100):
    attempts = 0
    while attempts < max_attempts:
        random_string = generate_random_string(length)
        if not is_string_in_file(file_path, random_string):
            return random_string
        attempts += 1
    return None

def derive_key(secret_key):
    salt = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))

def encrypt_text(secret_key, text):
    key = derive_key(secret_key)
    fernet = Fernet(key)
    encrypted_text = fernet.encrypt(text.encode('utf-8'))
    return base64.urlsafe_b64encode(encrypted_text).decode('utf-8')

def decrypt_text(secret_key, encoded_encrypted_text):
    key = derive_key(secret_key)
    fernet = Fernet(key)
    encrypted_text = base64.urlsafe_b64decode(encoded_encrypted_text.encode('utf-8'))
    decrypted_text = fernet.decrypt(encrypted_text).decode('utf-8')
    return decrypted_text



condition = threading.Condition()
file_lock = threading.Lock()

def get_external_ip():
    try:
        response = requests.get('https://ipv4.icanhazip.com')
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Error fetching external IP: {e}")
        sys.exit(1)


def load_config(file_path):
    config = {}
    license_url = 'https://raw.githubusercontent.com/syfqsamvpn/iptv/main/panel_access.txt'
    
    try:
        response = requests.get(license_url)
        license_content = response.text
    except requests.RequestException as e:
        print(f"Error fetching license content: {e}")
        sys.exit(1)
    
    server_ip = get_external_ip()
    if server_ip is None or server_ip not in license_content:
        print("Server IP not authorized. Check your license.")
        sys.exit(1)
    
    with open(file_path, 'r') as data_file:
        file_content = data_file.read()
        exec(file_content, config)
    
    return config


def load_vod_license(request_ip):
    license_url = 'https://raw.githubusercontent.com/syfqsamvpn/iptv/main/access_v.txt'
    
    try:
        response = requests.get(license_url)
        license_content = response.text
    except requests.RequestException:
        license_content = None
    
    if request_ip is None or request_ip not in license_content:
        return False
    return True


def agent_access():
    license_url = 'https://raw.githubusercontent.com/syfqsamvpn/iptv/main/agent.txt'
    
    try:
        response = requests.get(license_url)
        license_content = response.text
    except requests.RequestException as e:
        print(f"Error fetching license content: {e}")
        sys.exit(1)
    
    server_ip = get_external_ip()
    if server_ip is None or server_ip not in license_content:
        print("Server IP not authorized. Check your license.")
        return False
    return True


def checker_access():
    license_url = 'https://raw.githubusercontent.com/syfqsamvpn/iptv/main/xtro.txt'
    
    try:
        response = requests.get(license_url)
        license_content = response.text
    except requests.RequestException as e:
        print(f"Error fetching license content: {e}")
        sys.exit(1)
    
    server_ip = get_external_ip()
    if server_ip is None or server_ip not in license_content:
        print("Server IP not authorized. Check your license.")
        return False
    return True

def send_message_tele(message_text):
    escaped_message = message_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    params = {
        'chat_id': TELEGRAM_ADMIN_ID,
        'text': escaped_message,
        'parse_mode': 'HTML' }
    response = requests.post(tele_api_url, params, **('params',))
    return True


def load_short_links():
    try:
        with open(STORAGE_FILE, 'r') as file:
            data = file.read()
            if data:
                return json.loads(data)
            else:
                return {}
    except FileNotFoundError:
        return {}


def check_key_presence(play_list, key):
    return key in play_list


def load_sniff_links():
    try:
        with open(SNIFFER_DATA_FILE, 'r') as file:
            data = file.read()
            if data:
                return json.loads(data)
            else:
                return {}
    except FileNotFoundError:
        return {}


def load_multi_links():
    try:
        with open(MULTILOGIN_DATA_FILE, 'r') as file:
            data = file.read()
            if data:
                return json.loads(data)
            else:
                return {}
    except FileNotFoundError:
        return {}


def load_playlist_links():
    try:
        with open(SECURE_SHORT_FILE, 'r') as file:
            data = file.read()
            if data:
                return json.loads(data)
            else:
                return {}
    except FileNotFoundError:
        return {}


def shorten_with_tny(url):
    tny_api_url = f'''http://tny.im/yourls-api.php?action=shorturl&format=simple&url={url}'''
    response = requests.get(tny_api_url)
    result = response.text.strip()
    if not result:
        return url


def save_short_links(short_links):
    try:
        with open(STORAGE_FILE, 'w') as file:
            if short_links:
                json.dump(short_links, file)
    except FileNotFoundError:
        return {}


def save_secure_links(short_links):
    try:
        with open(SECURE_SHORT_FILE, 'w') as file:
            if short_links:
                json.dump(short_links, file)
    except FileNotFoundError:
        return {}


def read_m3u_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


def move_to_expired(username, user_uuid):
    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        users = []
    
    try:
        with open(EXPIRED_DATA, 'r') as expired_file:
            expireds = json.load(expired_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        expireds = []
    
    for user_info in users:
        if user_info.get('username') == username and user_info.get('uuid') == user_uuid:
            expiration_date_str = user_info.get('expiration_date', '')
            if expiration_date_str:
                expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d %H:%M:%S')
                current_date = datetime.now()
                if current_date > expiration_date:
                    expireds.append(user_info)
    
    with open(EXPIRED_DATA, 'w') as expired_file:
        json.dump(expireds, expired_file)


def remove_all_expired():
    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        users = []
    
    try:
        with open(EXPIRED_DATA, 'r') as expired_file:
            expireds = json.load(expired_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        expireds = []

    current_date = datetime.now()
    updated_logs = []

    for user_info in users:
        user_uuid = user_info.get('uuid')
        expiration_date_str = user_info.get('expiration_date', '')
        if expiration_date_str:
            expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d %H:%M:%S')
            if current_date > expiration_date:
                expireds.append(user_info)
            else:
                updated_logs.append(user_info)

    with open(USER_IPTV_FILE, 'w') as log_file:
        json.dump(updated_logs, log_file, indent=True)

    with open(EXPIRED_DATA, 'w') as expired_file:
        json.dump(expireds, expired_file)

    return True


def is_valid_user(username, user_uuid):
    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        users = []
    
    for user_info in users:
        if user_info.get('username') == username and user_info.get('uuid') == user_uuid:
            expiration_date_str = user_info.get('expiration_date', '')
            if expiration_date_str:
                expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d %H:%M:%S')
                current_date = datetime.now()
                if current_date <= expiration_date:
                    return True
                else:
                    move_to_expired(username, user_uuid)
                    return False
    return False


def generate_random_password(length):
    import string
    import random
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def is_username_taken(username):
    try:
        with open(RESELLER_FILE, 'r') as reseller_file:
            resellers = json.load(reseller_file)
            usernames = [reseller['username'] for reseller in resellers]
            return username in usernames
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return False


def register_reseller(username, balance):
    if is_username_taken(username):
        return False
    password = generate_random_password(8)
    reseller_info = {
        'username': username,
        'password': password,
        'balance': balance
    }
    try:
        with open(RESELLER_FILE, 'r') as reseller_file:
            resellers = json.load(reseller_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        resellers = []

    resellers.append(reseller_info)
    with open(RESELLER_FILE, 'w') as reseller_file:
        json.dump(resellers, reseller_file, indent=True)
    return password


def is_username_taken_agent(username):
    try:
        with open(AGENT_FILE, 'r') as agent_file:
            agents = json.load(agent_file)
            usernames = [agent['username'] for agent in agents]
            return username in usernames
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return False


def register_agent(username, balance, reseller_id):
    if is_username_taken_agent(username):
        return False
    password = generate_random_password(8)
    agent_info = {
        'username': username,
        'password': password,
        'balance': balance,
        'stokis_id': reseller_id
    }
    try:
        with open(AGENT_FILE, 'r') as agent_file:
            agents = json.load(agent_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        agents = []

    agents.append(agent_info)
    with open(AGENT_FILE, 'w') as agent_file:
        json.dump(agents, agent_file, indent=True)
    return password


def is_valid_reseller(username, password):
    if not os.path.exists(RESELLER_FILE):
        with open(RESELLER_FILE, 'w') as empty_file:
            json.dump([], empty_file)

    try:
        with open(RESELLER_FILE, 'r') as reseller_file:
            resellers = json.load(reseller_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return False

    for reseller_info in resellers:
        if reseller_info['username'] == username and reseller_info['password'] == password:
            return True
    return False


def is_valid_agent(username, password):
    if not os.path.exists(AGENT_FILE):
        with open(AGENT_FILE, 'w') as empty_file:
            json.dump([], empty_file)

    try:
        with open(AGENT_FILE, 'r') as agent_file:
            agents = json.load(agent_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return False

    for agent_info in agents:
        if agent_info['username'] == username and agent_info['password'] == password:
            return True
    return False


def get_user_info_by_uuid(user_uuid):
    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        users = []

    for user_info in users:
        if user_info.get('uuid') == user_uuid:
            return user_info
    return None


def get_expired_info_by_uuid(user_uuid):
    try:
        with open(EXPIRED_DATA, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        users = []

    for user_info in users:
        if user_info.get('uuid') == user_uuid:
            return user_info
    return None


def get_multilogin_info_by_uuid(user_uuid):
    try:
        with open(MULTILOGIN_DATA_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        users = []

    for user_info in users:
        if user_info.get('uuid') == user_uuid:
            return user_info
    return None


def get_sniffer_info_by_uuid(user_uuid):
    try:
        with open(SNIFFER_DATA_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        users = []

    for user_info in users:
        if user_info.get('uuid') == user_uuid:
            return user_info
    return None


def renew_user_expiration(current_date, days):
    current_date = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
    new_expiration_date = current_date + timedelta(days, **('days',))
    return new_expiration_date.strftime('%Y-%m-%d %H:%M:%S')


def get_reseller_info(username):
    try:
        with open(RESELLER_FILE, 'r') as reseller_file:
            resellers = json.load(reseller_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return None

    for reseller_info in resellers:
        if reseller_info['username'] == username:
            return reseller_info
    return None


def get_agent_info(username):
    try:
        with open(AGENT_FILE, 'r') as agent_file:
            agents = json.load(agent_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return None

    for agent_info in agents:
        if agent_info['username'] == username:
            return agent_info
    return None


def update_user_info(updated_info):
    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        users = []

    for i, user_info in enumerate(users):
        if user_info['username'] == updated_info['username'] and user_info.get('uuid') == updated_info.get('uuid'):
            users[i] = updated_info

    with open(USER_IPTV_FILE, 'w') as user_file:
        json.dump(users, user_file, indent=None)


def update_reseller_info(updated_info):
    try:
        with open(RESELLER_FILE, 'r') as reseller_file:
            resellers = json.load(reseller_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        resellers = []

    for i, reseller_info in enumerate(resellers):
        if reseller_info['username'] == updated_info['username']:
            resellers[i] = updated_info

    with open(RESELLER_FILE, 'w') as reseller_file:
        json.dump(resellers, reseller_file, indent=None)


def update_agent_info(self, agent_info):
    try:
        with open(self.agent_file, 'r') as file:
            agents = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        agents = []

    # Find and update the agent info
    for i, agent in enumerate(agents):
        if agent['uuid'] == agent_info['uuid']:
            agents[i] = agent_info
            break
    else:
        # If the agent is not found, add it to the list
        agents.append(agent_info)

    # Save the updated list back to the file
    with open(self.agent_file, 'w') as file:
        json.dump(agents, file, indent=4)


def log_user_info(user_id, user_uuid, reseller_username=None):
    user_info = {
        'user_id': user_id,
        'user_uuid': user_uuid,
        'ip_address': request.remote_addr,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'reseller_username': reseller_username
    }

    try:
        with open(USER_LOG_FILE, 'r') as log_file:
            user_logs = json.load(log_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        user_logs = []

    user_logs.append(user_info)

    with open(USER_LOG_FILE, 'w') as log_file:
        json.dump(user_logs, log_file, indent=None)


def api_check_multilogin(self):
    # Retrieve 'uuid' from the request arguments
    user_uuid = request.args.get('uuid')

    # Check if the UUID is not provided, return an error response
    if not user_uuid:
        return jsonify({"status": "error", "message": "UUID is missing"}), 400

    # Check multi-login using the provided UUID
    response_object = self.check_multilogin(user_uuid)[0]
    if response_object['status'] == 'blocked':
        return redirect(self.redirect_url)

    # Return the response object as a JSON response
    return jsonify(response_object)


def check_all_multilogin_data(self):
    # Open the multi-login data file
    try:
        with open(self.MULTILOGIN_DATA_FILE, 'r') as log_file:
            user_logs = json.load(log_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return []

    # Prepare a list to collect users with blocked status
    blocked_users = []

    # Iterate through all user logs
    for log in user_logs:
        if log['status'] == 'blocked':
            blocked_users.append(log['uuid'])

    # Return the list of blocked user UUIDs
    return blocked_users

def delete_old_logs():
    try:
        with open(USER_LOG_FILE, 'r') as log_file:
            user_logs = json.load(log_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return

    current_date = datetime.now()

    user_logs = [log for log in user_logs if current_date - datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S') <= timedelta(days=DURATION_LOG)]

    with open(USER_LOG_FILE, 'w') as log_file:
        json.dump(user_logs, log_file, indent=None)


def delete_short_link(username, user_uuid, storage_file_path):
    try:
        with open(storage_file_path, 'r') as STORAGE_FILE:
            short_links = json.load(STORAGE_FILE)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return

    short_links_copy = short_links.copy()

    for short_id, long_url in short_links_copy.items():
        if f"iptv?id={username}&uuid={user_uuid}" in long_url:
            del short_links[short_id]

    with open(storage_file_path, 'w') as STORAGE_FILE:
        json.dump(short_links, STORAGE_FILE)


def remove_entries_from_user_log(user_uuid):
    try:
        with open(USER_LOG_FILE, 'r') as log_file:
            user_logs = json.load(log_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return

    updated_logs = [log for log in user_logs if log['user_uuid'] != user_uuid]

    with open(USER_LOG_FILE, 'w') as log_file:
        json.dump(updated_logs, log_file, indent=None)


def remove_entries_from_expired_data(user_uuid):
    try:
        with open(USER_IPTV_FILE, 'r') as log_file:
            user_logs = json.load(log_file)
    except (json.JSONDecodeError, FileNotFoundError):
        return
    
    updated_logs = [log for log in user_logs if log.get('uuid') != user_uuid]
    
    with open(USER_IPTV_FILE, 'w') as log_file:
        json.dump(updated_logs, log_file, indent=True)


def remove_entries_from_multilogin_data(user_uuid):
    try:
        with open(MULTILOGIN_DATA_FILE, 'r') as log_file:
            user_logs = json.load(log_file)
    except (json.JSONDecodeError, FileNotFoundError):
        return
    
    updated_logs = [log for log in user_logs if log.get('uuid') != user_uuid]
    
    with open(MULTILOGIN_DATA_FILE, 'w') as log_file:
        json.dump(updated_logs, log_file, indent=True)


def remove_entries_from_sniffer_data(user_uuid):
    try:
        with open(SNIFFER_DATA_FILE, 'r') as log_file:
            user_logs = json.load(log_file)
    except (json.JSONDecodeError, FileNotFoundError):
        return
    
    updated_logs = [log for log in user_logs if log.get('uuid') != user_uuid]
    
    with open(SNIFFER_DATA_FILE, 'w') as log_file:
        json.dump(updated_logs, log_file, indent=True)


def delete_multi_from_file(username, user_uuid, ip_address, device_ids):
    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.JSONDecodeError, FileNotFoundError):
        return

    deleted_user = None
    updated_users = []

    for user in users:
        if user.get('username') == username and user.get('uuid') == user_uuid:
            deleted_user = user
        else:
            updated_users.append(user)

    with open(USER_IPTV_FILE, 'w') as user_file:
        json.dump(updated_users, user_file, indent=True)

    if not deleted_user:
        return

    try:
        with open(MULTILOGIN_DATA_FILE, 'r') as multilogin_file:
            multilogin_data = json.load(multilogin_file)
    except (json.JSONDecodeError, FileNotFoundError):
        multilogin_data = []

    deleted_user['ip_address'] = ip_address
    deleted_user['device_ids'] = device_ids
    multilogin_data.append(deleted_user)

    with open(MULTILOGIN_DATA_FILE, 'w') as multilogin_file:
        json.dump(multilogin_data, multilogin_file, indent=True)

    remove_entries_from_expired_data(user_uuid)

    try:
        with open('multilogin_template.txt', 'r') as template_file:
            message_template = template_file.read()
    except FileNotFoundError:
        return

    message_text = message_template.format(username=username, user_uuid=user_uuid, ip_address=ip_address)
    params = {'chat_id': TELEGRAM_CHANNEL_ID, 'text': message_text}

    response = requests.post(tele_api_url, params=params)
    return response


def delete_sniffer_from_file(username, user_uuid, ip_address):
    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.JSONDecodeError, FileNotFoundError):
        return

    deleted_user = None
    updated_users = []

    for user in users:
        if user.get('username') == username and user.get('uuid') == user_uuid:
            deleted_user = user
        else:
            updated_users.append(user)

    with open(USER_IPTV_FILE, 'w') as user_file:
        json.dump(updated_users, user_file, indent=True)

    if not deleted_user:
        return

    try:
        with open(SNIFFER_DATA_FILE, 'r') as sniffer_file:
            sniffer_data = json.load(sniffer_file)
    except (json.JSONDecodeError, FileNotFoundError):
        sniffer_data = []

    deleted_user['ip_address'] = ip_address
    sniffer_data.append(deleted_user)

    with open(SNIFFER_DATA_FILE, 'w') as sniffer_file:
        json.dump(sniffer_data, sniffer_file, indent=True)

    remove_entries_from_expired_data(user_uuid)

    try:
        with open('sniff_template.txt', 'r') as template_file:
            message_template = template_file.read()
    except FileNotFoundError:
        return

    message_text = message_template.format(username=username, user_uuid=user_uuid, ip_address=ip_address)
    params = {'chat_id': TELEGRAM_CHANNEL_ID, 'text': message_text}

    response = requests.post(tele_api_url, params=params)
    return response


def delete_user_from_file(username, user_uuid):
    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.JSONDecodeError, FileNotFoundError):
        return False

    updated_users = []
    user_deleted = False

    for user in users:
        if user.get('username') == username and user.get('uuid') == user_uuid:
            user_deleted = True
        else:
            updated_users.append(user)

    if user_deleted:
        with open(USER_IPTV_FILE, 'w') as user_file:
            json.dump(updated_users, user_file, indent=True)

        delete_short_link(username, user_uuid, STORAGE_FILE)
        remove_entries_from_expired_data(user_uuid)
        return True

    return False


def delete_for_renew(username, user_uuid):
    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.JSONDecodeError, FileNotFoundError):
        return False

    updated_users = []
    user_deleted = False

    for user in users:
        if user.get('username') == username and user.get('uuid') == user_uuid:
            user_deleted = True
        else:
            updated_users.append(user)

    if user_deleted:
        with open(USER_IPTV_FILE, 'w') as user_file:
            json.dump(updated_users, user_file, indent=True)

        remove_entries_from_expired_data(user_uuid)
        return True

    return False


def get_user_logs(self, user_uuid):
    # Call check_multilogin function and get the response object
    response_object = self.check_multilogin(user_uuid)[0]

    # Extract the user logs from the response object
    user_logs = json.loads(response_object.get_data(as_text=True))

    # Return the user logs
    return user_logs


def check_headers(headers):
    allowed_headers = [
        'User-Agent', 'Host', 'Connection', 'Accept-Encoding', 'Icy-Metadata',
        'Content-Type', 'Content-Length', 'Referer', 'Authorization', 'Range'
    ]
    for header, value in headers.items():
        if header not in allowed_headers:
            return True
    return False


def get_commission(stokis_id, commission):
    reseller_info = get_reseller_info(stokis_id)
    reseller_info['balance'] += commission
    update_reseller_info(reseller_info)


def check_shortlink_funct(username, user_uuid, short_links):
    m3u_link = f"{m3u_base}/iptv?id={username}&uuid={user_uuid}"
    short_id = sam_enc.get_unique_random_string(STORAGE_FILE, 8, 10)
    short_links[short_id] = m3u_link
    save_short_links(short_links)

    short_url = f"{m3u_base}/{short_id}"
    if SHORT_STATE == 'on':
        short_url = shorten_with_tny(short_url)
    elif str(SHORT_LINK) != 'off':
        short_url = f"https://{SHORT_LINK}/{short_id}"

    user_info = get_user_info_by_uuid(user_uuid)
    delete_for_renew(user_info['username'], user_uuid)
    user_info['link'] = short_url

    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except json.JSONDecodeError:
        users = []

    users.append(user_info)
    with open(USER_IPTV_FILE, 'w') as user_file:
        json.dump(users, user_file)

    update_user_info(user_info)
    return short_url


def notif_suspicious(headers, user_agent, full_url, time, user_ip):
    message_text = 'ÔòöÔòÉ\n'
    message_text += 'Ôòæ ­ƒÜ¿ Alert! ­ƒÜ¿\n'
    message_text += 'ÔòÜÔòÉ\n'
    message_text += f'''Ôòá User-Agent : {user_agent}\n'''
    message_text += f'''Ôòá Url : {full_url}\n'''
    message_text += f'''Ôòá Time : {time}\n'''
    message_text += f'''ÔòÜ IP : {user_ip}\n'''
    message_text += f'''\nHeader Ô¼ç´©Å\n{headers}\n'''
    send_message_tele(message_text)
    return True


def generate_xml_epg(xml_data, devices, SAFE_LOGIN):
    current_time = datetime.utcnow()
    start_time = current_time.strftime('%Y%m%d%H%M%S') + ' +0000'
    stop_time = (current_time + timedelta(12, **('hours',))).strftime('%Y%m%d%H%M%S') + ' +0000'
    xml_data = xml_data.replace('{start}', start_time)
    xml_data = xml_data.replace('{stop}', stop_time)
    xml_data = xml_data.replace('{total_device}', str(devices))
    xml_data = xml_data.replace('{SAFE_LOGIN}', str(SAFE_LOGIN))
    return xml_data


def ban_suspicious(user_uuid, headers, user_agent, time, request_url, request_ip):
    if not get_sniffer_info_by_uuid(user_uuid):
        user_data = get_user_info_by_uuid(user_uuid)
        if user_data:
            username = user_data['username']
            delete_sniffer_from_file(username, user_uuid, request_ip)
            notif_suspicious(headers, user_agent, request_url, time, request_ip)
            return 'Account banned'
        return None