
import os
import ConfigParser

CONFIG_FILE_NAME = os.environ.get("BOTO_CONFIG")
parser = ConfigParser.ConfigParser()
parser.read([CONFIG_FILE_NAME])

def get(section, name):
    return parser.get(section, name)

def github_client_id():
    return get("Credentials", "github_client_id")

def github_client_secret():
    return get("Credentials", "github_client_secret")
