"""
Generic web scraper for repositories without APIs.
Uses web scraping to find QDA files.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import time
from .base_scraper import BaseScraper


class WebScraper(BaseScraper):
    """Generic web scraper for finding QDA files on websites."""
    
    def __init__(
        self, 
        base_url: str,
        repository_name: str,
        config_path: str = "config/qda_extensions.json"
    ):
        """
        Initialize web scraper.
        
        Args:
            base_url: Base URL of the repository
            repository_name: Name of the repository
            config_path: Path to QDA extensions config
        """
        super().__init__(config_path)
        self.base_url = base_url.rstrip('/')
        self.repository_name = repository_name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QDA-Archive-Bot/1.0 (Research Data Collection)'
        })
        self.visited_urls = set()
    
    def search(
        self, 
        query: Optional[str] = None, 
        max_results: int = 50,
        max_depth: int = 2,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search website for QDA files.
        
        Args:
            query: Not used for web scraping
            max_results: Maximum number of files to find
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
            
            # Find all links
            for link in soup.find_all('a', href=True):
                if len(self.results) >= max_results:
                    break
                
                href = link['href']
                full_url = urljoin(url, href)
                
                # Check if it's a QDA file
                if self.is_qda_file(href):
                    file_meta = self._build_file_metadata(full_url, link, soup, url)
                    self.results.append(file_meta)
                
                # Recursively crawl if it's a page on the same domain
                elif self._is_same_domain(full_url) and full_url not in self.visited_urls:
                    time.sleep(0.5)  # Rate limiting
                    self._crawl_page(full_url, depth + 1, max_depth, max_results)
            
        except requests.exceptions.RequestException as e:
            print(f"Error crawling {url}: {e}")
    
    def _is_same_domain(self, url: str) -> bool:
        """Check if URL is on the same domain as base_url."""
        base_domain = urlparse(self.base_url).netloc
        url_domain = urlparse(url).netloc
        return base_domain == url_domain
    
    def _build_file_metadata(
        self, 
        file_url: str, 
        link_element: Any,
        page_soup: BeautifulSoup,
        page_url: str
    ) -> Dict[str, Any]:
        """Build metadata for a found file."""
        filename = file_url.split('/')[-1].split('?')[0]
        file_extension = '.' + filename.split('.')[-1] if '.' in filename else ''
        
        # Try to extract title from page
        title = ''
        title_tag = page_soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        
        # Try to extract description from meta tags
        description = ''
        meta_desc = page_soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', '')
        
        # Try to get link text as additional context
        link_text = link_element.get_text().strip()
        
        return self.normalize_metadata({
            'filename': filename,
            'file_extension': file_extension.lower(),
            'download_url': file_url,
            'source_repository': self.repository_name,
            'source_url': page_url,
            'source_id': file_url,
            'license_type': '',  # Cannot determine from web scraping
            'license_url': '',
            'project_title': title or link_text,
            'project_description': description,
            'authors': '',
            'publication_date': '',
            'keywords': '',
            'doi': '',
            'qda_software': self.get_qda_software(filename),
        })
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific file URL."""
        # For web scraper, file_id is the URL
        return {
            'download_url': file_id,
            'source_repository': self.repository_name
        }

