import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import requests
from bs4 import BeautifulSoup

class TestDlcran(unittest.TestCase):

    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    def test_create_folder(self, mock_exists, mock_makedirs):
        # Test if the folder is created when it does not exist
        if not os.path.exists('CRAN'):
            os.makedirs('CRAN')
        mock_exists.assert_called_once_with('CRAN')
        mock_makedirs.assert_called_once_with('CRAN')

    @patch('requests.get')
    def test_get_packages(self, mock_get):
        # Mock the response from the CRAN packages page
        mock_response = MagicMock()
        mock_response.text = '<html><body><a href="pkg1">pkg1</a><a href="pkg2">pkg2</a></body></html>'
        mock_get.return_value = mock_response

        url = 'https://cran.r-project.org/web/packages/available_packages_by_name.html'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        packages = [a.text for a in soup.find_all('a')]

        self.assertEqual(packages, ['pkg1', 'pkg2'])
        mock_get.assert_called_once_with(url)

    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_documentation(self, mock_open, mock_get):
        # Mock the response from the package page
        mock_response_pkg = MagicMock()
        mock_response_pkg.text = '<html><body><a href="doc.pdf">doc.pdf</a></body></html>'
        mock_get.side_effect = [mock_response_pkg, mock_response_pkg]

        packages = ['pkg1', 'pkg2']
        for package in packages:
            url = 'https://cran.r-project.org/web/packages/{}/'.format(package)
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            for a in soup.find_all('a'):
                if a.get('href').endswith('.pdf'):
                    r = requests.get(url + a.get('href'))
                    with open('CRAN/{}.pdf'.format(package), 'wb') as f:
                        f.write(r.content)
                    break

        self.assertEqual(mock_get.call_count, 4)  # 2 package pages + 2 PDF downloads
        self.assertEqual(mock_open.call_count, 2)  # 2 PDF files opened for writing

if __name__ == '__main__':
    unittest.main()