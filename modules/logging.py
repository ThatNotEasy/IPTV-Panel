import logging, json, datetime, requests
import coloredlogs

def setup_logging():
    # Define the logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set the default logging level

    # Define the format for the logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a console handler and set the level to debug
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(console_handler)

    # Apply coloredlogs configuration
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
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    visitor = ip
    tarikh = datetime.datetime.now().isoformat()
    user_agent = request.headers.get('User-Agent', '')
    referer = request.headers.get('Referer', '')
    accept_language = request.headers.get('Accept-Language', '')

    try:
        response = requests.get(f"https://ipapi.co/{visitor}/json/")
        response.raise_for_status()
        ip_data = response.json()
    except requests.exceptions.RequestException:
        return None

    relevant_fields = [
        'ip', 'version', 'city', 'region', 'region_code', 'country',
        'country_name', 'country_code', 'country_code_iso3', 'country_capital',
        'country_tld', 'postal', 'latitude','longitude', 'timezone', 'utc_offset', 
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
        "ip_data": ip_info,
        "ip_datas": ip_info
    }

    try:
        with open("visitor.log", "a") as file:
            json.dump(log_entry, file, indent=4)
            file.write(',\n')
    except IOError:
        return ip_info