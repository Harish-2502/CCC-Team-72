import unittest
from unittest.mock import patch, mock_open, Mock, MagicMock
import io
import pandas as pd
import sudodataexporter

class Testsudodataexporter(unittest.TestCase):
    
    @patch('builtins.open', new_callable=mock_open, read_data='test_data')
    def test_config(self, mock_file):
        result = sudodataexporter.config('test_key')
        mock_file.assert_called_with('/configs/default/shared-data/test_key', 'r')
        self.assertEqual(result, 'test_data')

    @patch('sudodataexporter.bulk')
    def test_index_documents(self, mock_bulk):
        es_client = MagicMock()
        json_data = [{'field': 'value'}]
        index_name = 'test_index'
        
        mock_bulk.return_value = (1, [])
        
        result = sudodataexporter.index_documents(json_data, index_name, es_client)
        
        expected_actions = [
            {
                "_index": index_name,
                "_source": {'field': 'value'}
            }
        ]
        
        mock_bulk.assert_called_once_with(es_client, expected_actions, index=index_name)
        self.assertEqual(result, 'OK')

    @patch('sudodataexporter.requests.Session.get')
    @patch('sudodataexporter.config')
    def test_dataset(self, mock_config, mock_get):
        mock_config.side_effect = lambda key: 'test_user' if key == 'GITHUB_USERNAME' else 'test_token'
        
        mock_csv_content = """
 lga_code_2021, lga_name_2021, state_code_2021, state_name_2021, area_km2, erp_2001, erp_2002, erp_2003, erp_2004, erp_2005, erp_2006, erp_2007, erp_2008, erp_2009, erp_2010, erp_2011, erp_2012, erp_2013, erp_2014, erp_2015, erp_2016, erp_2017, erp_2018, erp_2019, erp_2020, erp_2021
1, Test LGA, 1, Test State, 100.0, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100
"""
        mock_response = Mock()
        mock_response.content = mock_csv_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        result = sudodataexporter.dataset()
        
        expected_df = pd.read_csv(io.StringIO(mock_csv_content))
        pd.testing.assert_frame_equal(result, expected_df)
        
        mock_config.assert_any_call('GITHUB_USERNAME')
        mock_config.assert_any_call('GITHUB_TOKEN')
        mock_get.assert_called_once()

    @patch('sudodataexporter.index_documents')
    @patch('sudodataexporter.dataset')
    @patch('sudodataexporter.config')
    @patch('sudodataexporter.Elasticsearch')
    def test_main(self, mock_elasticsearch, mock_config, mock_dataset, mock_index_documents):
        mock_config.side_effect = lambda key: {
            'GITHUB_USERNAME': 'test_user',
            'GITHUB_TOKEN': 'test_token',
            'ES_USERNAME': 'es_user',
            'ES_PASSWORD': 'es_pass'
        }[key]
        
        mock_dataset.return_value = pd.DataFrame({
            ' lga_code_2021': [1],
            ' lga_name_2021': ['Test LGA'],
            ' state_code_2021': [1],
            ' state_name_2021': ['Test State'],
            ' area_km2': [100.0],
            ' erp_2001': [1000],
            ' erp_2002': [1100],
            ' erp_2003': [1200],
            ' erp_2004': [1300],
            ' erp_2005': [1400],
            ' erp_2006': [1500],
            ' erp_2007': [1600],
            ' erp_2008': [1700],
            ' erp_2009': [1800],
            ' erp_2010': [1900],
            ' erp_2011': [2000],
            ' erp_2012': [2100],
            ' erp_2013': [2200],
            ' erp_2014': [2300],
            ' erp_2015': [2400],
            ' erp_2016': [2500],
            ' erp_2017': [2600],
            ' erp_2018': [2700],
            ' erp_2019': [2800],
            ' erp_2020': [2900],
            ' erp_2021': [3000],
        })
        
        mock_elasticsearch_instance = MagicMock()
        mock_elasticsearch.return_value = mock_elasticsearch_instance
        
        result = sudodataexporter.main()
        
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

