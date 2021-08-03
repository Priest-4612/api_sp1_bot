import datetime as dt
import os
import sys
import time

import requests
from dotenv import load_dotenv

from constants import Http_Status_Code, Exit_Code

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')


class IsRequestError(Exception):
    pass


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


if __name__ == '__main__':
    current_timestamp = dt.datetime(2021, 6, 1).timestamp()
    homeworks = get_homeworks(current_timestamp)

    for hw in homeworks['homeworks']:
        print(hw)
