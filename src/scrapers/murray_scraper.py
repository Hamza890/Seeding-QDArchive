"""
Scraper for Murray Research Archive - Harvard University.
"""
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper


class MurrayScraper(BaseScraper):
    """Scraper for Murray Research Archive."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """
        Initialize Murray Research Archive scraper.
        
        Args:
            config_path: Path to QDA extensions config
        """
        super().__init__(config_path)
        self.base_url = "https://www.murray.harvard.edu"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QDA-Archive-Bot/1.0 (Research Data Collection)',
            'Accept': 'text/html,application/xhtml+xml'
        })
    
    def search(
        self, 
        query: Optional[str] = None, 
        max_results: int = 100,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search Murray Archive for qualitative data.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            **kwargs: Additional parameters
            
        Returns:
            List of metadata dictionaries
        """
        self.clear_results()

        if not query:
            search_terms = ["qualitative", "interview", "longitudinal"]
        else:
            search_terms = [query]

        total_fetched = 0

        for search_term in search_terms:
            if total_fetched >= max_results:
                break

            print(f"Searching Murray Archive for: '{search_term}'...")

            params = {
                'q': search_term,
                'page': 1
            }

            params.update(kwargs)

            while total_fetched < max_results:
                try:
                    # Try search endpoint
                    search_url = f"{self.base_url}/search"
                    response = self.session.get(search_url, params=params, timeout=30)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find dataset/study entries
                    datasets = soup.find_all('div', class_='dataset') or soup.find_all('article', class_='study')
                    
                    if not datasets:
                        # Try alternative selectors
                        datasets = soup.find_all('div', class_='search-result') or soup.find_all('li', class_='result')
                    
                    if not datasets:
                        print("No datasets found or page structure changed.")
                        break

                    for dataset in datasets:
                        if total_fetched >= max_results:
                            break

                        file_meta = self._extract_dataset_metadata(dataset)
                        if file_meta:
                            self.results.append(file_meta)
                            total_fetched += 1

                    # Check for next page
                    params['page'] += 1
                    time.sleep(1)  # Rate limiting

                    if len(datasets) == 0:
                        break

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching from Murray Archive ({search_term}): {e}")
                    break
        
        return self.results
    
    def _extract_dataset_metadata(self, dataset_element) -> Optional[Dict[str, Any]]:
        """Extract metadata from a dataset element."""
        try:
            # Find title
            title_elem = dataset_element.find('h3') or dataset_element.find('h2') or dataset_element.find('a', class_='title')
            if not title_elem:
                return None
            
            title_link = title_elem.find('a') if title_elem.name != 'a' else title_elem
            title = title_link.get_text(strip=True) if title_link else title_elem.get_text(strip=True)
            dataset_url = title_link.get('href', '') if title_link else ''
            
            if dataset_url and not dataset_url.startswith('http'):
                dataset_url = f"{self.base_url}{dataset_url}"
            
            # Find description
            desc_elem = dataset_element.find('p', class_='description') or dataset_element.find('p')
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # Find authors
            author_elem = dataset_element.find(class_='author') or dataset_element.find(class_='creator')
            authors = author_elem.get_text(strip=True) if author_elem else ''
            
            return self.normalize_metadata({
                'filename': f"{title}.dataset",
                'file_extension': '.dataset',
                'file_size': None,
                'download_url': dataset_url,
                'source_repository': 'Murray Research Archive',
                'source_url': dataset_url,
                'source_id': '',
                'license_type': '',
                'license_url': '',
                'project_title': title,
                'project_description': description,
                'authors': authors,
                'publication_date': '',
                'keywords': '',
                'doi': '',
                'qda_software': '',
                'is_qda_file': False
            })
        except Exception as e:
            print(f"Error extracting dataset metadata: {e}")
            return None
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific dataset."""
        return {}

