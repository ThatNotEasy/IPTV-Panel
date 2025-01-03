import logging
import json
import datetime
import requests
import coloredlogs
import os

os.makedirs("logs", exist_ok=True)

def setup_logging():
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logs_folder = 'logs'
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    coloredlogs.install(level='DEBUG', fmt=log_format, humanize=True)
    logging.basicConfig(level=logging.DEBUG, format=log_format, filename=os.path.join(logs_folder, 'log.log'))
    return logging

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