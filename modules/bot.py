import requests, os
from colorama import Fore
from modules.logging import setup_logging
from modules.config import setup_config

logging = setup_logging()
config = setup_config()

CHAT_ID = config["TELEGRAM"]["CHAT_ID"]
TOPIC_CHAT_ID = config["TELEGRAM"]["TOPIC_CHAT_ID"]
BOT_TOKEN = config["TELEGRAM"]["BOT_TOKEN"]

def send_message(text):
    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ms;q=0.8',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
}
    params = {'message_thread_id': TOPIC_CHAT_ID, 'chat_id': CHAT_ID,'text': text}
    response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',params=params,headers=headers,)
    if response.status_code == 200:
        logging.info(f"{Fore.GREEN}W00T!{Fore.RESET}")
    else:
        logging.info(f"{Fore.RED}FAILED!{Fore.RESET}")