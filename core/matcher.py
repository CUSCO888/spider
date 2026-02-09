def match_channels(needed_channels, spider_results_text):
    """
    needed_channels: 你 m3u 里已有的频道名列表 ['CCTV-1', 'BBC News']
    spider_results_text: 爬虫爬下来的大段文本 (也就是别人的 m3u 内容)
    返回: { 'CCTV-1': ['新URL1', '新URL2'], ... }
    """
    matched_data = {}
    lines = spider_results_text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            # 这一行是频道名，下一行通常是URL
            found_name = line.split(',')[-1].strip()
            # 简单的模糊匹配
            for my_channel in needed_channels:
                if my_channel in found_name:
                    if i + 1 < len(lines):
                        url = lines[i+1].strip()
                        if url and not url.startswith("#"):
                            if my_channel not in matched_data:
                                matched_data[my_channel] = []
                            matched_data[my_channel].append(url)
    return matched_data
