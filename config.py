import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

temp_folder = os.getcwd() + '\\tmp'

TOKEN = '5218712793:AAE6d5BPRVF57t-E78lJlU0TE-oceicVdbY'
MANAGER_ID = 7757078362

db = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=db)
