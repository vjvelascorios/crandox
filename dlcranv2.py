import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm
import json
from datetime import datetime, timedelta
import time
import concurrent.futures

class CRANDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = 'https://cran.r-project.org/web/packages'
        self.cache_file = Path('package_cache.json')
        self.dox_dir = Path('dox')
        self.dox_dir.mkdir(exist_ok=True)
        
    def _load_cache(self):
        if self.cache_file.exists():
            cache_data = json.loads(self.cache_file.read_text())
            if datetime.fromisoformat(cache_data['timestamp']) > datetime.now() - timedelta(days=1):
                return cache_data['packages']
        return None

    def _save_cache(self, packages):
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'packages': packages
        }
        self.cache_file.write_text(json.dumps(cache_data))

    def get_package_list(self):
        # Try to load from cache first
        cached_packages = self._load_cache()
        if cached_packages:
            return cached_packages

        # If no cache, fetch from web
        try:
            url = f'{self.base_url}/available_packages_by_name.html'
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            packages = [a.text for a in soup.find_all('a') if a.text]
            
            # Save to cache
            self._save_cache(packages)
            return packages
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching package list: {e}")
            return []

    def get_downloaded_packages(self):
        return {f.stem for f in self.dox_dir.glob('*.pdf')}

    def download_package(self, package):
        # Actualizar la lista de paquetes descargados antes de cada verificación
        downloaded = self.get_downloaded_packages()
        
        if package in downloaded:
            print(f"Skipping {package} - already downloaded")
            return False
        
        pdf_path = self.dox_dir / f'{package}.pdf'
        try:
            url = f'{self.base_url}/{package}/'
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            pdf_link = next((a.get('href') for a in soup.find_all('a') 
                            if a.get('href', '').endswith('.pdf')), None)
            
            if pdf_link:
                pdf_url = url + pdf_link
                response = self.session.get(pdf_url, timeout=30)
                response.raise_for_status()
                
                # Verificar una última vez antes de escribir
                if package not in self.get_downloaded_packages():
                    pdf_path.write_bytes(response.content)
                    print(f"Successfully downloaded {package}")
                    return True
                else:
                    print(f"Package {package} was downloaded by another thread")
                    return False
                    
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {package}: {e}")
            if pdf_path.exists():
                pdf_path.unlink()
        return False

def main():
    downloader = CRANDownloader()
    
    # Get all available packages
    all_packages = downloader.get_package_list()
    print(f'Total packages available: {len(all_packages)}')
    
    # Get already downloaded packages
    downloaded = downloader.get_downloaded_packages()
    print(f'Already downloaded: {len(downloaded)}')
    
    # Filter only packages that need downloading
    packages_to_download = [pkg for pkg in all_packages if pkg not in downloaded]
    print(f'Packages to download: {len(packages_to_download)}')
    
    if not packages_to_download:
        print("All packages are already downloaded!")
        return
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for package in packages_to_download:
            futures.append(executor.submit(downloader.download_package, package))
            
        for future in tqdm(concurrent.futures.as_completed(futures), 
                          total=len(futures),
                          desc="Downloading packages"):
            try:
                future.result()
            except Exception as e:
                print(f"Download failed: {e}")

if __name__ == '__main__':
    main()
