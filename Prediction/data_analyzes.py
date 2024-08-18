import json
import os
import time
from datetime import datetime

from Prediction.constants import VERIFY_YEARS_COUNT
from .city import CityModel
import numpy as np
from sklearn.linear_model import LinearRegression

class DataAnalyzes:
    def __init__(self):
        self.totalChapadaAraripe = 0        # Total de focos da chapada do araripe nos ultimos VERIFY_YEARS_COUNT anos
        self.occurredCurrentYear = 0        # Total do ano atual
        self.predictCurrentYear = 0         # Media anual final
        self.predictChapadaAraripe = []     # Previsao de queimadas em cada mes, para a chapada do araripe
        self.occurredChapadaAraripe = []    # Total de focos ocorridos no ano atual, por mes
        self.annualTotalOccurred = {}       # Total de focos ocorridos por ano
        self.cityModels = {}                # Dicionario de cidades
        self.dataChapadaAraripe = {}        # dados dos totais sobre os meses do ano atual}
        self.dataCities = []                # dados a serem enviados pro back-end referentes as cidades (lista de dados de cidaddes)

    def analyze(self):
        self.occurredChapadaAraripe.clear()
        for i in range(0, 12): self.occurredChapadaAraripe.append(0)

        if not os.path.exists('release'):
            os.mkdir('release')

        self.occurredCurrentYear = 0
        currentYear = datetime.now().year
        for year in range(currentYear - VERIFY_YEARS_COUNT, currentYear + 1):
            if year < currentYear:
                self.annualTotalOccurred[year] = 0
            for fileName in os.listdir(f'filtered/{year}'): # fileName Eg:= Salitre.json
                filePath = f'filtered/{year}/{fileName}'

                filtered = open(filePath, 'r', encoding="utf-8")
                array = json.loads(filtered.read())#['data']
                filtered.close()

                cityName = fileName[0:fileName.rfind('.')]
                cityModel = CityModel(cityName)
                if cityName in self.cityModels:
                    cityModel = self.cityModels[cityName]
                self.cityModels[cityName] = cityModel

                for arrayFire in array:
                    date = arrayFire[0].split('T')[0]
                    segments = date.split('-')
                    cityModel.putFiresData(segments[1], segments[0])
                    if currentYear == int(segments[0]):
                        self.occurredCurrentYear += 1
                    else:
                        self.totalChapadaAraripe += 1


        for cityName in self.cityModels:
            cityModel = self.cityModels[cityName]
            cityModel.calculateMonthlyAverage()
            print(cityModel.name)

            for y in self.annualTotalOccurred:
                if y < currentYear:
                    self.annualTotalOccurred[y] += self.cityModels[cityName].totalPerYears[str(y)]

            for i in range(12):
                base = []
                for items in cityModel.years.items():
                    months = items[1]  # 0 = 2022, 1 = [23, 45, 45,...]
                    base.append(months[i])
                cityModel.monthlyPredict.append(max(self.predictNextNumber(base), 0))
            cityModel.calculateTotals(currentYear)

            count = 0
            for items in cityModel.years.items():
                months = items[1] # 0 = 2022, 1 = [23, 45, 45,...]
                totalPerYears = cityModel.totalPerYears[items[0]]
                if currentYear != int(items[0]):
                    count += totalPerYears
                else:
                    for i in range(0, 12):
                        self.occurredChapadaAraripe[i] += months[i]
                print(f'{items[0]} -> {months} total: {totalPerYears}')
            print(f'Media -> {cityModel.monthlyAverage}')
            print(f'Media anual da cidade sem contar o atual ano -> {count / VERIFY_YEARS_COUNT}')
            print()

        timestamp = round(time.time() * 1000)
        dateTime = datetime.now().strftime("%Y-%m-%d %H:%M")
        for item in self.cityModels.items():
            print(f'Previsao: {item[1].monthlyPredict} {item[0]}')
            jsonMonths = []
            for index in range(0, 12):
                jsonMonths.append({"fireOccurrences": item[1].years[str(currentYear)][index], "firesPredicted": item[1].monthlyPredict[index]})
            jsonObject = {"timestamp": timestamp, "date_time": dateTime, 'city': item[0], 'prediction_total': item[1].predictedCurrentYear, 'occurred_total': item[1].totalOccurrencesCurrentYear, 'months': jsonMonths}
            self.dataCities.append(jsonObject)
            file = open(f'release/{item[0]}.json', 'w', encoding="utf-8")
            json.dump(jsonObject, file, ensure_ascii=False, indent=4)
            file.close()

        years = {}
        for year in range(currentYear - VERIFY_YEARS_COUNT, currentYear + 1):
            if year == currentYear:
                break
            years[year] = []
            for month in range(0, 12):
                years[year].append(0)
            for cityName in self.cityModels:
                for month in range(0, 12):
                    years[year][month] += self.cityModels[cityName].years[str(year)][month]
        base = []
        for month in range(0, 12):
            base.clear()
            for year in years:
                base.append(years[year][month])
            self.predictChapadaAraripe.append(self.predictNextNumber(base))

        print(f'________________________________________________________________________________________')
        print(f'|\tAno\t\t|\tTotal\t|\tMeses')
        base.clear()
        count = 0
        for y in self.annualTotalOccurred:
            count += self.annualTotalOccurred[y]
            if y != str(currentYear):
                base.append(self.annualTotalOccurred[y])
            print(f'|\t{y}\t|\t{self.annualTotalOccurred[y]}\t|\t{years[y]}')

        self.predictCurrentYear = self.predictNextNumber(base)

        print(f'|\t{currentYear}\t|\t{self.occurredCurrentYear}\t\t|\t', end='')
        print('[', end='')
        jsonMonths = []
        for i in range(0, 12):
            jsonMonth = {}
            #jsonMonth['number'] = i + 1
            jsonMonth['fireOccurrences'] = self.occurredChapadaAraripe[i]
            jsonMonth['firesPredicted'] = self.predictChapadaAraripe[i]
            jsonMonths.append(jsonMonth)
            print(self.occurredChapadaAraripe[i], end='')
            if i < 11: print(', ', end='')
        print(']')
        print(f'_________________________________________________________________________________________')
        print()


        self.dataChapadaAraripe = {"timestamp": timestamp, "date_time": dateTime, 'city': "Chapada do Araripe", 'prediction_total':  self.predictCurrentYear, 'occurred_total': self.occurredCurrentYear, 'months': jsonMonths}
        if not os.path.exists('release'):
            os.mkdir('release')
        file = open('release/Chapada do Araripe.json', 'w', encoding="utf-8")
        json.dump(self.dataChapadaAraripe, file, ensure_ascii=False, indent=4)
        file.close()

        #print(f'Total ocorrido nos ultimos {VERIFY_YEARS_COUNT} anos -> {self.totalChapadaAraripe}')
        print('----------------- PREVISTOS ------------------')
        print(f'PREVISTO MENSAL PARA ESSE ANO -> {self.predictChapadaAraripe}')
        print(f'PREVISTO TOTAL PARA ESSE ANO -> {self.predictCurrentYear}')

    def predictNextNumber(self, sequence):
        sequence = np.array(sequence)
        X = np.arange(len(sequence)).reshape(-1, 1)
        y = sequence

        model = LinearRegression()
        model.fit(X, y)

        next_index = len(sequence)
        next_value = model.predict([[next_index]])
        return int(next_value[0])