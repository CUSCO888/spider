import asyncio
import os
import logging
from core.loader import load_m3u_files
from core.spider import Spider
from core.matcher import match_channels
from core.validator import validate_urls

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    # 1. 读取 output 文件夹里的现有文件
    files_data = load_m3u_files("output")
    if not files_data:
        logger.warning("Output 文件夹为空，没有需要维护的文件。")
        return

    spider = Spider()

    # 2. 遍历每个文件进行处理
    for filename, channels in files_data.items():
        logger.info(f"=== 正在处理文件: {filename} ===")
        keyword = filename.replace(".m3u", "").replace(".m3u8", "")
        
        # 3. 爬虫抓取
        candidate_urls = await spider.search(keyword)
        tasks = [spider.fetch_playlist_content(u) for u in candidate_urls]
        external_playlists = await asyncio.gather(*tasks)
        
        # 4. 匹配与更新
        updated_content = []
        target_channel_names = list(channels.keys())
        
        for channel_name in target_channel_names:
            logger.info(f"正在为 {channel_name} 寻找新源...")
            potential_urls = []
            
            for playlist_text in external_playlists:
                if playlist_text:
                    matches = match_channels([channel_name], playlist_text)
                    if channel_name in matches:
                        potential_urls.extend(matches[channel_name])
            
            old_url = channels.get(channel_name)
            if old_url:
                potential_urls.append(old_url)
            
            potential_urls = list(set(potential_urls))
            
            # 5. 验证
            if potential_urls:
                valid_urls = await validate_urls(potential_urls)
                if valid_urls:
                    best_url = valid_urls[0]
                    logger.info(f"✅ {channel_name} 更新成功 (找到 {len(valid_urls)} 个源)")
                    updated_content.append(f"#EXTINF:-1 group-title=\"Auto\",{channel_name}\n{best_url}")
                    continue
            
            logger.warning(f"❌ {channel_name} 未找到有效新源")
            if old_url:
                updated_content.append(f"#EXTINF:-1 group-title=\"Auto\",{channel_name}\n{old_url}")

        # 6. 写回文件
        save_path = os.path.join("output", filename)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            f.write("\n".join(updated_content))
        logger.info(f"文件 {filename} 已更新完毕。")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
