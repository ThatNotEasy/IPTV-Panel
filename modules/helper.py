import requests, os
from modules.logging import setup_logging
from modules.config import setup_config

logging = setup_logging()
config = setup_config()

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

class HELPER:
    def __init__(self,):
        self.uuid = None
        self.username = None
        self.password = None

def get_external_ip():
    try:
        response = requests.get('https://ipv4.icanhazip.com')
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Error fetching external IP: {e}")
        
def access_panel():
    access_ip_panel_path = 'access_panel.txt'

    if not os.path.isfile(access_ip_panel_path):
        logging.error(f"Access IP panel file '{access_ip_panel_path}' does not exist.")
        return None

    try:
        with open(access_ip_panel_path, 'r') as panel_file:
            license_content = panel_file.read()
            logging.info("License content fetched successfully from local file.")
    except Exception as e:
        logging.error(f"Error reading license content from local file: {e}")
        return None

    server_ip = get_external_ip()
    if server_ip is None or server_ip not in license_content:
        logging.error("Server IP not authorized. Check your license.")
        return None

    config = {}
    try:
        with open(log_dir + 'IPs.txt', 'r') as data_file:
            file_content = data_file.read()
            exec(file_content, config)
            logging.info("Configuration file loaded and executed successfully.")
    except Exception as e:
        logging.error(f"Error loading configuration file: {e}")
        return None
    
    return config