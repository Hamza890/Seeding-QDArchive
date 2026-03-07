"""
Scraper for Columbia Oral History Archives.
"""
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper


class ColumbiaOralHistoryScraper(BaseScraper):
    """Scraper for Columbia University Oral History Archives."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """
        Initialize Columbia Oral History scraper.
        
        Args:
            config_path: Path to QDA extensions config
        """
        super().__init__(config_path)
        self.base_url = "https://library.columbia.edu/libraries/ccoh"
        self.guide_url = "https://guides.library.columbia.edu/oral_history/digital_collections"
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
        Search Columbia Oral History for qualitative data.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            **kwargs: Additional parameters
            
        Returns:
            List of metadata dictionaries
        """
        self.clear_results()

        if not query:
            search_terms = ["interview", "oral history", "transcript"]
        else:
            search_terms = [query]

        total_fetched = 0

        for search_term in search_terms:
            if total_fetched >= max_results:
                break

            print(f"Searching Columbia Oral History for: '{search_term}'...")

            params = {
                'q': search_term,
                'page': 1
            }

            params.update(kwargs)

            while total_fetched < max_results:
                try:
                    # Try the digital collections guide page
                    response = self.session.get(self.guide_url, params=params, timeout=30)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find collection entries
                    collections = soup.find_all('div', class_='collection') or soup.find_all('article')
                    
                    if not collections:
                        # Try alternative selectors
                        collections = soup.find_all('div', class_='s-lg-box') or soup.find_all('li', class_='collection-item')
                    
                    if not collections:
                        print("No collections found or page structure changed.")
                        break

                    for collection in collections:
                        if total_fetched >= max_results:
                            break

                        file_meta = self._extract_collection_metadata(collection)
                        if file_meta:
                            self.results.append(file_meta)
                            total_fetched += 1

                    # Check for next page
                    params['page'] += 1
                    time.sleep(1)  # Rate limiting

                    if len(collections) == 0:
                        break

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching from Columbia Oral History ({search_term}): {e}")
                    break
        
        return self.results
    
    def _extract_collection_metadata(self, collection_element) -> Optional[Dict[str, Any]]:
        """Extract metadata from a collection element."""
        try:
            # Find title
            title_elem = collection_element.find('h3') or collection_element.find('h2') or collection_element.find('a')
            if not title_elem:
                return None
            
            title_link = title_elem.find('a') if title_elem.name != 'a' else title_elem
            title = title_link.get_text(strip=True) if title_link else title_elem.get_text(strip=True)
            collection_url = title_link.get('href', '') if title_link else ''
            
            if collection_url and not collection_url.startswith('http'):
                collection_url = f"https://library.columbia.edu{collection_url}"
            
            # Find description
            desc_elem = collection_element.find('p', class_='description') or collection_element.find('p')
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            return self.normalize_metadata({
                'filename': f"{title}.collection",
                'file_extension': '.collection',
                'file_size': None,
                'download_url': collection_url,
                'source_repository': 'Columbia Oral History Archives',
                'source_url': collection_url,
                'source_id': '',
                'license_type': '',
                'license_url': '',
                'project_title': title,
                'project_description': description,
                'authors': '',
                'publication_date': '',
                'keywords': 'oral history, interview, transcript',
                'doi': '',
                'qda_software': '',
                'is_qda_file': False
            })
        except Exception as e:
            print(f"Error extracting collection metadata: {e}")
            return None
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific collection."""
        return {}

