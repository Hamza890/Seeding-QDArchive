"""
Scraper for ICPSR (Inter-university Consortium for Political and Social Research).
Uses the ICPSR Metadata Export API.
"""
import requests
import time
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper


class ICSPRScraper(BaseScraper):
    """Scraper for ICPSR."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """
        Initialize ICPSR scraper.
        
        Args:
            config_path: Path to QDA extensions config
        """
        super().__init__(config_path)
        self.api_base = "https://www.icpsr.umich.edu/web/ICPSR"
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
        Search ICPSR for QDA files.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            **kwargs: Additional parameters
            
        Returns:
            List of metadata dictionaries
        """
        self.clear_results()

        # Search for specific QDA-related terms
        if not query:
            search_terms = ["qualitative", "interview", "focus group", "ethnographic"]
        else:
            search_terms = [query]

        total_fetched = 0

        for search_term in search_terms:
            if total_fetched >= max_results:
                break

            print(f"Searching ICPSR for: '{search_term}'...")

            params = {
                'q': search_term,
                'start': 0,
                'rows': 50,  # Results per page
                'sort': 'score desc'
            }

            params.update(kwargs)

            while total_fetched < max_results:
                try:
                    url = f"{self.api_base}/search/studies"
                    response = self.session.get(url, params=params, timeout=30)
                    response.raise_for_status()

                    # ICPSR may return HTML or JSON depending on endpoint
                    # For now, we'll parse the response
                    data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    
                    items = data.get('response', {}).get('docs', [])

                    if not items:
                        break

                    for item in items:
                        if total_fetched >= max_results:
                            break

                        # Extract metadata from ICPSR item
                        file_meta = self._build_file_metadata(item)
                        
                        # Check if this is qualitative research
                        if self._is_qualitative_study(item):
                            self.results.append(file_meta)
                            total_fetched += 1

                    # Check if more results available
                    total_count = data.get('response', {}).get('numFound', 0)
                    if params['start'] + len(items) >= total_count:
                        break

                    params['start'] += len(items)
                    time.sleep(1)  # Rate limiting

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching from ICPSR ({search_term}): {e}")
                    break
                except ValueError:
                    # If JSON parsing fails, break
                    print(f"Could not parse JSON response from ICPSR")
                    break
        
        return self.results
    
    def _is_qualitative_study(self, item: Dict[str, Any]) -> bool:
        """Check if study is qualitative research."""
        # Check various fields for qualitative indicators
        text_fields = [
            item.get('title', ''),
            item.get('summary', ''),
            ' '.join(item.get('subject', [])),
            item.get('methodology', '')
        ]
        
        combined_text = ' '.join(str(f) for f in text_fields).lower()
        
        qualitative_indicators = [
            'qualitative', 'interview', 'focus group', 'ethnograph',
            'nvivo', 'maxqda', 'atlas.ti', 'case study', 'observation',
            'field notes', 'transcript'
        ]
        
        return any(indicator in combined_text for indicator in qualitative_indicators)
    
    def _build_file_metadata(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Build normalized metadata from ICPSR item."""
        study_number = item.get('study_number', item.get('id', ''))
        study_url = f"https://www.icpsr.umich.edu/web/ICPSR/studies/{study_number}" if study_number else ''
        
        # Extract DOI if available
        doi = ''
        if item.get('doi'):
            doi = item.get('doi')
        
        return self.normalize_metadata({
            'filename': f"{item.get('title', 'Unknown')}.study",
            'file_extension': '.study',  # Placeholder
            'file_size': None,
            'download_url': study_url,
            'source_repository': 'ICPSR',
            'source_url': study_url,
            'source_id': str(study_number),
            'license_type': item.get('data_access', ''),
            'license_url': '',
            'project_title': item.get('title', ''),
            'project_description': item.get('summary', ''),
            'authors': '; '.join(item.get('principal_investigators', [])),
            'publication_date': item.get('publication_date', ''),
            'keywords': '; '.join(item.get('subject', [])),
            'doi': doi,
            'qda_software': '',
            'is_qda_file': False  # ICPSR provides study metadata
        })
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific study."""
        try:
            url = f"{self.api_base}/studies/{file_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            # Parse response (may need adjustment based on actual API)
            return {}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching study {file_id}: {e}")
            return {}

