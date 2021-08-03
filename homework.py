import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

from constants import Exit_Code, Http_Status_Code

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


_log_format = (
    '%(asctime)s - [%(levelname)s] -  %(name)s - '
    '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
)

_log_folder = r'./logs'


def get_file_handler(path, name):
    file_handler = logging.FileHandler(
        f'{path}/{name}', mode='a', encoding='utf8'
    )
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler(_log_folder, name))
    logger.addHandler(get_stream_handler())
    return logger


# проинициализируйте бота здесь,
# чтобы он был доступен в каждом нижеобъявленном методе,
# и не нужно было прокидывать его в каждый вызов
bot = telegram.Bot(token=TELEGRAM_TOKEN)
logger = get_logger(__name__)


class IsRequestError(Exception):
    pass


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}

    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
        response_status = homework_statuses.status_code

        if response_status != Http_Status_Code['OK']['code']:
            raise IsRequestError

        return homework_statuses.json()

    except IsRequestError:
        print('Ошибка при работе с API сервиса Практикум.Домашка!')
        for key, item in Http_Status_Code.items():
            if item['code'] == response_status:
                message = (
                    'IsRequestError: Ошибка запроса. '
                    f'status code: { item["code"] }. '
                    f'message: { item["message"] }. '
                )
                logger.error(message)
                send_message(message)

        sys.exit(Exit_Code['ERROR'])


def send_message(message):
    logger.info(f'Сообщение отправлено. Текст сообщения: {message}')
    return bot.send_message(CHAT_ID, message)


def main():
    logger.debug('Старт приложения. Бот запущен!')
    current_timestamp = int(time.time())  # Начальное значение timestamp

    while True:
        try:
            homeworks = get_homeworks(current_timestamp)['homeworks']
            for hw in homeworks:
                message = parse_homework_status(hw)
                send_message(message)

            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            logger.error(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
