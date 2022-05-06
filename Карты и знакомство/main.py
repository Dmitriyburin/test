from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

cities = {
    'москва': ['1540737/daa6e420d33102bf6947', '213044/7df73ae4cc715175059e'],
    'нью-йорк': ['1652229/728d5c86707054d4745f', '1030494/aca7ed7acefde2606bdc'],
    'париж': ["1652229/f77136c2364eb90a3ea8", '123494/aca7ed7acefd12e606bdc']
}

country_to_city = {
    'москва': 'россия',
    'нью-йорк': 'сша',
    'париж': 'франция'
}

sessionStorage = {}


@app.route('/', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    res['response']['buttons'] = [
        {
            'title': 'Помощь',
            'hide': True
        },
    ]
    if 'помощь' in req['request']['nlu']['tokens']:
        res['response']['text'] = 'Это игра "УГАДАЙ ГОРОД", все просто: алиса предлагает угадать город '\
                                  'по фотографии, ваша задача назвать город, изображенный на картинке, у вас '\
                                  'будет две попытки на угадывание города.'
        return
    if req['session']['new']:
        res['response'][
            'text'] = 'Привет! Это навык Яндекс Алисы - отгадай город по фото. Для более подробной информации '\
                      'введи "Помощь"'\
                      '\n\nНазови свое имя, чтобы продолжить.'
        sessionStorage[user_id] = {
            'first_name': None,
            'game_started': False,
            'game_started_2': False
        }

        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name

            sessionStorage[user_id]['guessed_cities'] = []
            sessionStorage[user_id]['is_country'] = False

            res['response'][
                'text'] = f'Приятно познакомиться, {first_name.title()}. Я Алиса. Отгадаешь город по фото?'
            res['response']['buttons'] += [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                },

            ]
    else:

        if not sessionStorage[user_id]['game_started'] and not sessionStorage[user_id]['game_started_2']:
            if 'да' in req['request']['nlu']['tokens']:
                if len(sessionStorage[user_id]['guessed_cities']) == 3:
                    res['response']['text'] = f'Ты отгадал все города, {sessionStorage[user_id]["first_name"].capitalize()}!'
                    res['end_session'] = True
                else:
                    sessionStorage[user_id]['game_started'] = True
                    sessionStorage[user_id]['attempt'] = 1
                    play_game(res, req)
            elif 'нет' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Ну и ладно!'
                res['end_session'] = True

            else:
                res['response']['text'] = f'Не поняла ответа, {sessionStorage[user_id]["first_name"].capitalize()}! Так да или нет?'
                res['response']['buttons'] += [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    },

                ]
        elif sessionStorage[user_id]['game_started_2']:
            play_game_2(res, req)
        else:
            play_game(res, req)


def play_game_2(res, req):
    user_id = req['session']['user_id']
    country: str = country_to_city[sessionStorage[user_id]['city']]

    if country == get_country(req):
        res['response']['text'] = f'Правильно, {sessionStorage[user_id]["first_name"].capitalize()}, Сыграем еще?'
    else:
        res['response'][
            'text'] = f'Неправильно, {sessionStorage[user_id]["first_name"].capitalize()}, это {country.capitalize()}, Сыграем еще?'
    sessionStorage[user_id]['game_started_2'] = False


def play_game(res, req):
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    if attempt == 1:
        city = random.choice(list(cities))
        while city in sessionStorage[user_id]['guessed_cities']:
            city = random.choice(list(cities))
        sessionStorage[user_id]['city'] = city
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = f'Что это за город, {sessionStorage[user_id]["first_name"].capitalize()}?'
        res['response']['card']['image_id'] = cities[city][attempt - 1]
        res['response']['text'] = 'Тогда сыграем!'
    else:
        city = sessionStorage[user_id]['city']
        if get_city(req) == city:
            res['response'][
                'text'] = f'Правильно, {sessionStorage[user_id]["first_name"].capitalize()}! А в какой стране этот город?'
            sessionStorage[user_id]['guessed_cities'].append(city)
            sessionStorage[user_id]['game_started'] = False
            sessionStorage[user_id]['game_started_2'] = True

            return
        else:
            if attempt == 3:
                res['response'][
                    'text'] = f'{sessionStorage[user_id]["first_name"].capitalize()}, вы пытались. Это {city.title()}. Сыграем ещё?'
                sessionStorage[user_id]['game_started'] = False
                sessionStorage[user_id]['guessed_cities'].append(city)
                return
            else:
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card'][
                    'title'] = f'Неправильно, {sessionStorage[user_id]["first_name"].capitalize()}. Вот тебе дополнительное фото'
                res['response']['card']['image_id'] = cities[city][attempt - 1]
                res['response']['text'] = 'А вот и не угадал!'
    sessionStorage[user_id]['attempt'] += 1


def get_city(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('city', None)


def get_country(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('country', None)


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
