from asyncio import run, get_running_loop
from logging import basicConfig, INFO

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from storage import storage
from handlers import router as main_router
from utils import auto_save_storage


async def save_data_before_crash():
    await storage.save_storage()


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    dp.include_router(main_router)
    dp.shutdown.register(save_data_before_crash)

    loop = get_running_loop()
    loop.create_task(auto_save_storage(storage))

    await dp.start_polling(bot)


if __name__ == "__main__":
    basicConfig(
        level=INFO,
        filename="/usr/log/bot/logs.txt",
        format="%(asctime)s.%(msecs)03d - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    run(main())