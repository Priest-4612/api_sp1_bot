import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# проинициализируйте бота здесь,
# чтобы он был доступен в каждом нижеобъявленном методе,
# и не нужно было прокидывать его в каждый вызов
bot = ...


def parse_homework_status(homework):
    homework_name = ...
    if ...
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': int(current_timestamp)}

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
                print(
                    'IsRequestError: Ошибка запроса. '
                    f'status code: { item["code"] }. '
                    f'message: { item["message"] }. '
                )
        sys.exit(Exit_Code['ERROR'])

    except Exception as error:
        print(error)


def send_message(message):
    return bot.send_message(...)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp

    while True:
        try:
            ...
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
