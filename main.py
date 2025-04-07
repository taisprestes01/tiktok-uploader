import os
import urllib.parse
import threading
import requests
from flask import Flask, request
from dotenv import load_dotenv
import time

load_dotenv()

CLIENT_KEY = os.getenv("CLIENT_KEY")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
VIDEO_PATH = os.getenv("VIDEO_PATH")

code_holder = {}

app = Flask(__name__)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    code_holder["code"] = code
    return "Authorization code received. You can close this tab."

def run_flask():
    app.run(port=8080)
import webbrowser

def generate_auth_url():
    scopes = ['video.upload']
    state = '123abc'
    params = {
        'client_key': CLIENT_KEY,
        'response_type': 'code',
        'scope': ' '.join(scopes),
        'redirect_uri': REDIRECT_URI,
        'state': state
    }
    auth_url = f"https://www.tiktok.com/v2/auth/authorize/?{urllib.parse.urlencode(params)}"
    print(f"Opening browser to authorize:\n{auth_url}")
    webbrowser.open(auth_url)


def get_access_token(code):
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=headers, data=data)
    result = response.json()
    access_token = result.get("access_token") or result.get("data", {}).get("access_token")
    return access_token

def upload_video(access_token):
    video_size = os.path.getsize(VIDEO_PATH)

    init_url = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    init_payload = {
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": video_size,
            "total_chunk_count": 1
        }
    }

    init_res = requests.post(init_url, headers=headers, json=init_payload)
    init_data = init_res.json()

    if init_data.get("error", {}).get("code") != "ok":
        print("Error initializing upload:", init_data)
        return

    upload_url = init_data["data"]["upload_url"]
    publish_id = init_data["data"]["publish_id"]
    print("Upload started. Publish ID:", publish_id)

    with open(VIDEO_PATH, "rb") as video_file:
        video_data = video_file.read()

    upload_headers = {
        "Content-Type": "video/mp4"
    }

    upload_res = requests.put(upload_url, headers=upload_headers, data=video_data)

    print("Status:", upload_res.status_code)
    print("Response:", upload_res.text)

    if upload_res.status_code == 200:
        print("Video uploaded successfully. Check the TikTok app.")
    else:
        print("Failed to upload video.")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    generate_auth_url()

    print("Waiting for authorization code...")
    while "code" not in code_holder:
        time.sleep(0.2)

    access_token = get_access_token(code_holder["code"])
    if access_token:
        upload_video(access_token)
