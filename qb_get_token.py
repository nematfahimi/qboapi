import os
import requests
from dotenv import load_dotenv
from base64 import b64encode

load_dotenv()

CLIENT_ID = os.getenv('QUICKBOOKS_CLIENT_ID')
CLIENT_SECRET = os.getenv('QUICKBOOKS_CLIENT_SECRET')
REDIRECT_URI = os.getenv('QUICKBOOKS_REDIRECT_URI')

AUTHORIZATION_CODE = "XAB11751021740k3UZTncZfoarM5MIrGfh0otFMNYB0xUWKpEG"

token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

headers = {
    "Accept": "application/json",
    "Authorization": "Basic " + b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
    "Content-Type": "application/x-www-form-urlencoded"
}

data = {
    "grant_type": "authorization_code",
    "code": AUTHORIZATION_CODE,
    "redirect_uri": REDIRECT_URI
}

response = requests.post(token_url, headers=headers, data=data)
if response.status_code == 200:
    tokens = response.json()
    print("Access Token:", tokens.get('access_token'))
    print("Refresh Token:", tokens.get('refresh_token'))
    print("ID Token:", tokens.get('id_token'))
else:
    print("Error:", response.status_code)
    print(response.text)
