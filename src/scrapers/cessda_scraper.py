"""
Scraper for CESSDA (Consortium of European Social Science Data Archives).
Uses the CESSDA Data Catalogue REST API.
"""
import requests
import time
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper


class CESSDAScraper(BaseScraper):
    """Scraper for CESSDA Data Catalogue."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """
        Initialize CESSDA scraper.
        
        Args:
            config_path: Path to QDA extensions config
        """
        super().__init__(config_path)
        self.api_base = "https://api.tech.cessda.eu"
        self.web_base = "https://datacatalogue.cessda.eu"
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
        Search CESSDA for QDA files.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            **kwargs: Additional parameters
            
        Returns:
            List of metadata dictionaries
        """
        self.clear_results()

        # Search for specific QDA software names and qualitative research
        if not query:
            search_terms = ["qualitative", "interview", "NVivo", "MaxQDA", "ATLAS.ti"]
        else:
            search_terms = [query]

        total_fetched = 0

        for search_term in search_terms:
            if total_fetched >= max_results:
                break

            print(f"Searching CESSDA for: '{search_term}'...")

            params = {
                'q': search_term,
                'from': 0,
                'size': 25  # Results per page
            }

            params.update(kwargs)

            while total_fetched < max_results:
                try:
                    url = f"{self.api_base}/search"
                    response = self.session.get(url, params=params, timeout=30)
                    response.raise_for_status()

                    data = response.json()
                    
                    # CESSDA returns results in 'results' or 'hits' field
                    items = data.get('results', data.get('hits', []))

                    if not items:
                        break

                    for item in items:
                        if total_fetched >= max_results:
                            break

                        # Extract metadata from CESSDA item
                        file_meta = self._build_file_metadata(item)
                        
                        # Check if this is related to QDA research
                        if self._is_qualitative_study(item):
                            self.results.append(file_meta)
                            total_fetched += 1

                    # Check if more results available
                    total_count = data.get('total', 0)
                    if params['from'] + len(items) >= total_count:
                        break

                    params['from'] += len(items)
                    time.sleep(1)  # Rate limiting

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching from CESSDA ({search_term}): {e}")
                    break
        
        return self.results
    
    def _is_qualitative_study(self, item: Dict[str, Any]) -> bool:
        """Check if study is qualitative research."""
        # Check title, abstract, keywords for qualitative indicators
        text_fields = [
            item.get('title', ''),
            item.get('abstract', ''),
            ' '.join(item.get('keywords', [])),
            item.get('dataCollectionMethod', '')
        ]
        
        combined_text = ' '.join(text_fields).lower()
        
        qualitative_indicators = [
            'qualitative', 'interview', 'focus group', 'ethnograph',
            'nvivo', 'maxqda', 'atlas.ti', 'case study', 'observation'
        ]
        
        return any(indicator in combined_text for indicator in qualitative_indicators)
    
    def _build_file_metadata(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Build normalized metadata from CESSDA item."""
        # CESSDA provides study-level metadata, not individual files
        # We mark these as potential QDA studies
        
        study_url = item.get('studyUrl', '')
        if not study_url and item.get('id'):
            study_url = f"{self.web_base}/detail/{item.get('id')}"
        
        return self.normalize_metadata({
            'filename': f"{item.get('title', 'Unknown')}.study",
            'file_extension': '.study',  # Placeholder
            'file_size': None,
            'download_url': study_url,  # Link to study page
            'source_repository': 'CESSDA',
            'source_url': study_url,
            'source_id': item.get('id', ''),
            'license_type': item.get('dataAccessFreeTexts', ''),
            'license_url': '',
            'project_title': item.get('title', ''),
            'project_description': item.get('abstract', ''),
            'authors': '; '.join(item.get('creators', [])),
            'publication_date': item.get('publicationYear', ''),
            'keywords': '; '.join(item.get('keywords', [])),
            'doi': item.get('pidStudies', [{}])[0].get('pid', '') if item.get('pidStudies') else '',
            'qda_software': '',
            'is_qda_file': False  # CESSDA provides study metadata, not direct file downloads
        })
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific study."""
        try:
            url = f"{self.api_base}/study/{file_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            item = response.json()
            return self._build_file_metadata(item)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching study {file_id}: {e}")
            return {}

