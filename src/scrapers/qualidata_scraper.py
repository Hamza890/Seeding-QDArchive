"""
Scraper for Qualidata Network repositories (Qualidata, Qualiservice, QualiBi).
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
import time
from .base_scraper import BaseScraper


class QualidataScraper(BaseScraper):
    """Scraper for Qualidata Network - web scraping based."""
    
    def __init__(
        self, 
        repository_name: str = "Qualidata Network",
        base_url: str = "https://www.qualidatanet.com/en/",
        config_path: str = "config/qda_extensions.json"
    ):
        """
        Initialize Qualidata scraper.
        
        Args:
            repository_name: Name of the specific repository
            base_url: Base URL of the repository
            config_path: Path to QDA extensions config
        """
        super().__init__(config_path)
        self.repository_name = repository_name
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QDA-Archive-Bot/1.0 (Research Data Collection)'
        })
        self.visited_urls = set()
    
    def search(
        self, 
        query: Optional[str] = None, 
        max_results: int = 50,
        max_depth: int = 3,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search Qualidata Network for QDA files.
        
        Args:
            query: Search query (not used for web scraping)
            max_results: Maximum number of results
            max_depth: Maximum crawl depth
            **kwargs: Additional parameters
            
        Returns:
            List of metadata dictionaries
        """
        self.clear_results()
        self.visited_urls.clear()
        
        # Start crawling from base URL
        self._crawl_page(self.base_url, depth=0, max_depth=max_depth, max_results=max_results)
        
        return self.results
    
    def _crawl_page(self, url: str, depth: int, max_depth: int, max_results: int):
        """
        Recursively crawl pages looking for QDA files.
        
        Args:
            url: URL to crawl
            depth: Current depth
            max_depth: Maximum depth to crawl
            max_results: Maximum results to collect
        """
        if depth > max_depth or len(self.results) >= max_results:
            return
        
        if url in self.visited_urls:
            return
        
        self.visited_urls.add(url)
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract page metadata
            title = ''
            title_elem = soup.find('h1') or soup.find('title')
            if title_elem:
                title = title_elem.get_text().strip()
            
            description = ''
            desc_elem = soup.find('meta', attrs={'name': 'description'})
            if desc_elem:
                description = desc_elem.get('content', '')
            
            # Find all links
            for link in soup.find_all('a', href=True):
                if len(self.results) >= max_results:
                    break
                
                href = link['href']
                full_url = urljoin(url, href)
                link_text = link.get_text().strip()
                
                # Check if it's a QDA file
                if self.is_qda_file(href) or self.is_qda_file(link_text):
                    file_meta = self._build_file_metadata(
                        full_url, link_text, title, description, url
                    )
                    self.results.append(file_meta)
                
                # Recursively crawl if it's a page on the same domain
                elif self._is_same_domain(full_url) and full_url not in self.visited_urls:
                    # Look for data/archive/study pages
                    if any(keyword in full_url.lower() for keyword in 
                           ['data', 'archive', 'study', 'dataset', 'project']):
                        time.sleep(0.5)  # Rate limiting
                        self._crawl_page(full_url, depth + 1, max_depth, max_results)
            
        except requests.exceptions.RequestException as e:
            print(f"Error crawling {url}: {e}")
    
    def _is_same_domain(self, url: str) -> bool:
        """Check if URL is on the same domain as base_url."""
        from urllib.parse import urlparse
        base_domain = urlparse(self.base_url).netloc
        url_domain = urlparse(url).netloc
        return base_domain == url_domain
    
    def _build_file_metadata(
        self, 
        file_url: str, 
        link_text: str,
        page_title: str,
        page_description: str,
        page_url: str
    ) -> Dict[str, Any]:
        """Build metadata for a found file."""
        filename = file_url.split('/')[-1].split('?')[0]
        if not filename or '.' not in filename:
            filename = link_text if link_text else 'unknown.dat'
        
        file_extension = '.' + filename.split('.')[-1] if '.' in filename else ''
        
        return self.normalize_metadata({
            'filename': filename,
            'file_extension': file_extension.lower(),
            'download_url': file_url,
            'source_repository': self.repository_name,
            'source_url': page_url,
            'source_id': file_url,
            'license_type': '',  # Cannot determine from web scraping
            'license_url': '',
            'project_title': page_title or link_text,
            'project_description': page_description,
            'authors': '',
            'publication_date': '',
            'keywords': 'qualitative',
            'doi': '',
            'qda_software': self.get_qda_software(filename),
            'is_qda_file': True,  # Qualidata scraper only finds QDA files
        })
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific file URL."""
        return {
            'download_url': file_id,
            'source_repository': self.repository_name
        }


class QualiserviceScraper(QualidataScraper):
    """Scraper for Qualiservice."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        super().__init__(
            repository_name="Qualiservice",
            base_url="https://www.qualiservice.org/en/",
            config_path=config_path
        )


class QualiBiScraper(QualidataScraper):
    """Scraper for QualiBi."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        super().__init__(
            repository_name="QualiBi",
            base_url="https://www.qualibi.de/",
            config_path=config_path
        )

