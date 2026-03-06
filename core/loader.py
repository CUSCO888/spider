import os

class Loader:
    def load_m3u(self, file_path):
        """解析 M3U，返回包含元数据和 URL 的字典列表"""
        channels = []
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        current_inf = ""
        for line in lines:
            line = line.strip()
            if line.startswith("#EXTINF"):
                current_inf = line
            elif line.startswith("http") and current_inf:
                # 提取逗号后的频道名称
                name = current_inf.split(",")[-1].strip()
                channels.append({
                    "name": name, 
                    "inf": current_inf, 
                    "url": line
                })
                current_inf = ""
        return channels

    def save_m3u(self, channels, file_path):
        """写回文件"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for ch in channels:
                f.write(f"{ch['inf']}\n{ch['url']}\n")
