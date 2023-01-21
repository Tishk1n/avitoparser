import asyncio
import os

from aiogram.utils import executor

import main

from config import dp, temp_folder, MANAGER_ID
from database import create_db, add_search_db
from service import scheduler

main.register_message_handlers(dp)


async def on_startup(_):
    create_db()
    asyncio.create_task(scheduler())
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    print('Бот запущен!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
