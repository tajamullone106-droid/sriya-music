Import os
import re
import asyncio
import aiohttp
from pathlib import Path

from py_yt import Playlist, VideosSearch
from anony import logger
from anony.helpers import Track, utils

# Fast Download API config (Bina Cookies ke download karne ke liye)
API_URL = os.environ.get("SHRUTI_API_URL", "https://api.shrutibots.site")
# @SHRUTIAPIBOT se mili hui API KEY yahan 'YOUR_API_KEY' ki jagah dalein ya fir .env mein SHRUTI_API_KEY laga dein
API_KEY = os.environ.get("SHRUTI_API_KEY", "ShrutiBotsFxBCNJG7gkajQqdBift3") 

DOWNLOAD_DIR = "downloads"

class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.checked = True  # Cookies bypass karne ke liye True rakha hai
        self.cookie_dir = "anony/cookies"
        self.warned = False
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )

    def get_cookies(self):
        # Ab cookies ki koi zaroorat nahi hai
        return None

    async def save_cookies(self, urls: list[str]) -> None:
        # Agar bot background mein ise call kare toh error na aaye, isliye pass kiya
        pass

    async def download(self, video_id: str, video: bool = False) -> str | None:
        if not video_id or len(video_id) < 3:
            return None

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        ext = "mp4" if video else "mp3"
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")

        # Agar gaana pehle se download hai, toh wahin se play karega
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path

        mode = "video" if video else "audio"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{API_URL}/download",
                    params={"url": video_id, "type": mode, "api_key": API_KEY},
                    timeout=aiohttp.ClientTimeout(total=600 if video else 300)
                ) as resp:
                    if resp.status == 200:
                        with open(file_path, "wb") as f:
                            async for chunk in resp.content.iter_chunked(131072):
                                f.write(chunk)
                        
                        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                            return file_path
                    else:
                        logger.error(f"API Error: Status {resp.status}")
        except Exception as e:
            logger.error(f"External API Download Error: {e}")
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

