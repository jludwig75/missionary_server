#!/usr/bin/env python3

import http.client
import json


class Weather:
    def __init__(self, key, location, latitude, longitude):
        self._key = key
        self._location = location
        self._webserver = 'api.openweathermap.org'
        self._coords = ((latitude, longitude))

    def current_conditions(self):
        conn = http.client.HTTPSConnection(self._webserver)
        # conn.request('GET', '/data/2.5/weather?q=%s&appid=%s&units=imperial' % (self._location, self._key))
        uri = '/data/2.5/weather?lat=%.2f&lon=%.2f&appid=%s&units=imperial' % (self._coords[0], self._coords[1], self._key)
        print(uri)
        conn.request('GET', uri)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))

    def forecast(self):
        conn = http.client.HTTPSConnection(self._webserver)
        # conn.request('GET', '/data/2.5/forecast?q=%s&appid=%s&units=imperial' % (self._location, self._key))
        conn.request('GET', '/data/2.5/forecast?lat=%.2f&lon=%.2f&appid=%s&units=imperial' % (self._coords[0], self._coords[1], self._key))
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))

if __name__ == '__main__':
    with open('settings.json') as f:
        settings = json.loads(f.read())
    weather = Weather(settings['open_weather_map_key'], settings['location'], float(settings['latitude']), float(settings['longitude']))
    cc = weather.current_conditions()
    print(json.dumps(cc))
    print(cc['main']['temp'])
    print(cc['main']['humidity'])
    print(cc['weather'][0]['description'])
    # print(weather.forecast())