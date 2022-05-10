import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

import random
from functions.mapapi_PG import return_map


def main():
    vk_session = vk_api.VkApi(
        token='5ceb9639403ce9f3bc32244c1c95d360a45191a1432ea697d12e754a344da043619a90e03f77659c6b353')

    longpoll = VkBotLongPoll(vk_session, 213168703)
    sessionStorage = {}
    for event in longpoll.listen():
        print(event)
        if event.type == VkBotEventType.MESSAGE_NEW:
            print(event)
            print('Новое сообщение:')
            print('Для меня от:', event.obj.message['from_id'])
            print('Текст:', event.obj.message['text'])
            user_id = event.obj.message['from_id']
            text = event.obj.message['text']
            message = 'Введите название местности, которую хочешь увидеть'
            vk = vk_session.get_api()

            if type(sessionStorage.get(user_id, None)) == str:
                message = f'Это {sessionStorage[user_id]}. Что вы еще хотите увидеть?'
                l_t = 'map'
                if text == 'Спутник':
                    l_t = 'sat'
                vk_photo_id = img_load(sessionStorage[user_id], l=l_t)
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=message,
                                 random_id=random.randint(0, 2 ** 64),
                                 attachment=vk_photo_id[0])
                # img_delete(vk_photo_id[1], vk_photo_id[2])
                sessionStorage[user_id] = True

            elif sessionStorage.get(user_id, None):
                message = 'Выберите тип карты'
                sessionStorage[user_id] = text

                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('Спутник', color=VkKeyboardColor.SECONDARY)
                keyboard.add_button('Схема', color=VkKeyboardColor.POSITIVE)
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=message,
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=keyboard.get_keyboard())
            else:
                sessionStorage[user_id] = True
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=message,
                                 random_id=random.randint(0, 2 ** 64),
                                 )
            # img = return_map(text, l='')


def img_load(text, l='map'):
    vk_session = vk_api.VkApi(
        token='8ccf458377e4585db89d02b869073857f9a86f23eb1e5c27203198b40770df0ebdee96996719dd90c12b7')
    img = return_map(text, l=l)
    upload = vk_api.VkUpload(vk_session)
    photo = upload.photo(img, album_id=286560259, group_id=213168703)
    vk_photo_id = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}'
    return vk_photo_id, photo[0]["owner_id"], photo[0]["id"]


def img_delete(owner_id, photo_id):
    vk_session = vk_api.VkApi(
        token='8ccf458377e4585db89d02b869073857f9a86f23eb1e5c27203198b40770df0ebdee96996719dd90c12b7')
    vk = vk_session.get_api()
    vk.photos.delete(owner_id=owner_id, photo_id=photo_id)


if __name__ == '__main__':
    main()
