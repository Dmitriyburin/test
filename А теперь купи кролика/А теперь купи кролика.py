# импортируем библиотеки
from flask import Flask, request
import logging

# библиотека, которая нам понадобится для работы с JSON
import json

app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

sessionStorage = {}
status = False


@app.route('/', methods=['POST'])
@app.route('/post', methods=['POST'])
def main():
    global status
    logging.info(f'Request: {request.json!r}')

    print(request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    if status:
        handle_rabbit_dialog(request.json, response)
    else:
        response1 = handle_dialog(request.json, response)
        if response1:
            status = True

    logging.info(f'Response:  {response!r}')
    print(status)
    return json.dumps(response)


def handle_rabbit_dialog(req, res):
    user_id = req['session']['user_id']

    if True in [word in req['request']['original_utterance'].lower() for word in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо'
    ]]:
        res['response']['text'] = 'Кролика можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        return

    res['response']['text'] =\
        f"Все говорят '{req['request']['original_utterance']}', а ты купи кролика!"
    res['response']['buttons'] = get_suggests(user_id, st='кролик')


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        # Заполняем текст ответа
        res['response']['text'] = 'Привет! Купи слона!'
        # Получим подсказки
        res['response']['buttons'] = get_suggests(user_id)
        return

    if True in [word in req['request']['original_utterance'].lower() for word in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо'
    ]]:
        res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        # Заполняем текст ответа
        res['response']['text'] += '\n\nНо лучше купи кролика!'
        # Получим подсказки
        res['response']['buttons'] = get_suggests(user_id, st='кролик')
        return 'Новый круг'

    res['response']['text'] =\
        f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id, st='слон'):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={st}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()
