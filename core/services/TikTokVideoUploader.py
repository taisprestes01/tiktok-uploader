from core.interfaces.IVideoUploader import IVideoUploader
import os
import requests
from config import VIDEO_PATH

class TikTokVideoUploader(IVideoUploader):
    def upload(self, access_token: str) -> str:
        video_size = os.path.getsize(VIDEO_PATH)

        init_payload = {
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_size,
                "chunk_size": video_size,
                "total_chunk_count": 1
            }
        }

        init_res = requests.post("https://open.tiktokapis.com/v2/post/publish/inbox/video/init/",
                                 headers={
                                     "Authorization": f"Bearer {access_token}",
                                     "Content-Type": "application/json"
                                 },
                                 json=init_payload)

        init_data = init_res.json()
        if init_data.get("error", {}).get("code") != "ok":
            raise Exception(f"Erro ao iniciar upload: {init_data}")

        upload_url = init_data["data"]["upload_url"]
        publish_id = init_data["data"]["publish_id"]

        with open(VIDEO_PATH, "rb") as f:
            video_data = f.read()

        upload_res = requests.put(upload_url,
                                  headers={"Content-Type": "video/mp4"},
                                  data=video_data)

        if upload_res.status_code != 200:
            raise Exception(f"Erro ao enviar vídeo: {upload_res}")

        return publish_id
