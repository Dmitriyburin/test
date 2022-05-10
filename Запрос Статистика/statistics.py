import vk_api
import datetime
import pprint


def reformat_time(unix):
    value = datetime.datetime.fromtimestamp(unix)
    return value.strftime('date: %Y-%m-%d, time: %H:%M:%S')


def statistics(group_id):
    vk_session = vk_api.VkApi(
        token='8ccf458377e4585db89d02b869073857f9a86f23eb1e5c27203198b40770df0ebdee96996719dd90c12b7')
    vk = vk_session.get_api()
    try:
        stats = vk.stats.get(group_id=group_id, intervals_count=10)
    except Exception:
        return False
    comments, likes, subscribed, unsub = 0, 0, 0, 0
    cities = set()
    ages = {
        '12-18': 0,
        '18-21': 0,
        '21-24': 0,
        '24-27': 0,
        '27-30': 0,
        '30-35': 0,
        '35-45': 0,
        '45-100': 0
    }

    for stat in stats:
        for city in stat['visitors'].get('cities', []):
            cities.add(city['name'])
        activity = stat.get('activity', None)
        visitors = stat.get('visitors', None)
        if activity:
            comments += activity.get('comments', 0)
            likes += activity.get('likes', 0)
            subscribed += activity.get('subscribed', 0)
            unsub += activity.get('unsubscribed', 0)
        print(visitors)
        if visitors:
            for age in visitors.get('age', []):
                ages[age['value']] += age['count']

        pprint.pprint(stat)

    activities = {
        'comments': comments,
        'likes': likes,
        'subscribed': subscribed,
    }
    return activities, ages, cities
