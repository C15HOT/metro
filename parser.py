import asyncio
from pprint import pprint
from unicodedata import category

import aiohttp
from bs4 import BeautifulSoup
import time



base_url = f"https://online.metro-cc.ru/"
category = f"chaj-kofe-kakao/kofe"
category = 'bezalkogolnye-napitki/pityevaya-voda-kulery'

async def get_page(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            return html


async def get_pages_count(url):
    html = await get_page(url)
    soup = BeautifulSoup(html, 'html.parser')
    pages = soup.find_all('a', {'class': 'v-pagination__item'})
    return int(pages[-1].text)


async def get_page_data(page, url):
    links = []
    html = await get_page(url=f"{url}&page={page}")
    soup = BeautifulSoup(html, 'html.parser')
    _links = soup.find_all('a', {'class', 'product-card-name'})
    for link in _links:
        links.append(link.get('href'))
    return links

async def get_goods_links():
    links = []
    url = base_url+f'category/{category}?from=under_search'
    pages_count = await get_pages_count(url=url)
    tasks = []
    for page in range(pages_count + 1):
        task = asyncio.ensure_future(get_page_data(page, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    for list in results:
        links.extend(list)
    print(len(links))
    return links


start_time = time.time()
asyncio.run(get_goods_links())
print("--- %s seconds ---" % (time.time() - start_time))
