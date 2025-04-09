import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_KEY = os.getenv("CLIENT_KEY")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
VIDEO_PATH = os.getenv("VIDEO_PATH")
