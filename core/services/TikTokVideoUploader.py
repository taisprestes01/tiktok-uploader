from core.interfaces.IVideoUploader import IVideoUploader
import os
import requests
import time
from config import VIDEO_PATH

class TikTokVideoUploader(IVideoUploader):
    def upload(self, access_token: str, title: str = "", privacy_level: str = "SELF_ONLY") -> str:
        if not VIDEO_PATH:
            raise Exception("VIDEO_PATH not configured in .env file")
            
        video_size = os.path.getsize(VIDEO_PATH)

        print("Getting creator information...")
        creator_info = self._query_creator_info(access_token)
        print(f"Creator: {creator_info.get('creator_nickname', 'N/A')}")
        
        print("Initializing upload...")
        init_data = self._init_video_upload(access_token, video_size, title, privacy_level)
        
        upload_url = init_data["upload_url"]
        publish_id = init_data["publish_id"]
        
        print(f"Publish ID: {publish_id}")

        print("Sending file...")
        self._upload_file(upload_url, video_size)
        
        print("Checking publication status...")
        self._check_publish_status(access_token, publish_id)
        
        return publish_id

    def _query_creator_info(self, access_token: str) -> dict:
        response = requests.post(
            "https://open.tiktokapis.com/v2/post/publish/creator_info/query/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=UTF-8"
            }
        )
        
        data = response.json()
        if data.get("error", {}).get("code") != "ok":
            raise Exception(f"Error getting creator information: {data}")
        
        creator_data = data.get("data", {})
        
        print(f"Username: @{creator_data.get('creator_username', 'N/A')}")
        print(f"Name: {creator_data.get('creator_nickname', 'N/A')}")
        print(f"Max duration: {creator_data.get('max_video_post_duration_sec', 0)}s")
        
        if creator_data.get('comment_disabled'):
            print("Comments disabled")
        if creator_data.get('duet_disabled'):
            print("Duet disabled")
        if creator_data.get('stitch_disabled'):
            print("Stitch disabled")
        
        return creator_data

    def _init_video_upload(self, access_token: str, video_size: int, title: str = "", privacy_level: str = "SELF_ONLY") -> dict:
        from config import DEFAULT_VIDEO_TITLE, DEFAULT_PRIVACY_LEVEL
        
        if not title:
            title = DEFAULT_VIDEO_TITLE or "Video sent via API"
        if not privacy_level:
            privacy_level = DEFAULT_PRIVACY_LEVEL or "SELF_ONLY"
        
        privacy_mapping = {
            "SELF_ONLY": "SELF_ONLY",
            "MUTUAL_FOLLOW_FRIENDS": "MUTUAL_FOLLOW_FRIENDS", 
            "PUBLIC": "PUBLIC_TO_EVERYONE"
        }
        
        api_privacy_level = privacy_mapping.get(privacy_level, "SELF_ONLY")
        
        if video_size > 100 * 1024 * 1024:
            print("Warning: Video too large (>100MB), may take time to process")
            
        init_payload = {
            "post_info": {
                "title": title,
                "privacy_level": api_privacy_level,
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
                "video_cover_timestamp_ms": 0
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_size,
                "chunk_size": min(video_size, 10000000),
                "total_chunk_count": max(1, (video_size + 9999999) // 10000000)
            }
        }

        print(f"Title: {title}")
        print(f"Privacy: {api_privacy_level}")
        print(f"Size: {video_size / (1024*1024):.1f}MB")

        response = requests.post(
            "https://open.tiktokapis.com/v2/post/publish/video/init/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=UTF-8"
            },
            json=init_payload
        )

        data = response.json()
        if data.get("error", {}).get("code") != "ok":
            raise Exception(f"Error initializing upload: {data}")

        return data.get("data", {})

    def _upload_file(self, upload_url: str, video_size: int):
        if not VIDEO_PATH:
            raise Exception("VIDEO_PATH not configured in .env file")
            
        print(f"Sending file: {os.path.basename(VIDEO_PATH)}")
        
        with open(VIDEO_PATH, "rb") as f:
            video_data = f.read()
        
        content_range = f"bytes 0-{video_size - 1}/{video_size}"
        
        response = requests.put(
            upload_url,
            headers={
                "Content-Range": content_range,
                "Content-Type": "video/mp4"
            },
            data=video_data
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Error sending file: {response.status_code} - {response.text}")
        
        print("File sent successfully!")

    def _check_publish_status(self, access_token: str, publish_id: str, max_attempts: int = 30):
        print(f"Checking publication status: {publish_id}")
        
        for attempt in range(max_attempts):
            response = requests.post(
                "https://open.tiktokapis.com/v2/post/publish/status/fetch/",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json; charset=UTF-8"
                },
                json={"publish_id": publish_id}
            )
            
            data = response.json()
            status = data.get("data", {}).get("status")
            
            if status == "SUCCESS":
                print("Video published successfully!")
                return data
            elif status == "FAILED":
                error_msg = data.get("data", {}).get("error_message", "Unknown error")
                raise Exception(f"Publication failed: {error_msg}")
            elif status == "PROCESSING":
                print(f"Processing... ({attempt + 1}/{max_attempts})")
                time.sleep(2)
            elif status == "PENDING":
                print(f"Waiting for processing... ({attempt + 1}/{max_attempts})")
                time.sleep(3)
            else:
                print(f"Status: {status}")
                time.sleep(2)
        
        raise Exception("Timeout: Publication took too long to process")

    def publish(self, access_token: str, publish_id: str, title: str = "", privacy_level: str = "SELF_ONLY") -> dict:
        print("Warning: Obsolete method. Use upload()")
        return {"status": "obsolete", "message": "Use upload() method instead"}
