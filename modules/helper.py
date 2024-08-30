import requests, os, json, random, os, string
from modules.logging import setup_logging
from modules.config import setup_config

logging = setup_logging()
config = setup_config()

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

url_db = {}

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def shorten_url_logic(original_url):
    short_code = generate_short_code()
    url_db[short_code] = original_url
    short_url = f"http://localhost:1337/{short_code}"
    return short_url