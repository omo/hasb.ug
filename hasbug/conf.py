
import os
import ConfigParser

CONFIG_FILE_NAME = os.environ.get("BOTO_CONFIG")
parser = ConfigParser.ConfigParser()
parser.read([CONFIG_FILE_NAME])

def get(section, name):
    return parser.get(section, name)

def aws_access_key_id():
    return get("Credentials", "aws_access_key_id")

def aws_secret_access_key():
    return get("Credentials", "aws_secret_access_key")

def github_client_id():
    return get("Credentials", "github_client_id")

def github_client_secret():
    return get("Credentials", "github_client_secret")

def flask_secret_key():
    return get("Credentials", "flask_secret_key")

def google_api_key():
    return get("Credentials", "google_api_key")

def fake_google_api_key():
    parser.set("Credentials", "google_api_key", "fake")
