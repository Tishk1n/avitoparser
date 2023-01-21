import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

temp_folder = os.getcwd() + '\\tmp'

TOKEN = '5974426398:AAHAdzVgk_j8UDc8eFsDF8DdedLeyPyhJPg'
MANAGER_ID = 5484667168

db = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=db)
