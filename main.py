import asyncio
import os
import glob
from core.loader import Loader
from core.validator import Validator
from core.spider import Spider

async def process_file(file_path, validator, spider, loader):
    print(f"\n[任务] 正在处理列表: {os.path.basename(file_path)}")
    channels = loader.load_m3u(file_path)
    if not channels:
        print(f"  ⚠️ 文件为空或格式错误，跳过。")
        return

    updated_count = 0
    for ch in channels:
        # 1. 验证现有地址
        if await validator.validate(ch['url']):
            print(f"  ✅ {ch['name']} 有效")
        else:
            print(f"  ❌ {ch['name']} 失效，尝试修复...")
            # 2. 搜索新源
            new_sources = await spider.search(ch['name'])
            found = False
            for src in new_sources:
                if await validator.validate(src):
                    print(f"  ✨ {ch['name']} 修复成功")
                    ch['url'] = src
                    updated_count += 1
                    found = True
                    break
            if not found:
                print(f"  💀 {ch['name']} 修复失败")

    # 3. 覆盖写回原文件
    loader.save_m3u(channels, file_path)
    print(f"[完成] {os.path.basename(file_path)} 更新完毕，修复了 {updated_count} 条链接。")

async def main():
    loader = Loader()
    validator = Validator()
    spider = Spider()
    
    # 获取 output 目录下所有的 m3u 文件
    target_files = glob.glob("output/*.m3u")
    
    if not target_files:
        print("Error: output 目录下未发现 .m3u 文件。")
        return

    for f in target_files:
        await process_file(f, validator, spider, loader)

if __name__ == "__main__":
    asyncio.run(main())
