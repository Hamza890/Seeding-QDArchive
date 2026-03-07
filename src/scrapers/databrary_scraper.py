"""
Scraper for Databrary - Video data sharing library.
Note: Databrary requires authentication for most content.
"""
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper


class DatabraryScraper(BaseScraper):
    """Scraper for Databrary."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """
        Initialize Databrary scraper.
        
        Args:
            config_path: Path to QDA extensions config
        """
        super().__init__(config_path)
        self.base_url = "https://databrary.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QDA-Archive-Bot/1.0 (Research Data Collection)',
            'Accept': 'application/json'
        })
    
    def search(
        self, 
        query: Optional[str] = None, 
        max_results: int = 100,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search Databrary for qualitative data.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            **kwargs: Additional parameters
            
        Returns:
            List of metadata dictionaries
        """
        self.clear_results()

        # Search for qualitative-related terms
        if not query:
            search_terms = ["qualitative", "interview", "observation"]
        else:
            search_terms = [query]

        total_fetched = 0

        for search_term in search_terms:
            if total_fetched >= max_results:
                break

            print(f"Searching Databrary for: '{search_term}'...")
            print("Note: Databrary requires authentication for most content.")

            params = {
                'q': search_term,
                'tab': 0  # Volumes tab
            }

            params.update(kwargs)

            try:
                url = f"{self.base_url}/search"
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find volume entries
                volumes = soup.find_all('div', class_='volume') or soup.find_all('article')
                
                if not volumes:
                    print("No public volumes found. Most Databrary content requires authentication.")
                    break

                for volume in volumes:
                    if total_fetched >= max_results:
                        break

                    file_meta = self._extract_volume_metadata(volume)
                    if file_meta:
                        self.results.append(file_meta)
                        total_fetched += 1

                time.sleep(1)  # Rate limiting

            except requests.exceptions.RequestException as e:
                print(f"Error fetching from Databrary ({search_term}): {e}")
                break
        
        return self.results
    
    def _extract_volume_metadata(self, volume_element) -> Optional[Dict[str, Any]]:
        """Extract metadata from a volume element."""
        try:
            title_elem = volume_element.find('h3') or volume_element.find('a', class_='title')
            if not title_elem:
                return None
            
            title_link = title_elem.find('a') if title_elem.name != 'a' else title_elem
            title = title_link.get_text(strip=True) if title_link else title_elem.get_text(strip=True)
            volume_url = title_link.get('href', '') if title_link else ''
            
            if volume_url and not volume_url.startswith('http'):
                volume_url = f"{self.base_url}{volume_url}"
            
            desc_elem = volume_element.find(class_='description') or volume_element.find('p')
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            return self.normalize_metadata({
                'filename': f"{title}.volume",
                'file_extension': '.volume',
                'file_size': None,
                'download_url': volume_url,
                'source_repository': 'Databrary',
                'source_url': volume_url,
                'source_id': '',
                'license_type': 'Restricted - Authentication Required',
                'license_url': '',
                'project_title': title,
                'project_description': description,
                'authors': '',
                'publication_date': '',
                'keywords': '',
                'doi': '',
                'qda_software': '',
                'is_qda_file': False
            })
        except Exception as e:
            print(f"Error extracting volume metadata: {e}")
            return None
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific volume."""
        return {}

