import unittest
from unittest.mock import patch, MagicMock
import requests
import numpy as np
import pandas as pd
import time
from io import StringIO

from elasticsearch8 import Elasticsearch
from elasticsearch8.helpers import bulk

from lidataexporter import config, index_documents, dataset, main

class Testlidataexporter(unittest.TestCase):

    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data="test_value")
    def test_config(self, mock_open):
        result = config("dummy_key")
        mock_open.assert_called_with('/configs/default/shared-data/dummy_key', 'r')
        self.assertEqual(result, "test_value")

    @patch("elasticsearch8.helpers.bulk")
    def test_index_documents(self, mock_bulk):
        es_client = MagicMock()
        json_data = [{'field1': 'value1'}, {'field2': 'value2'}]
        index_name = "test_index"
        mock_bulk.return_value = (1, [])

        result = index_documents(json_data, index_name, es_client)

        actions = [
            {
                "_index": index_name,
                "_source": doc
            }
            for doc in json_data
        ]
        self.assertEqual(result, "OK")

    @patch("requests.get")
    def test_dataset(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"column1": "value1"}, {"column1": "value2"}]
        mock_get.return_value = mock_response

        expected_df = pd.DataFrame([{"column1": "value1"}, {"column1": "value2"}])

        result = dataset()

        mock_get.assert_called_with("https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/city-of-melbourne-liveability-and-social-indicators/exports/json?lang=en&timezone=Australia%2FSydney")
        pd.testing.assert_frame_equal(result, expected_df)

    @patch("lidataexporter.index_documents")
    @patch("lidataexporter.dataset")
    @patch("elasticsearch8.Elasticsearch")
    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data="test_value")
    @patch("time.time", side_effect=[0, 1]) 
    def test_main(self, mock_time, mock_open, mock_es, mock_dataset, mock_index_documents):
        mock_dataset.return_value = pd.DataFrame([{"column1": "value1"}, {"column1": np.nan}])
        mock_es_client = MagicMock()
        mock_es.return_value = mock_es_client

        result = main()

        mock_open.assert_any_call('/configs/default/shared-data/ES_USERNAME', 'r')
        mock_open.assert_any_call('/configs/default/shared-data/ES_PASSWORD', 'r')
        mock_dataset.assert_called_once()

        self.assertEqual(result, "OK")

if __name__ == '__main__':
    unittest.main()

