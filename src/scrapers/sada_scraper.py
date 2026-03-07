"""
Scraper for SADA (South African Data Archive) - DataFirst.
Uses NADA (National Data Archive) software.
"""
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper


class SADAScraper(BaseScraper):
    """Scraper for South African Data Archive (SADA/DataFirst)."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """
        Initialize SADA scraper.
        
        Args:
            config_path: Path to QDA extensions config
        """
        super().__init__(config_path)
        self.base_url = "https://www.datafirst.uct.ac.za/dataportal/index.php/catalog"
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
        Search SADA for qualitative data.
        
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
            search_terms = ["interview", "qualitative", "focus group"]
        else:
            search_terms = [query]

        total_fetched = 0

        for search_term in search_terms:
            if total_fetched >= max_results:
                break

            print(f"Searching SADA for: '{search_term}'...")

            params = {
                'sk': search_term,
                'ps': 50,
                'page': 1
            }

            params.update(kwargs)

            while total_fetched < max_results:
                try:
                    response = self.session.get(self.base_url, params=params, timeout=30)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find study entries in NADA catalog
                    studies = soup.find_all('div', class_='study-row') or soup.find_all('div', class_='catalog-search-result')
                    
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

                    # If we got fewer results than expected, we're done
                    if len(studies) < params['ps']:
                        break

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching from SADA ({search_term}): {e}")
                    break
        
        return self.results
    
    def _extract_study_metadata(self, study_element) -> Optional[Dict[str, Any]]:
        """Extract metadata from a study element."""
        try:
            # Extract title and link
            title_elem = study_element.find('a', class_='title') or study_element.find('h3')
            if title_elem:
                title_link = title_elem.find('a') if title_elem.name != 'a' else title_elem
                title = title_link.get_text(strip=True) if title_link else title_elem.get_text(strip=True)
                study_url = title_link.get('href', '') if title_link else ''
            else:
                return None
            
            if study_url and not study_url.startswith('http'):
                study_url = f"https://www.datafirst.uct.ac.za/dataportal/index.php{study_url}"
            
            # Extract study ID
            study_id = ''
            id_elem = study_element.find(class_='study-id') or study_element.find(text=lambda t: 'ID:' in str(t))
            if id_elem:
                study_id = id_elem.get_text(strip=True).replace('ID:', '').strip()
            
            # Extract description
            desc_elem = study_element.find(class_='description') or study_element.find('p')
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            return self.normalize_metadata({
                'filename': f"{title}.study",
                'file_extension': '.study',
                'file_size': None,
                'download_url': study_url,
                'source_repository': 'SADA - South African Data Archive',
                'source_url': study_url,
                'source_id': study_id,
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
        try:
            url = f"{self.base_url}/{file_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            # Parse and return metadata
            return {}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching study {file_id}: {e}")
            return {}

