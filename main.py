from adapters import flask_web_server
from utils.browser_utils import open_browser
from core.services.TikTokAuthorizationService import TikTokAuthorizationService
from core.services.TikTokVideoUploader import TikTokVideoUploader
from config import DEFAULT_VIDEO_TITLE, DEFAULT_PRIVACY_LEVEL, AUTO_PUBLISH

def main():
    flask_web_server.start_flask()

    auth_service = TikTokAuthorizationService()
    uploader = TikTokVideoUploader()

    auth_url = auth_service.generate_auth_url()
    open_browser(auth_url)

    code = flask_web_server.wait_for_code()
    token = auth_service.get_access_token(code)

    if token:
        print("Starting video upload and publication...")
        
        title = input(f"Enter video title (or press Enter to use '{DEFAULT_VIDEO_TITLE}'): ").strip()
        if not title:
            title = DEFAULT_VIDEO_TITLE or ""
        
        print(f"Current privacy level: {DEFAULT_PRIVACY_LEVEL}")
        privacy = input("Privacy level (1=Only me, 2=Friends, 3=Public) [Enter to keep current]: ").strip()
        
        privacy_map = {
            "1": "SELF_ONLY",
            "2": "MUTUAL_FOLLOW_FRIENDS", 
            "3": "PUBLIC"
        }
        
        privacy_level = privacy_map.get(privacy, DEFAULT_PRIVACY_LEVEL) if privacy else DEFAULT_PRIVACY_LEVEL
        
        print(f"Final configuration:")
        print(f"   Title: {title}")
        print(f"   Privacy: {privacy_level}")
        
        try:
            publish_id = uploader.upload(token, title, privacy_level)
            print(f"Process completed! Publish ID: {publish_id}")
        except Exception as e:
            print(f"Error during process: {e}")

if __name__ == "__main__":
    main()
