"""
Scraper for IHSN (International Household Survey Network).
"""
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper


class IHSNScraper(BaseScraper):
    """Scraper for International Household Survey Network (IHSN)."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """
        Initialize IHSN scraper.
        
        Args:
            config_path: Path to QDA extensions config
        """
        super().__init__(config_path)
        self.base_url = "https://ihsn.org"
        self.catalog_url = "https://catalog.ihsn.org"
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
        Search IHSN for qualitative data.
        
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
            search_terms = ["qualitative", "interview", "survey"]
        else:
            search_terms = [query]

        total_fetched = 0

        for search_term in search_terms:
            if total_fetched >= max_results:
                break

            print(f"Searching IHSN for: '{search_term}'...")

            params = {
                'sk': search_term,
                'page': 1
            }

            params.update(kwargs)

            while total_fetched < max_results:
                try:
                    response = self.session.get(f"{self.catalog_url}/index.php/catalog", params=params, timeout=30)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find study entries
                    studies = soup.find_all('div', class_='study') or soup.find_all('div', class_='catalog-item')
                    
                    if not studies:
                        break

                    for study in studies:
                        if total_fetched >= max_results:
                            break

                        file_meta = self._extract_study_metadata(study)
                        if file_meta:
                            self.results.append(file_meta)
                            total_fetched += 1

                    # Check for next page
                    params['page'] += 1
                    time.sleep(1)  # Rate limiting

                    if len(studies) == 0:
                        break

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching from IHSN ({search_term}): {e}")
                    break
        
        return self.results
    
    def _extract_study_metadata(self, study_element) -> Optional[Dict[str, Any]]:
        """Extract metadata from a study element."""
        try:
            title_elem = study_element.find('a', class_='title') or study_element.find('h3')
            if not title_elem:
                return None
            
            title_link = title_elem.find('a') if title_elem.name != 'a' else title_elem
            title = title_link.get_text(strip=True) if title_link else title_elem.get_text(strip=True)
            study_url = title_link.get('href', '') if title_link else ''
            
            if study_url and not study_url.startswith('http'):
                study_url = f"{self.catalog_url}{study_url}"
            
            desc_elem = study_element.find(class_='description') or study_element.find('p')
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            return self.normalize_metadata({
                'filename': f"{title}.study",
                'file_extension': '.study',
                'file_size': None,
                'download_url': study_url,
                'source_repository': 'IHSN - International Household Survey Network',
                'source_url': study_url,
                'source_id': '',
                'license_type': '',
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
            print(f"Error extracting study metadata: {e}")
            return None
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific study."""
        return {}

