import unittest
from unittest.mock import patch, mock_open, Mock, MagicMock
import pandas as pd
from bpdataexporter import config, index_documents, dataset, main

class Testbpdataexporter(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='test_data')
    def test_config(self, mock_file):
        result = config('test_key')
        mock_file.assert_called_with('/configs/default/shared-data/test_key', 'r')
        self.assertEqual(result, 'test_data')

    @patch('bpdataexporter.bulk')
    def test_index_documents(self, mock_bulk):
        es_client = MagicMock()
        json_data = [{'field': 'value'}]
        index_name = 'test_index'

        mock_bulk.return_value = (1, [])

        result = index_documents(json_data, index_name, es_client)

        expected_actions = [
            {
                "_index": index_name,
                "_source": {'field': 'value'}
            }
        ]

        mock_bulk.assert_called_once_with(es_client, expected_actions, index=index_name)
        self.assertEqual(result, 'OK')

    @patch('bpdataexporter.requests.get')
    def test_dataset(self, mock_get):
        mock_json_data = [
            {
                "issue_date": "2021-01-01",
                "commence_by_date": "2021-12-31",
                "completed_by_date": "2022-12-31",
                "estimated_cost_of_works": 1000
            },
            {
                "issue_date": "2022-01-01",
                "commence_by_date": "2021-12-31",  # Invalid record
                "completed_by_date": "2022-12-31",
                "estimated_cost_of_works": 1000
            },
            {
                "issue_date": "2021-01-01",
                "commence_by_date": "2021-12-31",
                "completed_by_date": "2022-12-31",
                "estimated_cost_of_works": -1000  # Invalid record
            }
        ]

        mock_response = Mock()
        mock_response.json.return_value = mock_json_data
        mock_get.return_value = mock_response

        result = dataset()

        expected_df = pd.DataFrame([
            {
                "issue_date": "2021-01-01",
                "commence_by_date": "2021-12-31",
                "completed_by_date": "2022-12-31",
                "estimated_cost_of_works": 1000
            }
        ])

        pd.testing.assert_frame_equal(result, expected_df)
        mock_get.assert_called_once_with("https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/building-permits/exports/json?lang=en&timezone=Australia%2FSydney")

    @patch('bpdataexporter.index_documents')
    @patch('bpdataexporter.dataset')
    @patch('bpdataexporter.config')
    @patch('bpdataexporter.Elasticsearch')
    def test_main(self, mock_elasticsearch, mock_config, mock_dataset, mock_index_documents):
        mock_config.side_effect = lambda key: {
            'ES_USERNAME': 'es_user',
            'ES_PASSWORD': 'es_pass'
        }[key]

        mock_dataset.return_value = pd.DataFrame([
            {
                "issue_date": "2021-01-01",
                "commence_by_date": "2021-12-31",
                "completed_by_date": "2022-12-31",
                "estimated_cost_of_works": 1000
            }
        ])

        mock_elasticsearch_instance = MagicMock()
        mock_elasticsearch.return_value = mock_elasticsearch_instance

        result = main()

        self.assertEqual(result, "OK")
        mock_config.assert_any_call('ES_USERNAME')
        mock_config.assert_any_call('ES_PASSWORD')
        mock_dataset.assert_called_once()
        mock_elasticsearch.assert_called_once_with(
            'https://elasticsearch-master.elastic.svc.cluster.local:9200',
            verify_certs=False,
            ssl_show_warn=False,
            basic_auth=('es_user', 'es_pass')
        )
        mock_index_documents.assert_called_once()

if __name__ == '__main__':
    unittest.main()

