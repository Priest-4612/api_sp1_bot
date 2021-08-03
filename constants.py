Http_Status_Code = {
    'OK': {'code': 200, 'message': ''},
    'CREATED': {'code': 201, 'message': ''},
    'BAD_REQUEST': {'code': 400, 'message': 'Неверный запрос/Bad Request'},
    'UNAUTHORIZED': {
        'code': 401,
        'message': 'Неавторизованный запрос/Unauthorized'
    },
    'FORBIDDEN': {
        'code': 403,
        'message': 'Доступ к ресурсу запрещен/Forbidden'
    },
    'NOT_FOUND': {
        'code': 404,
        'message': 'Ресурс не найден/Not Found'
    },
    'INTERNAL_SERVER_ERROR': {
        'code': 500,
        'message': 'Внутренняя ошибка сервера/Internal Server Error'
    },
}


Exit_Code = {
    'SUCCESS': 0,
    'ERROR': 1,
}


Homework_Status = {
    'reviewing': 'работа взята в ревью',
    'approved': 'ревью успешно пройдено',
    'rejected': 'в работе есть ошибки, нужно поправить'
}
