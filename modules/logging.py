import logging
import json
import datetime
import requests
import coloredlogs
import os

os.makedirs("logs", exist_ok=True)

def setup_logging():
    """Sets up logging to display only debug-level messages with colored output."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG) 

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Colored logs configuration
    coloredlogs.install(
        level='DEBUG',
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level_styles={
            'info': {'color': 'green'},
            'debug': {'color': 'blue'},
            'warning': {'color': 'yellow'},
            'error': {'color': 'red'},
            'critical': {'color': 'red', 'bold': True},
        },
        field_styles={
            'asctime': {'color': 'cyan'},
            'name': {'color': 'magenta'},
            'levelname': {'color': 'white', 'bold': True},
            'message': {'color': 'white'},
        }
    )

    return logger

def log_user_ip(request):
    """Logs user IP information and details to a file."""
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')
    referer = request.headers.get('Referer', '')
    accept_language = request.headers.get('Accept-Language', '')
    tarikh = datetime.datetime.now().isoformat()

    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/")
        response.raise_for_status()
        ip_data = response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve IP data: {e}")
        ip_data = {}

    relevant_fields = [
        'ip', 'version', 'city', 'region', 'region_code', 'country',
        'country_name', 'country_code', 'country_code_iso3', 'country_capital',
        'country_tld', 'postal', 'latitude', 'longitude', 'timezone', 'utc_offset',
        'country_calling_code', 'currency', 'currency_name', 'languages',
        'country_area', 'country_population', 'asn', 'org'
    ]

    ip_info = {field: ip_data.get(field) for field in relevant_fields}

    log_entry = {
        "date": tarikh,
        "visitor": {
            "user_agent": user_agent,
            "referer": referer,
            "accept_language": accept_language
        },
        "ip_data": ip_info
    }

    try:
        log_file = "logs/visitor.log"
        with open(log_file, "a") as file:
            file.write(json.dumps(log_entry, indent=4) + ',\n')
    except IOError as e:
        logging.error(f"Failed to write log entry: {e}")