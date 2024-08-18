from Prediction.constants import VERIFY_YEARS_COUNT, CITIES_IDS
from .api import Requester
from datetime import datetime
import time
import json
import os

DATA_PATH = os.getcwd() + "/data"


class TerraBrasilis:
    def __init__(self):
        self.__requester = Requester()
        self.__requester.setTimeout(300)
        self.__url = 'https://terrabrasilis.dpi.inpe.br/'
        self.__cookieUrl = 'queimadas/bdqueimadas/'
        self.__urlCsrf = 'queimadas/bdqueimadas/#tabela-de-atributos'
        self.__csrf = ''
        self.__cookie = ''

    def initialize(self):
        if self.__cookie == '':
            content = self.__requester.requestGet(self.__url + self.__cookieUrl)
            if self.__requester.getResponseCode() == 200:
                lines = content.split('\n')
                for line in lines:
                    if '_csrf' in line:
                        self.__csrf = line[line.rfind('_csrf') + 14: -2]
                        # print(line)
                        break
                headers = self.__requester.getHeaders()
                for a in headers.items():
                    if a[0] == 'set-cookie':
                        cookie = headers['set-cookie']
                        self.__cookie = cookie[0: cookie.rfind(';')]
                        # print(cookie)
        if self.__cookie == '':
            raise Exception('Cookie not initialized!')
        if self.__csrf == '':
            raise Exception('_csrf Cookie not initialized!')

    def getCsrf(self):
        return self.__csrf

    def getCookie(self):
        return self.__cookie

    def retrieveCities(self):
        if not os.path.exists(DATA_PATH):
            os.mkdir(DATA_PATH)
        currentYear = datetime.now().year
        for year in range(currentYear - VERIFY_YEARS_COUNT, currentYear):
            print(f'Enter in {year}', end='. ')
            folderYear = f'{DATA_PATH}/{year}'
            if not os.path.exists(folderYear):
                os.mkdir(folderYear)
            for city in CITIES_IDS.items():
                fileCityPath = f'{folderYear}/{city[0]}.json'
                if not os.path.exists(fileCityPath):
                    timeFrom = self.__requester.urlEncode(f'{year}-01-01 00:00:00')
                    timeTo = self.__requester.urlEncode(f'{year}-12-31 23:59:59')

                    header = {
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'X-CSRF-Token': self.__csrf,
                        'Cookie': self.__cookie
                    }
                    print(f'{year} - Requesting data from {city[0]}...', end='')
                    retries = 0
                    responseCode = 0
                    while responseCode != 200:
                        retries += 1
                        if retries == 10:
                            raise Exception(f'Fail request data city {city[0]}')
                        content = self.__requester.requestPost(f'https://terrabrasilis.dpi.inpe.br/queimadas/bdqueimadas/get-attributes-table', header, self.__getData(city[1], timeFrom, timeTo))
                        responseCode = self.__requester.getResponseCode()

                        if responseCode == 200:
                            fileCity = open(fileCityPath, 'w', encoding="utf-8")
                            json.dump(json.loads(content), fileCity, ensure_ascii=False, indent=4)
                            fileCity.close()
                        if responseCode != 200 and retries < 10:
                            time.sleep(1)
                            print(f' Retrying now', end='')
                    print(f' Successful.')
                    time.sleep(1)
            print('Finished.')

    def updateCurrentData(self):
        now = datetime.now()
        timeFrom = self.__requester.urlEncode(f'{now.year}-01-01 00:00:00')
        if now.day < 10:
            day = f'0{now.day}'
        else:
            day = f'{now.day}'
        if now.month < 10:
            month = f'0{now.month}'
        else:
            month = f'{now.month}'
        timeTo = self.__requester.urlEncode(f'{now.year}-{month}-{day} 23:59:59')
        folderYear = f'{DATA_PATH}/{now.year}'
        if not os.path.exists(folderYear):
            os.mkdir(folderYear)
        print(f'Enter in {now.year}')
        for city in CITIES_IDS.items():
            print(f'{now.year} - Requesting data from {city[0]}...', end=' ')
            header = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-CSRF-Token': self.__csrf,
                'Cookie': self.__cookie
            }
            retries = 0
            responseCode = 0
            while responseCode != 200:
                retries += 1
                if retries == 10:
                    raise Exception(f'Fail request data city {city[0]}')
                content = self.__requester.requestPost(f'https://terrabrasilis.dpi.inpe.br/queimadas/bdqueimadas/get-attributes-table', header, self.__getData(city[1], timeFrom, timeTo))
                responseCode = self.__requester.getResponseCode()

                if responseCode == 200:
                    fileCityPath = f'{folderYear}/{city[0]}.json'
                    fileCity = open(fileCityPath, 'w', encoding="utf-8")
                    json.dump(json.loads(content), fileCity, ensure_ascii=False, indent=4)
                    fileCity.close()
                elif retries < 10:
                    time.sleep(1)
            print(f'Successful.')

    def __getData(self, city, timeFrom, timeTo):
        return ('draw=8&columns%5B0%5D%5Bdata%5D=0&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false' +
                '&columns%5B1%5D%5Bdata%5D=1&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false' +
                '&columns%5B2%5D%5Bdata%5D=2&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false' +
                '&columns%5B3%5D%5Bdata%5D=3&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false' +
                '&columns%5B4%5D%5Bdata%5D=4&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false' +
                '&columns%5B5%5D%5Bdata%5D=5&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false' +
                '&columns%5B6%5D%5Bdata%5D=6&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false' +
                '&columns%5B7%5D%5Bdata%5D=7&columns%5B7%5D%5Bname%5D=&columns%5B7%5D%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false' +
                '&columns%5B8%5D%5Bdata%5D=8&columns%5B8%5D%5Bname%5D=&columns%5B8%5D%5Bsearchable%5D=true&columns%5B8%5D%5Borderable%5D=true&columns%5B8%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B8%5D%5Bsearch%5D%5Bregex%5D=false' +
                '&columns%5B9%5D%5Bdata%5D=9&columns%5B9%5D%5Bname%5D=&columns%5B9%5D%5Bsearchable%5D=true&columns%5B9%5D%5Borderable%5D=true&columns%5B9%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B9%5D%5Bsearch%5D%5Bregex%5D=false' +
                '&columns%5B10%5D%5Bdata%5D=10&columns%5B10%5D%5Bname%5D=&columns%5B10%5D%5Bsearchable%5D=true&columns%5B10%5D%5Borderable%5D=true&columns%5B10%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B10%5D%5Bsearch%5D%5Bregex%5D=false' +
                '&columns%5B11%5D%5Bdata%5D=11&columns%5B11%5D%5Bname%5D=&columns%5B11%5D%5Bsearchable%5D=true&columns%5B11%5D%5Borderable%5D=true&columns%5B11%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B11%5D%5Bsearch%5D%5Bregex%5D=false' +
                '&columns%5B12%5D%5Bdata%5D=12&columns%5B12%5D%5Bname%5D=&columns%5B12%5D%5Bsearchable%5D=true&columns%5B12%5D%5Borderable%5D=true&columns%5B12%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B12%5D%5Bsearch%5D%5Bregex%5D=false' +
                '&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=desc&start=0&length=1000&search%5Bvalue%5D=&search%5Bregex%5D=false&dateTimeFrom=' + timeFrom + '&dateTimeTo=' + timeTo + '&satellites=&biomes=' +
                '&continent=8&countries=33&states=03323&cities=' + city + '&specialRegions=&protectedArea=&industrialFires=false')

    def removeDuplicities(self):
        # 1 - remover duplicidades de horarios
        # concluido
        if not os.path.exists('filtered'):
            os.mkdir('filtered')
        for yearFolder in os.listdir("data"):
            print(yearFolder)

            if not os.path.exists(f'filtered/{yearFolder}'):
                os.mkdir(f'filtered/{yearFolder}')

            for fileName in os.listdir(f'data/{yearFolder}'):
                filePath = f'data/{yearFolder}/{fileName}'
                filteredPath = f'filtered/{yearFolder}/{fileName}'
                print(f'{filePath}')

                filtered = open(filePath, 'r', encoding="utf-8")
                jsonObject = json.loads(filtered.read())
                filtered.close()
                jsonArray = jsonObject['data']
                jsonArray2 = []
                for jsonFire in jsonArray:
                    found = False
                    for jsonFire2 in jsonArray2:
                        if jsonFire[0] == jsonFire2[0]:
                            found = True
                            break
                    if not found:
                        jsonArray2.append(jsonFire)
                print(f'Fires {len(jsonArray2)}')
                print(f'Removed items {len(jsonArray) - len(jsonArray2)}')
                filtered = open(filteredPath, 'w', encoding="utf-8")
                json.dump(jsonArray2, filtered, ensure_ascii=False, indent=4)
                filtered.close()
        # 2 - remover dados com coordenadas muito proximas de alguma outra
        # nao necessario por enquanto

    def generateCustomData(self):
        if not os.path.exists('custom'):
            os.mkdir('custom')
        jsonArray = []
        for city in CITIES_IDS.items():
            jsonArray.append(city[0])
        filtered = open('custom/Cities.json', 'w', encoding="utf-8")
        json.dump(jsonArray, filtered, ensure_ascii=False, indent=4)
        filtered.close()
        print("ok")
