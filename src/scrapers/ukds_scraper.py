"""
Scraper for UK Data Service.
Uses the DataCite REST API (client-id=bl.ukda, DOI prefix 10.5255) for
study-level metadata.  The previous web-scraping approach targeted
beta.ukdataservice.ac.uk which has been replaced by a Vue SPA with no
accessible backend search endpoint.
"""
import requests
import time
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper


class UKDataServiceScraper(BaseScraper):
    """Scraper for UK Data Service via DataCite public API."""

    _DATACITE_URL = "https://api.datacite.org/dois"
    _CLIENT_ID = "bl.ukda"   # DOI prefix 10.5255
    _PAGE_SIZE = 50

    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """Initialize UK Data Service scraper."""
        super().__init__(config_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QDA-Archive-Bot/1.0 (Research Data Collection)',
            'Accept': 'application/json',
        })
    
    def search(
        self,
        query: Optional[str] = None,
        max_results: int = 50,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Search UK Data Service datasets via DataCite public API.

        DataCite has full-text search over UKDS DOI-registered datasets
        (client-id=bl.ukda, prefix 10.5255), returning study-level metadata.

        Args:
            query: Search query (e.g. "qualitative interview")
            max_results: Maximum number of study records to return
            **kwargs: Ignored (kept for API compatibility)

        Returns:
            List of normalized metadata dictionaries
        """
        self.clear_results()

        q = query or "qualitative"
        page = 1

        while len(self.results) < max_results:
            params = {
                'client-id': self._CLIENT_ID,
                'query': q,
                'page[size]': self._PAGE_SIZE,
                'page[number]': page,
            }
            try:
                resp = self.session.get(self._DATACITE_URL, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()

                items = data.get('data', [])
                if not items:
                    break

                for item in items:
                    if len(self.results) >= max_results:
                        break
                    self.results.append(self._build_file_metadata(item))

                # DataCite paginates via links.next
                if not data.get('links', {}).get('next'):
                    break

                page += 1
                time.sleep(0.5)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching from UK Data Service/DataCite (q={q!r}): {e}")
                break

        return self.results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_file_metadata(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Build normalized metadata from a DataCite record."""
        attrs = item.get('attributes', {})
        doi = attrs.get('doi', '')
        landing_url = attrs.get('url', f"https://doi.org/{doi}" if doi else '')

        titles = attrs.get('titles', [])
        title = titles[0].get('title', '') if titles else ''

        creators = attrs.get('creators', [])
        authors = '; '.join(
            c.get('name', '') or f"{c.get('givenName','')} {c.get('familyName','')}".strip()
            for c in creators
        )

        subjects = attrs.get('subjects', [])
        keywords = '; '.join(s.get('subject', '') for s in subjects if s.get('subject'))

        descriptions = attrs.get('descriptions', [])
        description = descriptions[0].get('description', '') if descriptions else ''

        rights_list = attrs.get('rightsList', [])
        license_name = rights_list[0].get('rights', '') if rights_list else 'UK Data Service End User Licence'
        license_url = rights_list[0].get('rightsUri', '') if rights_list else 'https://ukdataservice.ac.uk/help/access-policy/'

        pub_year = str(attrs.get('publicationYear', '') or '')

        return self.normalize_metadata({
            'filename': f"{title or doi}.study",
            'file_extension': '.study',
            'file_size': None,
            'download_url': landing_url,
            'source_repository': 'UK Data Service',
            'source_url': landing_url,
            'source_id': doi,
            'license_type': license_name,
            'license_url': license_url,
            'project_title': title,
            'project_description': description,
            'authors': authors,
            'publication_date': pub_year,
            'keywords': keywords,
            'doi': doi,
            'qda_software': '',
            'is_qda_file': False,
        })

    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific UKDS study by its DOI."""
        try:
            resp = self.session.get(
                f"{self._DATACITE_URL}/{file_id}", timeout=30
            )
            resp.raise_for_status()
            item = resp.json().get('data', {})
            return self._build_file_metadata(item)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching UKDS study {file_id}: {e}")
            return {}

