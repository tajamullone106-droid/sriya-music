import os
import re
import asyncio
import aiohttp
from pathlib import Path

from py_yt import Playlist, VideosSearch
from anony import logger, app  # (app 👈 Pyrogram क्लाइंट को इम्पोर्ट किया ताकि Telegram से फ़ास्ट डाउनलोड हो)
from anony.helpers import Track, utils

# --- आपका नया कस्टम Nobita Music API Config ---
API_URL = "https://nobita-music-api.onrender.com"
# आपने बॉट से जो API Key बनाई है, उसे यहाँ डालें 👇
API_KEY = "feccdadd-0dd4-469a-a965-d17f2dafd9df" 

DOWNLOAD_DIR = "downloads"

class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.checked = True 
        self.cookie_dir = "anony/cookies"
        self.warned = False
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )

    def get_cookies(self):
        return None

    async def save_cookies(self, urls: list[str]) -> None:
        pass

    async def download(self, video_id: str, video: bool = False) -> str | None:
        if not video_id or len(video_id) < 3:
            return None

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        ext = "mp4" if video else "mp3"
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")

        # अगर गाना पहले से सर्वर पर डाउनलोड है, तो तुरंत प्ले करेगा
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path

        mode = "video" if video else "audio"
        
        try:
            # 1. Nobita API से रिक्वेस्ट करना
            async with aiohttp.ClientSession() as session:
                api_link = f"{API_URL}/api/play?api_key={API_KEY}&type={mode}&query={video_id}"
                
                async with session.get(api_link, timeout=aiohttp.ClientTimeout(total=300)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        if data.get("status") == "success":
                            # API से File ID निकालना
                            file_id = data["data"]["file_id"]
                            
                            # 2. Pyrogram (app) का इस्तेमाल करके Telegram सर्वर से फ़ास्ट डाउनलोड करना
                            await app.download_media(
                                message=file_id,
                                file_name=file_path
                            )
                            
                            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                                return file_path
                        else:
                            logger.error(f"Nobita API Error: {data.get('error')}")
                    else:
                        logger.error(f"API Http Error: Status {resp.status}")
        except Exception as e:
            logger.error(f"Nobita API Download Error: {e}")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
        return None

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        try:
            _search = VideosSearch(query, limit=1)
            results = await _search.next()
            if results and results["result"]:
                data = results["result"][0]
                return Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name"),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")),
                    message_id=m_id,
                    title=data.get("title")[:25],
                    thumbnail=data.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                    url=data.get("link"),
                    view_count=data.get("viewCount", {}).get("short"),
                    video=video,
                )
        except Exception as e:
            logger.error(f"Search Error: {e}")
            return None

    async def playlist(self, limit: int, user: str, url: str, video: bool) -> list:
        tracks = []
        try:
            plist = await Playlist.get(url)
            for data in plist["videos"][:limit]:
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")),
                    title=data.get("title")[:25],
                    thumbnail=data.get("thumbnails")[-1].get("url").split("?")[0],
                    url=data.get("link").split("&list=")[0],
                    user=user,
                    view_count="",
                    video=video,
                )
                tracks.append(track)
        except Exception as e:
            logger.error(f"Playlist Error: {e}")
        return tracks
