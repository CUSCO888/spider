import time
import asyncio
import aiohttp

async def validate_urls(urls):
    """并发验证一组 URL，返回有效的并按速度排序"""
    valid_list = []
    async def check(session, url):
        try:
            start = time.time()
            async with session.get(url, timeout=5, ssl=False) as resp:
                if resp.status == 200:
                    cost = (time.time() - start) * 1000
                    return (url, cost)
        except:
            pass
        return None

    urls = list(set(urls))
    async with aiohttp.ClientSession() as session:
        tasks = [check(session, u) for u in urls]
        results = await asyncio.gather(*tasks)
        results_filtered = [r for r in results if r]
        results_filtered.sort(key=lambda x: x[1])
    return [v[0] for v in results_filtered]
