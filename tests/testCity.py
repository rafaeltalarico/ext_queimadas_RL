import unittest
from datetime import datetime
from Prediction.city import CityModel
from Prediction.constants import VERIFY_YEARS_COUNT

class TestCityModel(unittest.TestCase):

    def setUp(self):
        self.city = CityModel(name="Araripe")

    def test_initialization(self):
        self.assertEqual(self.city.name, "Araripe")
        current_year = datetime.now().year
        for y in range(current_year - VERIFY_YEARS_COUNT, current_year + 1):
            self.assertIn(str(y), self.city.years)
            self.assertEqual(self.city.totalPerYears[str(y)], 0)
            self.assertEqual(len(self.city.years[str(y)]), 12)
            self.assertTrue(all(month == 0 for month in self.city.years[str(y)]))

    def test_putFiresData(self):
        self.city.putFiresData(month=5, year=str(datetime.now().year))
        current_year = str(datetime.now().year)
        self.assertEqual(self.city.years[current_year][4], 1)
        self.assertEqual(self.city.totalPerYears[current_year], 1)

    def test_calculateMonthlyAverage(self):
        self.city.putFiresData(month=1, year=str(datetime.now().year - 1))
        self.city.calculateMonthlyAverage()
        self.assertGreater(self.city.monthlyAverage[0], 0)

    def test_calculateTotals(self):
        current_year = datetime.now().year
        self.city.monthlyPredict = [1] * 12
        self.city.putFiresData(month=1, year=str(current_year))
        self.city.calculateTotals(current_year)
        self.assertEqual(self.city.predictedCurrentYear, 12)
        self.assertEqual(self.city.totalOccurrencesCurrentYear, 1)

if __name__ == '__main__':
    unittest.main()
