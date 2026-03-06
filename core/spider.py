import aiohttp
import re

class Spider:
    async def search(self, keyword):
        """针对特定频道名进行精准搜索"""
        search_url = f"http://tonkiang.us/hoteliptv.php?s={keyword}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, timeout=15, headers=headers) as resp:
                    text = await resp.text()
                    # 匹配 http/https 开头的 URL
                    links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
                    # 仅保留常见的直播流后缀或路径特征
                    candidates = [l for l in links if any(ext in l.lower() for ext in ['.m3u', '.m3u8', '.ts', '/udp/', '/hls/'])]
                    return list(set(candidates))
        except:
            return []
