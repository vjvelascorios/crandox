# download entire CRAN website and save it to a folder
"""
This script downloads the entire documentation from the CRAN website and saves it to a folder named 'CRAN'.
Usage:
    python dlcran.py
Modules:
    os: Provides a way of using operating system dependent functionality.
    requests: Allows you to send HTTP requests.
    bs4 (BeautifulSoup): Library for parsing HTML and XML documents.
    concurrent.futures: Provides a high-level interface for asynchronously executing callables.
Functions:
    download_package(package): Downloads the PDF documentation for a given package.
Workflow:
    1. Checks if a folder named 'CRAN' exists, and creates it if it does not.
    2. Fetches the list of available packages from the CRAN website.
    3. Uses ThreadPoolExecutor to download the PDF documentation for each package in parallel.
    4. Saves the downloaded PDF files into the 'CRAN' folder.
Note:
    Ensure you have the required libraries installed:
    - requests
    - beautifulsoup4
    - futures (if using Python 2)
"""
# Usage: python dlcran.py

import os
import requests
from bs4 import BeautifulSoup
import concurrent.futures

# create a folder to save the documentation
if not os.path.exists('dox'):
    os.makedirs('dox')

# get the list of packages
url = 'https://cran.r-project.org/web/packages/available_packages_by_name.html'
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')
packages = [a.text for a in soup.find_all('a')]
print('Total packages:', len(packages))

# Create a set of already downloaded packages
downloaded_packages = {f[:-4] for f in os.listdir('dox') if f.endswith('.pdf')}

def download_package(package):
    if package in downloaded_packages:
        print(f'{package}.pdf already exists, skipping download.')
        return
    
    print('Processing:', package)
    pdf_path = f'dox/{package}.pdf'
    
    url = f'https://cran.r-project.org/web/packages/{package}/'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    for a in soup.find_all('a'):
        if a.get('href').endswith('.pdf'):
            pdf_url = url + a.get('href')
            r = requests.get(pdf_url)
            with open(pdf_path, 'wb') as f:
                f.write(r.content)
            print(f'Downloaded {package}.pdf')
            break

# Use ThreadPoolExecutor to download packages in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(download_package, packages)

print('Done')
