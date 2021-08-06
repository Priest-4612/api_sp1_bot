from unittest import TestCase
from unittest import main as uni_main
from unittest import mock

import requests

import homework

ReqEx = requests.RequestException


class TestReq(TestCase):
    @mock.patch('requests.get')
    def test_raised(self, rq_get):
        rq_get.side_effect = mock.Mock(
            side_effect=ReqEx('testing')
        )
        homework.main()

    @mock.patch('requests.get')
    def test_error(self, rq_get):
        JSON = {'error': 'testing'}
        resp = mock.Mock()
        resp.json = mock.Mock(
            return_value=JSON
        )
        rq_get.return_value = resp
        homework.main()

    @mock.patch('requests.get')
    def test_error_value(self, rq_get):
        JSON = {'homeworks': [{'homework_name': 'test', 'status': 'test'}]}
        resp = mock.Mock()
        resp.json = mock.Mock(
            return_value=JSON
        )
        rq_get.return_value = resp
        homework.main()

    @mock.patch('requests.get')
    def test_error_invalid_json(self, rq_get):
        JSON = {'homeworks': 1}
        resp = mock.Mock()
        resp.json = mock.Mock(
            return_value=JSON
        )
        rq_get.return_value = resp
        homework.main()


if __name__ == '__main__':
    uni_main()
