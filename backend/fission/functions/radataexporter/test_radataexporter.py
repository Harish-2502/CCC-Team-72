import unittest
from unittest.mock import patch, mock_open, MagicMock
import pandas as pd
import numpy as np
import requests

import io
import time

from radataexporter import config, index_documents, dataset, main

class Testradataexporter(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="test_value")
    def test_config(self, mock_file):
        self.assertEqual(config('test_key'), 'test_value')
        mock_file.assert_called_with('/configs/default/shared-data/test_key', 'r')

    @patch("elasticsearch8.helpers.bulk")
    def test_index_documents(self, mock_bulk):
        mock_bulk.return_value = (1, [])
        es_client = MagicMock()
        json_data = [{"key": "value"}]
        index_name = "test_index"
        
        result = index_documents(json_data, index_name, es_client)
        
        self.assertEqual(result, "OK")

    @patch.object(requests.Session, 'get')
    @patch('pandas.read_csv')
    def test_dataset(self, mock_read_csv, mock_get):
        mock_get.return_value.content = b'column1,column2\nvalue1,value2'
        mock_read_csv.return_value = pd.DataFrame({"column1": ["value1"], "column2": ["value2"]})
        
        with patch('radataexporter.config', return_value='test_user') as mock_config:
            result = dataset()
            
            mock_config.assert_any_call('GITHUB_USERNAME')
            mock_config.assert_any_call('GITHUB_TOKEN')
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)

    @patch("time.time", side_effect=[0, 1])
    @patch("radataexporter.index_documents")
    @patch("radataexporter.dataset")  
    @patch("radataexporter.config") 
    @patch("elasticsearch8.Elasticsearch")
    def test_main(self, mock_elasticsearch, mock_config, mock_dataset, mock_index_documents, mock_time):
        mock_config.side_effect = ['es_user', 'es_pass']
        mock_dataset.return_value = pd.DataFrame({"column1": [np.nan, "value2"]})
        es_client_mock = MagicMock()
        mock_elasticsearch.return_value = es_client_mock
        
        result = main()
        
        mock_config.assert_any_call('ES_USERNAME')
        mock_config.assert_any_call('ES_PASSWORD')
        mock_dataset.assert_called_once()

if __name__ == "__main__":
    unittest.main()

