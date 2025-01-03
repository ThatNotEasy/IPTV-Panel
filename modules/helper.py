import requests, os, json, random, os, string, re, time
from flask import request, jsonify, Response, redirect, url_for, abort
from modules.logging import setup_logging
from modules.config import setup_config
from functools import wraps
import geoip2.database, random, string

# ================================================================================================================================================== #

logging = setup_logging()
config = setup_config()

log_dir = 'logs'
REQUESTS = {}
RATE_LIMIT = 5  # Maximum requests allowed per minute
TIME_FRAME = 60  # Time frame in seconds
GEOIP_DB = 'GeoLite2-City.mmdb'
geoip_reader = geoip2.database.Reader(GEOIP_DB)
COUNTRY_CODE = ['MY', 'ES']
WHITELISTED_IPS = set()
BLACKLISTED_IPS = set()

os.makedirs(log_dir, exist_ok=True)

# ================================================================================================================================================== #

def detect_sniffing(user_agent, client_ip):
    suspicious_patterns = [
        r'emulator',  # Detect emulators
        r'bot',       # Detect bots
        r'scanner',   # Detect scanners
        r'curl',      # Detect curl requests
        r'wget',      # Detect wget requests
        r'python',    # Detect Python scripts
        r'Dalvik',    # Detect Dalvik-based user agents (often emulator related)
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, user_agent, re.IGNORECASE):
            logging.warning(f"Sniffing attempt detected from {client_ip} with User-Agent: {user_agent}")
            return True
    return False

suspicious_headers = ["via", "forwarded", "x-forwarded-for", "x-client-ip", "x-real-ip"]
# ================================================================================================================================================== #

def get_external_ip():
    try:
        response = requests.get("https://ipv4.icanhazip.com")
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Error fetching external IP: {e}")

# ================================================================================================================================================== #

def manage_ip_lists(client_ip, suspicious=False):
    if suspicious:
        if client_ip in WHITELISTED_IPS:
            WHITELISTED_IPS.discard(client_ip)
        BLACKLISTED_IPS.add(client_ip)
        logging.info(f"IP {client_ip} has been moved to the blacklist due to suspicious activity.")
    else:
        if client_ip not in WHITELISTED_IPS and client_ip not in BLACKLISTED_IPS:
            WHITELISTED_IPS.add(client_ip)
            logging.info(f"IP {client_ip} added to the whitelist.")
            
# ================================================================================================================================================== #

def rate_limit(f):
    REQUESTS = {}
    RATE_LIMIT = 5
    TIME_FRAME = 60
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        now = time.time()

        if client_ip not in REQUESTS:
            REQUESTS[client_ip] = []

        REQUESTS[client_ip] = [timestamp for timestamp in REQUESTS[client_ip] if now - timestamp < TIME_FRAME]

        if len(REQUESTS[client_ip]) >= RATE_LIMIT:
            logging.warning(f"Rate limit exceeded for {client_ip}")
            return jsonify({"responseData": "Rate limit exceeded. Please try again later."}), 429

        REQUESTS[client_ip].append(now)
        return f(*args, **kwargs)
    return decorated_function

# ================================================================================================================================================== #

def check_client_certificate(client_ip):
    client_cert = request.headers.get('X-Client-Cert')
    if client_cert and "self-signed" in client_cert:
        logging.warning(f"Self-signed certificate detected from {client_ip}")
        return abort(403, description="Invalid certificate")

# ================================================================================================================================================== #

def generate_stream_id(length=4):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))

# ================================================================================================================================================== #

def geoip_lookup(ip):
    try:
        response = geoip_reader.city(ip)
        return response.country.iso_code
    except Exception as e:
        logging.error(f"GeoIP lookup failed for IP {ip}: {e}")
        return None