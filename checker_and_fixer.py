import requests
import concurrent.futures
from your_spider_module import search_fofa_for_channel # 假设这是你现有的爬虫函数

# --- 配置区 ---
SOURCE_FILE = "output/merged.m3u"
TIMEOUT = 5  # 检测超时时间（秒）
MAX_WORKERS = 10 # 并发检测线程数
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

class IPTVManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.channels = [] # 格式: [{"name": "CCTV1", "url": "http://...", "valid": True}]

    def check_url(self, channel):
        """检测单个 URL 是否有效"""
        try:
            # 使用 HEAD 请求节省带宽，模拟真实播放器 UA
            response = requests.head(channel['url'], timeout=TIMEOUT, headers={"User-Agent": UA}, allow_redirects=True)
            if response.status_code == 200:
                return True
        except:
            pass
        return False

    def run_check(self):
        """并发检测所有频道"""
        print(f"开始检测 {len(self.channels)} 个频道...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_ch = {executor.submit(self.check_url, ch): ch for ch in self.channels}
            for future in concurrent.futures.as_completed(future_to_ch):
                ch = future_to_ch[future]
                ch['valid'] = future.result()

    def fix_invalid_channels(self):
        """核心：对失效的频道重新触发抓取"""
        for ch in self.channels:
            if not ch['valid']:
                print(f"检测到失效: {ch['name']}，正在重新获取...")
                # 调用你现有的爬虫逻辑去搜新地址
                new_urls = search_fofa_for_channel(ch['name']) 
                
                if new_urls:
                    # 对搜到的新地址进行“速检”，选出第一个可用的
                    for new_url in new_urls:
                        if self.check_url({"url": new_url}):
                            print(f"成功修复 {ch['name']} -> {new_url}")
                            ch['url'] = new_url
                            ch['valid'] = True
                            break
                else:
                    print(f"未能找到 {ch['name']} 的可用新源")

    def save_results(self):
        """覆盖原始 M3U 文件"""
        # 这里编写将 self.channels 写回 M3U 格式的逻辑
        pass

# --- 主程序 ---
if __name__ == "__main__":
    manager = IPTVManager(SOURCE_FILE)
    # 1. 加载现有的 m3u
    # 2. manager.run_check()
    # 3. manager.fix_invalid_channels()
    # 4. manager.save_results()
