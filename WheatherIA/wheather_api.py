import json
import os
import time

from WeatherIA.api import Requester
from WeatherIA.constants import CITIES_COORDINATES, MAX_HISTORIC


class WeatherApi:

    def __init__(self):
        self.__url = f'https://api.weatherapi.com/'
        self.__requester = Requester()

    def update(self):
        arrayToSendWeather = []
        arrayToSendProbabillity = []
        for city in CITIES_COORDINATES.items():
            # weather feature
            print(f'Requesting data for: {city[0]}', end=' ')
            url = f'{self.__url}v1/current.json?key=a8856d705d3b4b17b25151225240605&q={city[1]}&aqi=yes'
            data = self.downloadData(url)
            if data is None:
                # raise Exception(f'Fail request data city {city[0]}')
                print(f'Error while trying request weather data from {city[0]}')
                continue
            else:
                weather = self.retrieveWeatherContent(data, city)
                arrayToSendWeather.append(weather)
            time.sleep(1)
            # Probability feature
            url = f'{self.__url}v1/forecast.json?key=a8856d705d3b4b17b25151225240605&q={city[1]}&aqi=yes'
            forecast = self.downloadData(url)
            if data is None:
                # raise Exception(f'Fail request data city {city[0]}')
                print(f'Error while trying request weather data from {city[0]}')
            else:
                arrayToSendProbabillity.append(self.retrieveForecastContent(weather, forecast, city))
            time.sleep(1)
            print()
        if not os.path.exists('release'):
            os.mkdir('release')
        file = open('release/WeatherData.json', 'w', encoding="utf-8")
        json.dump(arrayToSendWeather, file, ensure_ascii=False, indent=4)
        file.close()
        file = open('release/ProbabilityData.json', 'w', encoding="utf-8")
        json.dump(arrayToSendProbabillity, file, ensure_ascii=False, indent=4)
        file.close()

    def removeRest(self, jsonArray):
        while len(jsonArray) > MAX_HISTORIC:
            jsonArray.pop(0)

    def downloadData(self, url):
        retries = 0
        responseCode = 0
        while responseCode != 200:
            retries += 1
            if retries == 10:
                return None
            content = self.__requester.requestGet(url)
            responseCode = self.__requester.getResponseCode()
            if responseCode == 200:
                return content
            elif retries < 10:
                time.sleep(1)

    def calculateProbability(self, temperature, humidity, daysWithoutRain, uvIndex):
        valueTemperature = max(temperature - 30, 1)     # consider using only high temperatures over 30 degrees
        valueHumidity = 100 - humidity                  # inversely proportional
        weightTemperatureHumidity = ((valueTemperature * valueHumidity) / 1000) * uvIndex
        return min(int((weightTemperatureHumidity**3) * max(1, daysWithoutRain)), 100)

    def retrieveForecastContent(self, weather, forecast, city):
        if not os.path.exists('forecast'):
            os.mkdir('forecast')
        listForecastHours = json.loads(forecast)['forecast']['forecastday'][0]['hour']
        jsonCity = {'probabilities': []}
        for hourData in listForecastHours:
            data = {
                'timestamp': hourData['time_epoch'], 'date_time': hourData['time'], 'temperature': hourData['temp_c'],
                'humidity': hourData['humidity'], 'uv_index': hourData['uv']
            }
            data['probability'] = self.calculateProbability(data['temperature'], data['humidity'], weather['days_without_rain'], hourData['uv'])
            jsonCity['probabilities'].append(data)
            jsonCity['city'] = weather['city']

        filePath = f'forecast/{city[0]}.json'
        file = open(filePath, 'w', encoding="utf-8")
        json.dump(jsonCity, file, ensure_ascii=False, indent=4)
        file.close()
        return jsonCity

    def retrieveWeatherContent(self, weather, city):
        jsonWeather = json.loads(weather)
        print(f'from {jsonWeather['location']['region']}. Successful.', end=' ')

        if not os.path.exists('weather'):
            os.mkdir('weather')

        filePath = f'weather/{city[0]}.json'
        current = jsonWeather['current']
        jsonCity = {}
        if os.path.exists(filePath):
            file = open(filePath, 'r', encoding="utf-8")
            jsonCity = json.loads(file.read())
            file.close()

        if current['precip_mm'] >= 1:
            daysWithoutRain = 0
            hadPrecipitation = True
        else:
            if len(jsonCity) > 0:
                daysWithoutRain = jsonCity['days_without_rain']
                hadPrecipitation = jsonCity['had_precipitation']
            else:
                daysWithoutRain = 0
                hadPrecipitation = False

        jsonItem = {
            'city': city[0], 'timestamp': current['last_updated_epoch'], 'date_time': current['last_updated'], 'temperature': current['temp_c'], 'humidity': current['humidity'],
            'precipitation': current['precip_mm'], 'cloud': current['cloud'], 'carbon_monoxide': current['air_quality']['co'], 'days_without_rain': daysWithoutRain
        }

        if 'data' not in jsonCity:
            jsonCity['data'] = []
        jsonArray = jsonCity['data']
        jsonArray.append(jsonItem)
        self.removeRest(jsonArray)
        jsonCity['city'] = city[0]
        jsonCity['days_without_rain'] = daysWithoutRain
        jsonCity['had_precipitation'] = hadPrecipitation
        file = open(filePath, 'w', encoding="utf-8")
        json.dump(jsonCity, file, ensure_ascii=False, indent=4)
        file.close()

        return jsonItem

    def verifyDaysWithoutRain(self):
        for city in CITIES_COORDINATES.items():
            filePath = f'weather/{city[0]}.json'
            jsonCity = {}
            if os.path.exists(filePath):
                file = open(filePath, 'r', encoding="utf-8")
                jsonCity = json.loads(file.read())
                file.close()

            if not jsonCity['had_precipitation']:
                jsonCity['days_without_rain'] += 1
            file = open(filePath, 'w', encoding="utf-8")
            json.dump(jsonCity, file, ensure_ascii=False, indent=4)
            file.close()
        time.sleep(1)
