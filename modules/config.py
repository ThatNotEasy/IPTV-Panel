from configparser import ConfigParser

def setup_config():
    config = ConfigParser()
    config.read('config.ini')
    return config