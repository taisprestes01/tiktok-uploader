import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_KEY = os.getenv("CLIENT_KEY")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
VIDEO_PATH = os.getenv("VIDEO_PATH")

DEFAULT_VIDEO_TITLE = os.getenv("DEFAULT_VIDEO_TITLE", "")
DEFAULT_PRIVACY_LEVEL = os.getenv("DEFAULT_PRIVACY_LEVEL", "SELF_ONLY")
AUTO_PUBLISH = os.getenv("AUTO_PUBLISH", "false").lower() == "true"
