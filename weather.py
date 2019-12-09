#!/usr/bin/env python3

import http.client
import json


class Weather:
    def __init__(self, key, location):
        self._key = key
        self._location = location
        self._webserver = 'api.openweathermap.org'

    def current_conditions(self):
        conn = http.client.HTTPSConnection(self._webserver)
        conn.request('GET', '/data/2.5/weather?q=%s&appid=%s&units=imperial' % (self._location, self._key))
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))

    def forecast(self):
        conn = http.client.HTTPSConnection(self._webserver)
        conn.request('GET', '/data/2.5/forecast?q=%s&appid=%s&units=imperial' % (self._location, self._key))
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))

if __name__ == '__main__':
    weather = Weather('1f2b4a6cc54d6c4fffc9515b17208d4b', 'Cebu%20City,ph')
    cc = weather.current_conditions()
    print(json.dumps(cc))
    print(cc['main']['temp'])
    print(cc['main']['humidity'])
    # print(weather.forecast())