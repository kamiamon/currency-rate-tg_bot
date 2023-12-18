import unittest
import tempfile
import shutil
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.utils import is_valid_currency, load_rate_data_from_cache, save_rate_data_to_cache

class TestUtilsFunctions(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def test_is_valid_currency(self):
        currencies_data = {'currencies': {'USD': 'US Dollar', 'EUR': 'Euro'}}

        # Test with a valid currency
        self.assertTrue(is_valid_currency('USD', currencies_data))

        # Test with an invalid currency
        self.assertFalse(is_valid_currency('GBP', currencies_data))

    def test_load_rate_data_from_cache(self):
        # Create a temporary file with sample data
        file_path = os.path.join(self.test_dir, 'test_cache.json')
        sample_data = {'rates': {'USD': 1.0, 'EUR': 0.85}}
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(sample_data))

        # Test loading data from the cache file
        loaded_data = load_rate_data_from_cache(file_path)
        self.assertEqual(loaded_data, sample_data)

        # Test loading from a non-existent file
        non_existent_file_path = os.path.join(self.test_dir, 'non_existent_cache.json')
        loaded_data_non_existent = load_rate_data_from_cache(non_existent_file_path)
        self.assertEqual(loaded_data_non_existent, {})

    def test_save_rate_data_to_cache(self):
        # Create a temporary file path
        file_path = os.path.join(self.test_dir, 'test_cache.json')

        # Sample data to save
        sample_data = {'rates': {'USD': 1.0, 'EUR': 0.85}}

        # Test saving data to the cache file
        save_rate_data_to_cache(sample_data, file_path)

        # Check if the file exists and has the correct content
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, 'r', encoding='utf-8') as file:
            loaded_data = json.load(file)
        self.assertEqual(loaded_data, sample_data)

if __name__ == '__main__':
    unittest.main()
