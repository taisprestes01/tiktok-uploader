from flask import Flask, request
from threading import Thread
import time

code_holder = {}

app = Flask(__name__)

@app.route("/callback")
def callback():
    code_holder["code"] = request.args.get("code")
    return "Authorization code received. You can close this tab."

def start_flask():
    Thread(target=app.run, kwargs={"port": 8080}).start()

def wait_for_code():
    while "code" not in code_holder:
        time.sleep(0.2)
    return code_holder["code"]
