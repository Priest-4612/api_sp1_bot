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


PHRASE_START_BOT = 'Старт приложения. Бот запущен!'
PHRASE_MAIN_EXCEPTION = (
    'Приложение остановлено в функции main()'
    ' из-за перехваченого исключения: \n{exception}'
)
PHRASE_TELEGRAM_SEND_MESSAGE = (
    'Собщение отправлено пользователю: {username}'
    '\nТекст сообщения: {message}'
)
PHRASE_TELEGRAM_HOMEWORK_STATUS = (
    'У вас проверили работу '
    '"{homework_name}"!\n\n{verdict}'
)
PHRASE_TELEGRAM_SEND_MESSAGE_EXCEPTION = (
    'Произошла ошибка при отправке сообщения в телеграмм'
    '\nТекст исключения: {exception}'
)
PHRASE_REQUEST_ERROR = (
    'Произошла ошибка "{name}"'
    '\nТекст из перехваченного исключения: {exception}'
    '{params}'
)
PHRASE_REQUEST_PARAMS = (
    '\nПараметры запроса: \nurl: {url}, header: {header}, params: {params}'
)
PHRASE_STATUS_ERROR = (
    'Неизвестный статус домашки.'
    '\nСтатус домашки: {status}'
)
PHRASE_JSON_ERROR = (
    'Сервер вернул некорректный json'
)
VERDICTS = {
    'reviewing': 'Работа взята в ревью.',
    'approved': 'Ревьюеру всё понравилось, работа зачтена!',
    'rejected': 'К сожалению, в работе нашлись ошибки.'
}

TIMEOUT = 20 * 60

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def get_homeworks(current_timestamp):
    payload = {'from_date': current_timestamp}

    params_request = PHRASE_REQUEST_PARAMS.format(
        url=URL,
        header=HEADERS,
        params=payload
    )

    try:
        homework_statuses = requests.get(URL, headers=HEADERS, params=payload)
    except requests.RequestException as exception:
        raise ConnectionError(PHRASE_REQUEST_ERROR.format(
            name='Произошла ошибка соединения.',
            exception=exception,
            params=params_request
        ))

    homeworks_json = homework_statuses.json()
    if type(homeworks_json['homeworks']) != list:
        raise TypeError(PHRASE_JSON_ERROR)

    for key in ('error', 'code'):
        if key in homeworks_json:
            raise ValueError(PHRASE_REQUEST_ERROR.format(
                name='API. Практикум.Домашка вернул отказ. ',
                exception=homeworks_json[key],
                params=params_request
            ))

    return homeworks_json


def parse_homework_status(homework):
    status = homework['status']
    if status not in VERDICTS:
        raise ValueError(PHRASE_STATUS_ERROR.format(status=status))
    return PHRASE_TELEGRAM_HOMEWORK_STATUS.format(
        homework_name=homework['homework_name'],
        verdict=VERDICTS[status]
    )


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def delayed(timeout):
    time.sleep(timeout)


def main():
    current_timestamp = int(time.time())

    logging.debug(PHRASE_START_BOT)

    while True:
        try:
            homeworks_json = get_homeworks(current_timestamp)
            current_timestamp = homeworks_json.get(
                'current_date', current_timestamp
            )
            homeworks = homeworks_json['homeworks']
            if homeworks:
                message_status = send_message(
                    parse_homework_status(homeworks[0])
                )
                logging.info(
                    PHRASE_TELEGRAM_SEND_MESSAGE.format(
                        username=message_status['chat']['username'],
                        message=message_status['text']
                    )
                )

            delayed(TIMEOUT)

        except Exception as exception:
            try:
                send_message(f'{exception}')
            except Exception as error:
                logging.error(
                    PHRASE_TELEGRAM_SEND_MESSAGE_EXCEPTION.format(
                        exception=error
                    ),
                    exc_info=True
                )
            logging.error(PHRASE_MAIN_EXCEPTION.format(exception=exception))

            delayed(TIMEOUT)


if __name__ == '__main__':
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

    main()
