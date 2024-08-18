from Prediction.constants import VERIFY_YEARS_COUNT
from datetime import datetime

class CityModel:

    def __init__(self, name):
        self.name = name            # Nome da cidade
        self.years = {}             # Meses dos anos Ex: {2022: [12, 3, 4, 5, ...], 2023: [43, 5, 6..], ...}
        self.totalPerYears = {}     # Total focos nos meses dos anos Ex: {2014: 3000, 2015: 1000, ...}
        self.monthlyAverage = []    # Media de de cada mes Ex: [12, 3, 6, ...]
        self.monthlyPredict = []
        self.predictedCurrentYear = 0
        self.totalOccurrencesCurrentYear = 0
        self.percentage = 0
        for y in range(datetime.now().year - VERIFY_YEARS_COUNT, datetime.now().year + 1):
            months = []
            self.totalPerYears[str(y)] = 0
            for m in range(0, 12):
                months.append(0)
            self.years[str(y)] = months

    def putFiresData(self, month, year):
        self.years[year][int(month) - 1] += 1
        self.totalPerYears[year] += 1

    def calculateMonthlyAverage(self):
        for i in range(0, 12): self.monthlyAverage.append(0)
        for year in self.years:
            month = self.years[year]
            if year != str(datetime.now().year):
                for i in range(0, 12):
                    self.monthlyAverage[i] += month[i]
        for i in range(0, 12):
            self.monthlyAverage[i] /= VERIFY_YEARS_COUNT

    def  calculateTotals(self, currentYear):
        for index in range(0, 12):
            self.predictedCurrentYear += self.monthlyPredict[index]
            self.totalOccurrencesCurrentYear += self.years[str(currentYear)][index]