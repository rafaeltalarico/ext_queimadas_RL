import unittest
from unittest.mock import patch, MagicMock
from Prediction.app import main

class TestApp(unittest.TestCase):
    
    @patch('Prediction.app.Sender')
    @patch('Prediction.app.DataAnalyzes')
    @patch('Prediction.app.TerraBrasilis')
    def test_main(self, MockTerraBrasilis, MockDataAnalyzes, MockSender):
        mock_tb_api = MockTerraBrasilis.return_value
        mock_data_analyzes = MockDataAnalyzes.return_value
        mock_sender = MockSender.return_value
        
        mock_tb_api.retrieveCities.return_value = None
        mock_tb_api.updateCurrentData.return_value = None
        mock_tb_api.removeDuplicities.return_value = None
        
        mock_data_analyzes.analyze.return_value = None
        mock_data_analyzes.dataChapadaAraripe = 'dataChapadaAraripe'
        mock_data_analyzes.dataCities = 'dataCities'
        
        mock_sender.sendData.return_value = None

        main()

        mock_tb_api.initialize.assert_called_once()
        mock_tb_api.retrieveCities.assert_called_once()
        mock_tb_api.updateCurrentData.assert_called_once()
        mock_tb_api.removeDuplicities.assert_called_once()
        
        mock_data_analyzes.analyze.assert_called_once()
        
        mock_sender.sendData.assert_called_once()

if __name__ == '__main__':
    unittest.main()
