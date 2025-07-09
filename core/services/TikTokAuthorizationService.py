from core.interfaces.IAuthorizationService import IAuthorizationService
import urllib.parse
import requests
from config import CLIENT_KEY, CLIENT_SECRET, REDIRECT_URI

class TikTokAuthorizationService(IAuthorizationService):
    def generate_auth_url(self) -> str:
        scopes = [
            'video.publish'
        ]
        params = {
            'client_key': CLIENT_KEY,
            'response_type': 'code',
            'scope': ' '.join(scopes),
            'redirect_uri': REDIRECT_URI,
            'state': '123abc'
        }
        return f"https://www.tiktok.com/v2/auth/authorize/?{urllib.parse.urlencode(params)}"

    def get_access_token(self, code: str) -> str:
        response = requests.post("https://open.tiktokapis.com/v2/oauth/token/", data={
            "client_key": CLIENT_KEY,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})

        result = response.json()
        return result.get("access_token") or result.get("data", {}).get("access_token")
