import os
import re

def load_m3u_files(output_dir="output"):
    """
    读取 output 目录下所有的 m3u 文件
    返回结构: { '文件名.m3u': {'频道名': '当前URL', ...} }
    """
    files_data = {}
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建了文件夹: {output_dir}，请放入你的 .m3u 文件")
        return {}

    for filename in os.listdir(output_dir):
        if filename.endswith((".m3u", ".m3u8")):
            filepath = os.path.join(output_dir, filename)
            channels = {}
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                current_extinf = None
                current_name = None
                for line in lines:
                    line = line.strip()
                    if line.startswith("#EXTINF"):
                        current_extinf = line
                        parts = line.split(',')
                        if len(parts) > 1:
                            current_name = parts[-1].strip()
                    elif line and not line.startswith("#") and current_name:
                        # 存储为 { 频道名: { 'url': URL, 'extinf': 完整的EXTINF行 } }
                        channels[current_name] = {
                            'url': line,
                            'extinf': current_extinf
                        }
                        current_name = None
                        current_extinf = None
                files_data[filename] = channels
                print(f"已加载 {filename}: 包含 {len(channels)} 个频道")
            except Exception as e:
                print(f"读取文件 {filename} 出错: {e}")
                
    return files_data
