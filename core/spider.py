import aiohttp
import re
import logging

logger = logging.getLogger(__name__)

class Spider:
    async def search(self, keyword):
        """去 Tonkiang 搜索关键字，返回找到的所有 m3u/直播源链接"""
        logger.info(f"正在搜索关键字: {keyword}")
        search_url = f"http://tonkiang.us/hoteliptv.php?s={keyword}"
        candidates = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, timeout=15) as response:
                    text = await response.text()
                    links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
                    candidates = [l for l in links if '.m3u' in l or '/udp/' in l or '/hls/' in l]
        except Exception as e:
            logger.error(f"搜索失败 {keyword}: {e}")
        return list(set(candidates))

    async def fetch_playlist_content(self, url):
        """获取外部播放列表内容"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        return await response.text()
        except:
            pass
        return ""
