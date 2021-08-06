import logging
from logging.handlers import RotatingFileHandler
import os
import time

import requests
from requests.models import requote_uri
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}

P_TELEGRAM = (
    'У вас проверили работу '
    '"{homework_name}"!\n\n{verdict}'
)

P_REQUEST_ERROR = (
    'Произошла ошибка "{name}"'
    '\nТекст из перехваченного исключения: {exception}'
    '{params}'
)

P_PARAMS = (
    '\nПараметры запроса: \nurl: {url}, header: {header}, params: {params}'
)

P_STATUS_ERROR = (
    'Неизвестный статус домашки.'
    '\nСтатус домашки: {status}'
)

VERDICTS = {
    'reviewing': 'Работа взята в ревью.',
    'approved': 'Ревьюеру всё понравилось, работа зачтена!',
    'rejected': 'К сожалению, в работе нашлись ошибки.'
}

REQUEST_ATTRIBUTE_ERROR = [
    'error',
    'code',
]

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def get_homeworks(current_timestamp):
    payload = {'from_date': current_timestamp}
    params_request = P_PARAMS.format(
            url=URL,
            header=HEADERS,
            params=payload
    )

    try:
        homework_statuses = requests.get(URL, headers=HEADERS, params=payload)
    except requests.ConnectionError as exception:
        raise ConnectionError(P_REQUEST_ERROR.format(
            name='Произошла ошибка подключения.',
            exception=exception,
            params=params_request
        ))
    except requests.HTTPError as exception:
        raise ConnectionError(P_REQUEST_ERROR.format(
            name='Произошла ошибка подключения.',
            exception=exception,
            params=params_request
        ))
    except requests.Timeout as exception:
        raise ConnectionError(P_REQUEST_ERROR.format(
            name='Время ожидания истекло.',
            exception=exception,
            params=params_request
        ))

    homeworks_json = homework_statuses.json()

    for key in homeworks_json.keys():
        if key in REQUEST_ATTRIBUTE_ERROR:
            raise AttributeError(P_REQUEST_ERROR.format(
            name='API. Практикум.Домашка вернул ошибку. ',
            exception=homeworks_json['code'],
            params=params_request
        ))

    return homeworks_json


def parse_homework_status(homework):
    status = homework['status']
    if status not in VERDICTS:
        raise AttributeError(P_STATUS_ERROR.format(status=status))

    verdict = VERDICTS[status]
    return P_TELEGRAM.format(homework_name=homework['homework_name'], verdict=verdict)

def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    timeout = 20 * 60
    current_timestamp = int(time.time())
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PATH_TO_LOG = os.path.join(BASE_DIR, 'logs', 'main.log')
    _log_format = (
        '%(asctime)s - [%(levelname)s] -  %(name)s - '
        '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
    )

    file_handler = logging.FileHandler(
        filename=PATH_TO_LOG, mode='a', encoding='utf8'
    )
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(logging.Formatter(_log_format))

    logging.basicConfig(
        level=logging.DEBUG,
        format=_log_format,
        handlers=[logging.StreamHandler(), file_handler])

    logging.debug('Старт приложения. Бот запущен!')

    while True:
        try:
            homeworks_json = get_homeworks(current_timestamp)
            current_timestamp = homeworks_json.get('current_date', current_timestamp)
            homeworks = homeworks_json['homeworks']
            if homeworks:
                message_status = send_message(parse_homework_status(homeworks[0]))
                logging.info(
                    f'Собщение отправлено пользователю: {message_status["chat"]["username"]}'
                    f'\nТекст сообщения: {message_status["text"]}'
                )
                time.sleep(timeout)

        except Exception as exception:
            logging.error(exception, exc_info=True)
            time.sleep(timeout)


if __name__ == '__main__':
    main()
