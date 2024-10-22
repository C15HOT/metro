import asyncio
import json
from unicodedata import category
import aiohttp
from bs4 import BeautifulSoup
import time



base_url = f"https://online.metro-cc.ru"
category = f"chaj-kofe-kakao/kofe"


async def get_page(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            return html


async def get_pages_count(url: str) -> int:
    html = await get_page(url)
    soup = BeautifulSoup(html, 'html.parser')
    pages = soup.find_all('a', {'class': 'v-pagination__item'})
    return int(pages[-1].text)


async def get_page_data(page: int, url: str) -> list:
    links = []
    html = await get_page(url=f"{url}&page={page}")
    soup = BeautifulSoup(html, 'html.parser')
    _links = soup.find_all('a', {'class', 'product-card-name'})
    for link in _links:
        links.append(link.get('href'))
    return links

async def get_good_info(link: str):
    html = await get_page(base_url+link)
    soup = BeautifulSoup(html, 'html.parser')

    id = soup.find('p', {'itemprop': 'productID'})
    if not id:
        return
    id = ''.join((x for x in id.text if x.isdigit()))

    h1 = soup.find('h1')
    name = h1.find('span').text.split('\n')[1]
    actual_div = soup.find('div', {'class': 'product-unit-prices__actual-wrapper'})
    if not actual_div:
        return
    actual_price = actual_div.find('span', {'class': 'product-price__sum-rubles'}).text
    actual_price = int(''.join(i for i in actual_price if i.isdigit()))



    old_div = soup.find('div', {'class': 'product-unit-prices__old-wrapper'})
    old_price = old_div.find('span', {'class': 'product-price__sum-rubles'})
    if old_price:
        old_price = int(''.join(i for i in old_price.text if i.isdigit()))
    else:
        old_price = None


    params_ul = soup.find('ul', {'class': 'product-attributes__list'})
    params_li = params_ul.find_all('li')
    brand = None
    for li in params_li:
        if 'Бренд' in li.find('span', {'class': 'product-attributes__list-item-name-text'}).text:
            brand = li.find('a').text.split('\n')[1]



    good = {'id': id,
            'name': name,
            'actual_price': actual_price,
            'old_price': old_price,
            'brand': brand,
            'link': base_url+link}
    return good

async def get_goods_links():
    links = []
    url = base_url+f'/category/{category}?from=under_search'
    pages_count = await get_pages_count(url=url)
    tasks = []
    for page in range(pages_count + 1):
        task = asyncio.ensure_future(get_page_data(page, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    for _list in results:
        links.extend(_list)
    data_tasks = []
    for link in links:
        task = asyncio.ensure_future(get_good_info(link))
        data_tasks.append(task)
    data = await asyncio.gather(*data_tasks)
    data = list(filter(lambda item: item is not None, data))
    print(len(data))
    with open ('moscow_coffee.json', "w") as f:
        json.dump(data, f)

start_time = time.time()
asyncio.run(get_goods_links())
print("--- %s seconds ---" % (time.time() - start_time))
