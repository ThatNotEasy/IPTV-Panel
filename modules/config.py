from dotenv import load_dotenv
import configparser

load_dotenv('.env')

def setup_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config