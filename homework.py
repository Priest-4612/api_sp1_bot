import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}

MESSAGE_STATUS = (
    'У вас проверили работу '
    '"{homework_name}"!\n\n{verdict}'
)
VERDICTS = {
    'reviewing': 'Работа взята в ревью.',
    'approved': 'Ревьюеру всё понравилось, работа зачтена!',
    'rejected': 'К сожалению, в работе нашлись ошибки.'
}

bot = telegram.Bot(token=TELEGRAM_TOKEN)

base_dir = os.path.dirname(os.path.abspath(__file__))
_log_folder = os.path.join(base_dir, 'logs')
_log_format = (
    '%(asctime)s - [%(levelname)s] -  %(name)s - '
    '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
)

logging.basicConfig(
    level=logging.DEBUG,
    format=_log_format
)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(
    f'{_log_folder}/{__name__}', mode='a', encoding='utf8'
)
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(logging.Formatter(_log_format))
stream_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    verdict = VERDICTS[homework['status']]
    return MESSAGE_STATUS.format(homework_name=homework_name, verdict=verdict)


class RequestsError(Exception):
    pass


def get_homeworks(current_timestamp):
    payload = {'from_date': current_timestamp}

    try:
        homework_statuses = requests.get(URL, headers=HEADERS, params=payload)
        homeworks_json = homework_statuses.json()
        keys = homeworks_json.keys()
        if 'error' in keys or 'code' in keys:
            raise RequestsError({'message': f'code: {homeworks_json["code"]}'})
        return homeworks_json
    except RequestsError:
        message = (
            f'Ошибка запроса!'
            f'\nPraktikum API error: {homeworks_json} '
            f'\nrequest: url: {URL}, params: {payload}'
        )
        logger.error(message)
        send_message(message)
        sys.exit(1)


def send_message(message):
    bot.send_message(CHAT_ID, message)
    logger.info(
        f'Сообщение отправлено. Текст в сообщении: {message}'
    )
    return


def main():
    logger.debug('Старт приложения. Бот запущен!')
    current_timestamp = int(time.time())

    while True:
        try:
            homeworks_json = get_homeworks(current_timestamp)
            current_timestamp = homeworks_json['current_date']
            homework = homeworks_json['homeworks']
            if len(homework) != 0:
                message = parse_homework_status(homework[0])
                send_message(message)

            time.sleep(20 * 60)

        except Exception as error:
            message = f'Произошла ошибка: {error}'
            logger.error(message, exc_info=True)
            send_message(message)
            time.sleep(20 * 60)


if __name__ == '__main__':
    main()
