"""
Scraper for UK Data Service.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import time
from .base_scraper import BaseScraper


class UKDataServiceScraper(BaseScraper):
    """Scraper for UK Data Service - web scraping based."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """Initialize UK Data Service scraper."""
        super().__init__(config_path)
        self.base_url = "https://ukdataservice.ac.uk"
        self.search_base = "https://beta.ukdataservice.ac.uk/datacatalogue/studies"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QDA-Archive-Bot/1.0 (Research Data Collection)'
        })
        self.visited_urls = set()
    
    def search(
        self, 
        query: Optional[str] = None, 
        max_results: int = 50,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search UK Data Service for QDA files.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            **kwargs: Additional parameters
            
        Returns:
            List of metadata dictionaries
        """
        self.clear_results()
        self.visited_urls.clear()
        
        # Search for qualitative data
        search_query = query or "qualitative"
        
        try:
            # Search the data catalogue
            params = {
                'Search': search_query,
                'Rows': 100
            }
            
            response = self.session.get(self.search_base, params=params, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find study links
            study_links = soup.find_all('a', href=True)
            
            for link in study_links:
                if len(self.results) >= max_results:
                    break
                
                href = link['href']
                
                # Look for study detail pages
                if '/study/' in href or '/dataset/' in href:
                    full_url = urljoin(self.base_url, href)
                    
                    if full_url not in self.visited_urls:
                        self.visited_urls.add(full_url)
                        
                        # Check study page for QDA files
                        study_files = self._check_study_page(full_url)
                        self.results.extend(study_files)
                        
                        time.sleep(1)  # Rate limiting
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching UK Data Service: {e}")
        
        return self.results[:max_results]
    
    def _check_study_page(self, url: str) -> List[Dict[str, Any]]:
        """Check a study page for QDA files."""
        qda_files = []
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract study metadata
            title = ''
            title_elem = soup.find('h1')
            if title_elem:
                title = title_elem.get_text().strip()
            
            description = ''
            desc_elem = soup.find('meta', attrs={'name': 'description'})
            if desc_elem:
                description = desc_elem.get('content', '')
            
            # Look for download links
            for link in soup.find_all('a', href=True):
                href = link['href']
                link_text = link.get_text().strip()
                
                # Check if it's a QDA file
                if self.is_qda_file(href) or self.is_qda_file(link_text):
                    filename = href.split('/')[-1].split('?')[0]
                    if not filename or '.' not in filename:
                        filename = link_text
                    
                    file_extension = '.' + filename.split('.')[-1] if '.' in filename else ''
                    download_url = urljoin(url, href)
                    
                    file_meta = self.normalize_metadata({
                        'filename': filename,
                        'file_extension': file_extension.lower(),
                        'download_url': download_url,
                        'source_repository': 'UK Data Service',
                        'source_url': url,
                        'source_id': url.split('/')[-1],
                        'license_type': 'UK Data Service End User Licence',
                        'license_url': 'https://ukdataservice.ac.uk/help/access-policy/',
                        'project_title': title,
                        'project_description': description,
                        'authors': '',
                        'publication_date': '',
                        'keywords': 'qualitative',
                        'doi': '',
                        'qda_software': self.get_qda_software(filename),
                        'is_qda_file': True,  # UKDS scraper only finds QDA files
                    })

                    qda_files.append(file_meta)
            
        except requests.exceptions.RequestException as e:
            print(f"Error checking study page {url}: {e}")
        
        return qda_files
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific study."""
        # For UK Data Service, file_id is the study URL
        files = self._check_study_page(file_id)
        return files[0] if files else {}

