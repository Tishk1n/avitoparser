import asyncio
import datetime
import os
import random
import shutil
import string

from playwright.async_api import async_playwright, Page
import urllib.request
from playwright._impl._api_types import TimeoutError

from bs4 import BeautifulSoup

from config import bot, MANAGER_ID, temp_folder
from database import Search, update_resent_seen_db, get_searches_db, get_user_db, User


async def parse_item(page: Page, url: str):
    class SearchResult:
        def __init__(self, title: str, link: str, place: str, image: str, price: str, about: str):
            self.title = title
            self.link = link
            self.place = place
            self.image = image
            self.price = price
            self.about = about

    await page.goto(url, wait_until="domcontentloaded")
    html = await page.inner_html('.iva-item-content-rejJg')
    soup = BeautifulSoup(html, 'lxml')

    # title
    title_element = soup.find('div', {'class': 'iva-item-titleStep-pdebR'}).find('a')

    title = title_element.text
    url = 'https://www.avito.ru' + title_element.get('href')

    # image
    image = soup.find('img', {'class': 'photo-slider-image-YqMGj'})['src']
    try:
        place = soup.find('span', {'class': 'geo-address-fhHd0'}).find('span').text
    except:
        place = None

    # price
    price = soup.find('meta', itemprop='price')['content']

    about = soup.find('div', {'class': 'iva-item-text-Ge6dR'}).text

    return SearchResult(title, url, place, image, price, about)


async def parser(searches: [Search]):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        page = await browser.new_page()

        for search in searches:
            user: User = await get_user_db(search.creator_id)
            if user.membership_activate and user.membership_activate >= datetime.date.today() or int(
                    user.user_id) == MANAGER_ID:
                try:
                    item = await parse_item(page, search.search)
                except TimeoutError:
                    try:
                        item = await parse_item(page, search.search)
                    except:
                        continue
                except Exception as e:
                    continue
                if item.title != search.resent_seen_title or not search.resent_seen_title:
                    await update_resent_seen_db(search.id, item.title)

                    if not search.resent_seen_title:
                        continue

                    image_path = await download_image(item.image)

                    await bot.send_photo(search.creator_id, open(image_path, 'rb'),
                                         f'Появилось новое объявление:\n\n{item.title}\n{item.place}\n{item.price}₽\n\n{item.about}\n\n{item.link}')

            else:
                continue
        await delete_temp()
        await browser.close()


async def scheduler():
    while True:
        try:
            searches = await get_searches_db()
            await parser(searches) if searches else None
            await asyncio.sleep(5)
        except:
            pass


async def download_image(url):
    filename = ''.join(random.choice(string.ascii_letters) for i in range(12)) + '.jpg'
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    file_path = urllib.request.urlretrieve(url, f'{temp_folder}\{filename}')[0]
    return file_path


async def delete_temp():
    files = os.listdir(temp_folder)

    for file in files:
        file_path = os.path.join(temp_folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
