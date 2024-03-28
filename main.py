from os import getenv
from time import sleep

from random import choice
from string import ascii_lowercase, ascii_uppercase, digits
from dotenv import load_dotenv
from telegram.ext import (
    CallbackContext,Updater, JobQueue
)
from telegram import Bot, ReplyKeyboardMarkup, Update

import robokassa as rk

load_dotenv()

TOKEN = getenv('token')
MERCHANT_LOGIN = getenv('login')
PASSWORD = getenv('password')

START = (
    'Привет! Я бот для покупки VPN.\n'
    'Чтобы купить VPN, нажмите \'приобрести VPN\'.\n'
    'Если у вас есть вопросы, нажмите \'справка\' или \'поддержка\'.'
)

PAYMENT_PERIODS = (
    ('1 месяц', 299),
    ('3 месяца', 599),
    ('6 месяцев', 999),
    ('12 месяцев', 1599),
)
CURRENCY = '₽'
PURCHASE_VPN = ('Приобрести VPN', PAYMENT_PERIODS,)
INFO = ('Справка', 'some info_text',)
SUPPORT = ('Поддержка', 'some support_text',)

PROMOCODE_SIZE = 10
PAYMENT_UPDATE_INTERVAL = 10  # seconds
PAYMENT_QUEUE_INTERVAL = 60 * 60  # seconds
PAYMENT_QUEUE_TIMEOUT = (
    'Payment  queue timeout!'
    'If the money was debited from the account'
    'but the code did not arrive within 60 minutes,'
    'then write to us in support'
)

MAIN_ENDPOINT = 'https://auth.robokassa.ru/Merchant/Index.aspx'


def promocode_match(promo: str) -> bool:

    promo_path = ''

    try:
        with open(promo_path, 'w') as file:
            promocodes = file.readlines
    except FileNotFoundError as err:
        raise SystemExit(err)
    else:
        if promo not in promocodes:
            file.write(f'\n{promo}')
        file.close()
        return promo in promocodes


def generate_promocode(size: str = PROMOCODE_SIZE) -> str | None:

    promocode = ''.join(
        choice(
            ascii_lowercase + ascii_uppercase + digits
        ) for _ in range(size)
    )

    return promocode if not promocode_match(promocode) else None


def start(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=START,
        reply_markup=ReplyKeyboardMarkup(
            [
                [PURCHASE_VPN[0], INFO[0], SUPPORT[0]]
            ]
        )
    )


def invoke_subscription(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    out_sum = update.message.text[-1].split()[1][:-1]
    invoice_id = f'{user_id}_{chat_id}'
    descriptions = 'Telegram subscription'

    payment_link = rk.generate_payment_link(
        merchant_login=MERCHANT_LOGIN,
        merchant_password_1=PASSWORD,
        cost=out_sum,
        number=invoice_id,
        description=descriptions,
        robokassa_payment_url=MAIN_ENDPOINT,
    )

    update.message.reply_text(
        (
            'Перейдите по ссылке, чтобы оплатить подписку'
            f'{payment_link}'
        )
    )


def handle_text(update: Update, context: CallbackContext) -> None:

    current_chat = update.effective_chat
    msg = update.message.text
    bot = context.bot

    if msg == PURCHASE_VPN[0]:
        bot.send_message(
            chat_id=current_chat.id,
            text=None,
            reply_markup=ReplyKeyboardMarkup(
                [
                    [f'{x[0]} {x[1]}{CURRENCY}' for x in PAYMENT_PERIODS]
                ]
            )
        )
    elif any([x[0] == msg for x in PAYMENT_PERIODS]):

        invoke_subscription(update=update, context=context)

        job_queue = JobQueue(bot)
        job_queue.run_repeating(
            callback=callback_payment,
            interval=PAYMENT_UPDATE_INTERVAL
        )
        job_queue.start()
    else:
        if msg == INFO[0] or msg == SUPPORT[0]:
            bot.send_message(
                chat_id=current_chat.id,
                text='Some text'
            )
        else:
            bot.send_message(
                chat_id=current_chat.id,
                text='Unknown'
            )


def callback_payment(update: Update, context: CallbackContext) -> None:

    data = context.job.context
    signature = rk.calculate_signature(data, PASSWORD)

    queue_interval = PAYMENT_QUEUE_INTERVAL

    while queue_interval > 0:

        if signature == data.get('SignatureValue'):
            if data.get('ResultCode') == '0':
                out_sum = data.get('OutSum')
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Successeful payment {out_sum}"
                )
            else:
                pass
        else:
            raise ValueError("Invalid SignatureValue")

        queue_interval = queue_interval - PAYMENT_UPDATE_INTERVAL
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=PAYMENT_QUEUE_TIMEOUT
        )


def main():

    bot = Bot(token=TOKEN)
    bot.infinity_polling(True)

    updater = Updater(token=TOKEN, use_context=True)
    
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':

    main()
