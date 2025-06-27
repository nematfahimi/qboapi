import os
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('QUICKBOOKS_CLIENT_ID')
REDIRECT_URI = os.getenv('QUICKBOOKS_REDIRECT_URI')

SCOPES = [
    "com.intuit.quickbooks.accounting",
    "openid",
    "profile",
    "email",
    "phone",
    "address"
]

AUTH_BASE_URL = "https://appcenter.intuit.com/connect/oauth2"

def build_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "state": "random_string"
    }
    return f"{AUTH_BASE_URL}?{urlencode(params)}"

if __name__ == "__main__":
    print("روی این لینک کلیک کن و بعد از لاگین، کد را بردار:")
    print(build_auth_url())
