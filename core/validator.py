import aiohttp
import asyncio

class Validator:
    def __init__(self):
        self.headers = {
            "User-Agent": "VLC/3.0.12 LibVLC/3.0.12",
            "Accept": "*/*"
        }

    async def validate(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                # 增加 allow_redirects=True 处理跳转源
                async with session.get(url, timeout=8, headers=self.headers, allow_redirects=True) as response:
                    if response.status == 200:
                        ct = response.headers.get('Content-Type', '').lower()
                        # 必须包含视频流或 M3U 特征
                        if any(x in ct for x in ['video', 'mpegurl', 'octet-stream', 'application/x-mpegurl']):
                            # 尝试读取数据片段，确保不是空流
                            content = await response.content.read(512)
                            return len(content) > 0
        except:
            pass
        return False
