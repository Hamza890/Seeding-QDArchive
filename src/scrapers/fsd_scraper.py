"""
Scraper for FSD (Finnish Social Science Data Archive).
Uses OAI-PMH protocol and web scraping.
"""
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper


class FSDScraper(BaseScraper):
    """Scraper for Finnish Social Science Data Archive (FSD)."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """
        Initialize FSD scraper.
        
        Args:
            config_path: Path to QDA extensions config
        """
        super().__init__(config_path)
        self.base_url = "https://services.fsd.tuni.fi/catalogue"
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
        Search FSD for qualitative data.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            **kwargs: Additional parameters
            
        Returns:
            List of metadata dictionaries
        """
        self.clear_results()

        print(f"Searching FSD for qualitative data...")

        # FSD has a specific filter for qualitative data
        params = {
            'limit': 50,
            'study_language': 'en',
            'lang': 'en',
            'page': 0,
            'field': 'publishing_date',
            'direction': 'descending',
            'data_kind_string_facet': 'Qualitative'
        }

        params.update(kwargs)
        total_fetched = 0

        while total_fetched < max_results:
            try:
                response = self.session.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find study entries
                studies = soup.find_all('div', class_='study-row') or soup.find_all('tr', class_='study')
                
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

                # If we got fewer results than limit, we're done
                if len(studies) < params['limit']:
                    break

            except requests.exceptions.RequestException as e:
                print(f"Error fetching from FSD: {e}")
                break
        
        return self.results
    
    def _extract_study_metadata(self, study_element) -> Optional[Dict[str, Any]]:
        """Extract metadata from a study element."""
        try:
            # Extract study ID and title
            title_elem = study_element.find('a', class_='study-title') or study_element.find('a')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            study_url = title_elem.get('href', '')
            
            if study_url and not study_url.startswith('http'):
                study_url = f"https://services.fsd.tuni.fi{study_url}"
            
            # Extract study ID
            study_id = ''
            id_elem = study_element.find(class_='study-id') or study_element.find('td', class_='id')
            if id_elem:
                study_id = id_elem.get_text(strip=True)
            
            return self.normalize_metadata({
                'filename': f"{title}.study",
                'file_extension': '.study',
                'file_size': None,
                'download_url': study_url,
                'source_repository': 'FSD - Finnish Social Science Data Archive',
                'source_url': study_url,
                'source_id': study_id,
                'license_type': '',
                'license_url': '',
                'project_title': title,
                'project_description': '',
                'authors': '',
                'publication_date': '',
                'keywords': 'qualitative',
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
            url = f"{self.base_url}/study/{file_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            # Parse and return metadata
            return {}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching study {file_id}: {e}")
            return {}

