import logging
import os
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
START_BOT = 'Старт приложения. Бот запущен!'
MAIN_EXCEPTION = (
    'Приложение остановлено в функции main()'
    ' из-за перехваченого исключения: \n{exception}'
)
TELEGRAM_SEND_MESSAGE = (
    'Собщение отправлено!'
)
TELEGRAM_HOMEWORK_STATUS = (
    'У вас проверили работу '
    '"{homework_name}"!\n\n{verdict}'
)
TELEGRAM_SEND_MESSAGE_EXCEPTION = (
    'Произошла ошибка при отправке сообщения в телеграмм'
    '\nТекст исключения: {exception}'
)
REQUEST_ERROR = (
    'Произошла ошибка "{name}"'
    '\nТекст из перехваченного исключения: {exception}'
    '{params}'
)
REQUEST_PARAMS = (
    '\nПараметры запроса: \nurl: {url}, header: {header}, params: {params}'
)
STATUS_ERROR = (
    'Неизвестный статус домашки.'
    '\nСтатус домашки: {status}'
)
VERDICTS = {
    'reviewing': 'Работа взята в ревью.',
    'approved': 'Ревьюеру всё понравилось, работа зачтена!',
    'rejected': 'К сожалению, в работе нашлись ошибки.'
}
TIMEOUT = 20 * 60
bot = telegram.Bot(token=TELEGRAM_TOKEN)


class IncorrectKeyWarning(Exception):
    pass


def get_homeworks(current_timestamp):
    payload = {'from_date': current_timestamp}
    params_request = REQUEST_PARAMS.format(
        url=URL,
        header=HEADERS,
        params=payload
    )
    try:
        homework_statuses = requests.get(URL, headers=HEADERS, params=payload)
    except requests.RequestException as exception:
        raise ConnectionError(REQUEST_ERROR.format(
            name='Произошла ошибка соединения.',
            exception=exception,
            params=params_request
        ))
    homeworks = homework_statuses.json()
    for key in ('error', 'code'):
        if key in homeworks:
            raise IncorrectKeyWarning(REQUEST_ERROR.format(
                name='API. Практикум.Домашка вернул отказ. ',
                exception=homeworks[key],
                params=params_request
            ))
    return homeworks


def parse_homework_status(homework):
    status = homework['status']
    if status not in VERDICTS:
        raise ValueError(STATUS_ERROR.format(status=status))
    return TELEGRAM_HOMEWORK_STATUS.format(
        homework_name=homework['homework_name'],
        verdict=VERDICTS[status]
    )


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())
    logging.debug(START_BOT)
    while True:
        try:
            homeworks = get_homeworks(current_timestamp)
            current_timestamp = homeworks.get(
                'current_date', current_timestamp
            )
            homeworks = homeworks['homeworks']
            if homeworks:
                send_message(parse_homework_status(homeworks[0]))
                logging.info(TELEGRAM_SEND_MESSAGE)
        except Exception as exception:
            try:
                # send_message(f'{exception}')
                logging.error(
                    MAIN_EXCEPTION.format(exception=exception),
                    exc_info=True
                )
            except Exception as error:
                logging.error(
                    TELEGRAM_SEND_MESSAGE_EXCEPTION.format(
                        exception=error
                    ),
                    exc_info=True
                )
        time.sleep(TIMEOUT)


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PATH_TO_LOG = os.path.join(BASE_DIR, 'main.log')
    _log_format = (
        '%(asctime)s - [%(levelname)s] -  %(name)s - '
        '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
    )

    logging.basicConfig(
        level=logging.DEBUG,
        format=_log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                filename=PATH_TO_LOG, mode='a', encoding='utf8'
            )
        ])

    main()
