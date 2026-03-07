"""
Scraper for CIS - Centro de Investigaciones Sociológicas (Spain).
"""
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper


class CISSpainScraper(BaseScraper):
    """Scraper for CIS Spain (Centro de Investigaciones Sociológicas)."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """
        Initialize CIS Spain scraper.
        
        Args:
            config_path: Path to QDA extensions config
        """
        super().__init__(config_path)
        self.base_url = "https://www.cis.es/estudios/catalogo-estudios"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QDA-Archive-Bot/1.0 (Research Data Collection)',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
        })
    
    def search(
        self, 
        query: Optional[str] = None, 
        max_results: int = 100,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search CIS Spain for qualitative data.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            **kwargs: Additional parameters
            
        Returns:
            List of metadata dictionaries
        """
        self.clear_results()

        # Search for qualitative-related terms (in Spanish)
        if not query:
            search_terms = ["cualitativo", "entrevista", "grupo focal", "qualitative", "interview"]
        else:
            search_terms = [query]

        total_fetched = 0

        for search_term in search_terms:
            if total_fetched >= max_results:
                break

            print(f"Searching CIS Spain for: '{search_term}'...")

            params = {
                'busqueda': search_term,
                'page': 0
            }

            params.update(kwargs)

            while total_fetched < max_results:
                try:
                    response = self.session.get(self.base_url, params=params, timeout=30)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find study entries
                    studies = soup.find_all('div', class_='estudio') or soup.find_all('article', class_='study')
                    
                    if not studies:
                        # Try alternative selectors
                        studies = soup.find_all('div', class_='item-estudio') or soup.find_all('tr', class_='study-row')
                    
                    if not studies:
                        print("No studies found or page structure changed.")
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
                    print(f"Error fetching from CIS Spain ({search_term}): {e}")
                    break
        
        return self.results
    
    def _extract_study_metadata(self, study_element) -> Optional[Dict[str, Any]]:
        """Extract metadata from a study element."""
        try:
            # Find title
            title_elem = study_element.find('h3') or study_element.find('h2') or study_element.find('a', class_='titulo')
            if not title_elem:
                return None
            
            title_link = title_elem.find('a') if title_elem.name != 'a' else title_elem
            title = title_link.get_text(strip=True) if title_link else title_elem.get_text(strip=True)
            study_url = title_link.get('href', '') if title_link else ''
            
            if study_url and not study_url.startswith('http'):
                study_url = f"https://www.cis.es{study_url}"
            
            # Find study number
            study_id = ''
            id_elem = study_element.find(class_='numero-estudio') or study_element.find(text=lambda t: 'Estudio' in str(t))
            if id_elem:
                study_id = id_elem.get_text(strip=True)
            
            # Find description
            desc_elem = study_element.find('p', class_='descripcion') or study_element.find('p')
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            return self.normalize_metadata({
                'filename': f"{title}.study",
                'file_extension': '.study',
                'file_size': None,
                'download_url': study_url,
                'source_repository': 'CIS - Centro de Investigaciones Sociológicas',
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
        return {}

