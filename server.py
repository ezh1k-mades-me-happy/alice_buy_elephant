from flask import Flask, request
import logging
import json
import requests
from math import sin, cos, sqrt, atan2, radians


def get_geo_info(city, type_info='country'):
    if type_info == 'country':
        return get_country(city)
    return get_coordinates(city)


def get_coordinates(city):
    url = "https://geocode-maps.yandex.ru/1.x/"

    params = {
        'geocode': city,
        'format': 'json',
        'apikey': "40d1649f-0493-4b70-98ba-98533de7710b"
    }

    response = requests.get(url, params)
    json = response.json()
    point_str = json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    point_array = [float(x) for x in point_str.split(' ')]

    return point_array


def get_country(city):
    url = "https://geocode-maps.yandex.ru/1.x/"

    params = {
        'geocode': city,
        'format': 'json',
        'apikey': "40d1649f-0493-4b70-98ba-98533de7710b"
    }

    response = requests.get(url, params)
    json = response.json()

    return \
        json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
            'GeocoderMetaData'][
            'AddressDetails']['Country']['CountryName']


def get_distance(p1, p2):
    R = 6373.0

    lon1 = radians(p1[0])
    lat1 = radians(p1[1])
    lon2 = radians(p2[0])
    lat2 = radians(p2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance


app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')

@app.route('/post', methods=['POST'])
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

    logging.info('Request: %r', response)

    return json.dumps(response)


def handle_dialog(res, req):

    user_id = req['session']['user_id']

    if req['session']['new']:

        res['response']['text'] = 'РџСЂРёРІРµС‚! РЇ РјРѕРіСѓ СЃРєР°Р·Р°С‚СЊ РІ РєР°РєРѕР№ СЃС‚СЂР°РЅРµ РіРѕСЂРѕРґ РёР»Рё СЃРєР°Р·Р°С‚СЊ СЂР°СЃСЃС‚РѕСЏРЅРёРµ РјРµР¶РґСѓ РіРѕСЂРѕРґР°РјРё!'

        return

    cities = get_cities(req)

    if len(cities) == 0:

        res['response']['text'] = 'РўС‹ РЅРµ РЅР°РїРёСЃР°Р» РЅР°Р·РІР°РЅРёРµ РЅРµ РѕРґРЅРѕРіРѕ РіРѕСЂРѕРґР°!'

    elif len(cities) == 1:

        res['response']['text'] = 'РС‚РѕС‚ РіРѕСЂРѕРґ РІ СЃС‚СЂР°РЅРµ - ' + get_country(cities[0])

    elif len(cities) == 2:

        distance = get_distance((get_geo_info(cities[0]), 'coordinates'), (get_geo_info(cities[1]), 'coordinates'))
        res['response']['text'] = 'Р Р°СЃСЃС‚РѕСЏРЅРёРµ РјРµР¶РґСѓ СЌС‚РёРјРё РіРѕСЂРѕРґР°РјРё: ' + str(round(distance)) + ' РєРј.'

    else:

        res['response']['text'] = 'РЎР»РёС€РєРѕРј РјРЅРѕРіРѕ РіРѕСЂРѕРґРѕРІ!'


def get_cities(req):

    cities = []

    for entity in req['request']['nlu']['entities']:

        if entity['type'] == 'YANDEX.GEO':

            if 'city' in entity['value'].keys():
                cities.append(entity['value']['city'])

    return cities


if __name__ == '__main__':
    app.run()
