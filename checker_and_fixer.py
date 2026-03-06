import asyncio
import aiohttp
import re
import os
import sys

# --- 核心修复：手动指定路径，防止 GitHub Actions 找不到 spider.py ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from spider import Spider
except ImportError:
    import importlib.util
    # 尝试直接通过文件路径加载 spider.py
    spec = importlib.util.spec_from_file_location("spider", os.path.join(os.getcwd(), "spider.py"))
    spider_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(spider_mod)
    Spider = spider_mod.Spider
# ------------------------------------------------------------------

# --- 配置 ---
INPUT_FILE = "output/merged.m3u"
OUTPUT_FILE = "output/cleaned.m3u" # 建议先输出到新文件，确认无误再覆盖
CONCURRENT_LIMIT = 20  # 同时检测的连接数
TIMEOUT = 5            # 每个链接的超时时间（秒）

class IPTVFixer:
    def __init__(self):
        self.spider = Spider()
        self.semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)

    async def check_url(self, session, url):
        """检测单个 URL 是否有效"""
        async with self.semaphore:
            try:
                # 模拟播放器 UA
                headers = {"User-Agent": "VLC/3.0.12 LibVLC/3.0.12"}
                async with session.get(url, timeout=TIMEOUT, headers=headers) as response:
                    # 只要状态码是 200，且内容类型看起来像视频流
                    if response.status == 200:
                        return True
            except:
                pass
            return False

    def parse_m3u(self, content):
        """简单的 M3U 解析，提取频道名和 URL"""
        items = []
        current_item = {}
        for line in content.splitlines():
            if line.startswith("#EXTINF"):
                name = line.split(",")[-1].strip()
                current_item = {"name": name, "line": line}
            elif line.startswith("http"):
                current_item["url"] = line.strip()
                items.append(current_item)
                current_item = {}
        return items

    async def process(self):
        if not os.path.exists(INPUT_FILE):
            print(f"文件 {INPUT_FILE} 不存在，请先运行 spider.py")
            return

        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        channels = self.parse_m3u(content)
        print(f"开始检测 {len(channels)} 个频道...")

        async with aiohttp.ClientSession() as session:
            # 1. 批量检测现有链接
            tasks = [self.check_url(session, ch['url']) for ch in channels]
            results = await asyncio.gather(*tasks)

            final_m3u = ["#EXTM3U"]
            
            for i, is_valid in enumerate(results):
                ch = channels[i]
                if is_valid:
                    final_m3u.append(ch['line'])
                    final_m3u.append(ch['url'])
                else:
                    print(f"发现失效: {ch['name']}，尝试重新搜索...")
                    # 2. 调用你 spider.py 里的 search 方法
                    new_links = await self.spider.search(ch['name'])
                    
                    found_fix = False
                    for link in new_links:
                        if await self.check_url(session, link):
                            print(f"✅ 已修复 {ch['name']}: {link}")
                            final_m3u.append(ch['line'])
                            final_m3u.append(link)
                            found_fix = True
                            break
                    
                    if not found_fix:
                        print(f"❌ 无法修复 {ch['name']}")

        # 3. 保存结果
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(final_m3u))
        print(f"任务完成！结果已保存至 {OUTPUT_FILE}")

if __name__ == "__main__":
    fixer = IPTVFixer()
    asyncio.run(fixer.process())
