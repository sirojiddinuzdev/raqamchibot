import asyncio
from config import SPIDER_API_KEY
from spider_api import SpiderAPI

async def main():
    spider = SpiderAPI(SPIDER_API_KEY)
    c = await spider.get_countries()
    print(c)

asyncio.run(main())
