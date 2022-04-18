import vk_api
import datetime


def reformat_time(unix):
    value = datetime.datetime.fromtimestamp(unix)
    return value.strftime('date: %Y-%m-%d, time: %H:%M:%S')


def main():
    vk_session = vk_api.VkApi(
        token='d9a4c5b61933675c3049da47a46107ea8f4cca86f50db48479dd83c3da08f3b4e0c9fca7b3d6fa5dc42c3')
    upload = vk_api.VkUpload(vk_session)
    photos = [r'static/img/1.jpg', r'static/img/2.jpg']
    for ph in photos:
        photo = upload.photo(ph, album_id=282596389, group_id=212701807)
        vk_photo_url = 'https://vk.com/photo/{}_{}'.format(
            photo[0]['owner_id'], photo[0]['id'])
        vk_photo_id = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}'
        print(photo, vk_photo_id, vk_photo_url, sep='\n')
        vk = vk_session.get_api()
        vk.wall.post(message="Test", attachments=[vk_photo_id])


if __name__ == '__main__':
    main()

