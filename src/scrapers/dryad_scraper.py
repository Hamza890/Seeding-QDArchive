"""
Scraper for Dryad repository.
"""
import requests
import time
from typing import List, Dict, Any, Optional
from urllib.parse import quote
from .base_scraper import BaseScraper


class DryadScraper(BaseScraper):
    """Scraper for Dryad data repository."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """Initialize Dryad scraper."""
        super().__init__(config_path)
        self.api_base = "https://datadryad.org/api/v2"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QDA-Archive-Bot/1.0 (Research Data Collection)',
            'Content-Type': 'application/json'
        })
    
    def search(
        self, 
        query: Optional[str] = None, 
        max_results: int = 100,
        page_size: int = 100,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search Dryad for QDA files.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            page_size: Results per page
            **kwargs: Additional parameters
            
        Returns:
            List of metadata dictionaries
        """
        self.clear_results()

        # Search for each QDA software separately (OR operator doesn't work in Dryad)
        if not query:
            # Search for each software name individually
            search_terms = ["NVivo", "MaxQDA", "ATLAS.ti", "HyperRESEARCH", "Dedoose"]
        else:
            search_terms = [query]

        total_fetched = 0

        for search_term in search_terms:
            if total_fetched >= max_results:
                break

            print(f"Searching Dryad for: '{search_term}'...")

            params = {
                'q': search_term,
                'per_page': min(page_size, 100),
                'page': 1
            }

            params.update(kwargs)

            while total_fetched < max_results:
                try:
                    url = f"{self.api_base}/search"
                    response = self.session.get(url, params=params, timeout=30)
                    response.raise_for_status()

                    data = response.json()
                    datasets = data.get('_embedded', {}).get('stash:datasets', [])

                    if not datasets:
                        break

                    for dataset in datasets:
                        if total_fetched >= max_results:
                            break

                        # Get dataset details including files
                        dataset_id = dataset.get('identifier')
                        if dataset_id:
                            qda_files = self._get_dataset_files(dataset_id)

                            for file_meta in qda_files:
                                self.results.append(file_meta)
                                total_fetched += 1

                                if total_fetched >= max_results:
                                    break

                    # Check for next page
                    links = data.get('_links', {})
                    if 'next' not in links:
                        break

                    params['page'] += 1
                    time.sleep(2)  # Rate limiting - increased to avoid 429 errors

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching from Dryad ({search_term}): {e}")
                    break

        return self.results
    
    def _get_dataset_files(self, dataset_id: str) -> List[Dict[str, Any]]:
        """Get files from a Dryad dataset."""
        all_files = []

        try:
            # URL-encode the DOI for the API request
            encoded_id = quote(dataset_id, safe='')

            # Get dataset details
            url = f"{self.api_base}/datasets/{encoded_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            dataset = response.json()

            # Get version link to access files
            version_link = dataset.get('_links', {}).get('stash:version', {})
            if isinstance(version_link, dict):
                version_href = version_link.get('href', '')
            else:
                # Fallback: try to construct version URL
                version_href = f"/api/v2/datasets/{encoded_id}/versions/1"

            if not version_href:
                return all_files

            # Make version URL absolute
            if version_href.startswith('/'):
                version_url = f"https://datadryad.org{version_href}"
            else:
                version_url = version_href

            # Get version details which includes files
            version_response = self.session.get(version_url, timeout=30)
            version_response.raise_for_status()

            version_data = version_response.json()
            files = version_data.get('_embedded', {}).get('stash:files', [])

            # First, check if this dataset contains any QDA files
            has_qda_file = False
            for file_info in files:
                filename = file_info.get('path', '')
                if self.is_qda_file(filename):
                    has_qda_file = True
                    break

            # If dataset has QDA files, extract ALL files from it
            if has_qda_file:
                print(f"Found {len(files)} file(s) in dataset!")
                for file_info in files:
                    filename = file_info.get('path', '')
                    file_meta = self._build_file_metadata(file_info, dataset)
                    file_meta['is_qda_file'] = self.is_qda_file(filename)
                    all_files.append(file_meta)

            time.sleep(1)  # Rate limiting - increased to avoid 429 errors

        except requests.exceptions.RequestException as e:
            print(f"Error fetching dataset {dataset_id}: {e}")

        return all_files
    
    def _build_file_metadata(self, file_info: Dict[str, Any], dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Build normalized metadata for a file."""
        # Extract authors
        authors_list = dataset.get('authors', [])
        authors = '; '.join([
            f"{a.get('firstName', '')} {a.get('lastName', '')}".strip() 
            for a in authors_list
        ])
        
        # Extract keywords
        keywords_list = dataset.get('keywords', [])
        keywords = '; '.join(keywords_list) if isinstance(keywords_list, list) else ''
        
        # License
        license_info = dataset.get('license', 'CC0-1.0')  # Dryad default
        
        filename = file_info.get('path', '')
        file_extension = '.' + filename.split('.')[-1] if '.' in filename else ''
        
        return self.normalize_metadata({
            'filename': filename,
            'file_extension': file_extension.lower(),
            'file_size': file_info.get('size'),
            'download_url': file_info.get('_links', {}).get('stash:download', {}).get('href'),
            'source_repository': 'Dryad',
            'source_url': dataset.get('_links', {}).get('stash:landing-page', {}).get('href'),
            'source_id': dataset.get('identifier', ''),
            'license_type': license_info,
            'license_url': 'https://creativecommons.org/publicdomain/zero/1.0/',
            'project_title': dataset.get('title', ''),
            'project_description': dataset.get('abstract', ''),
            'authors': authors,
            'publication_date': dataset.get('publicationDate', ''),
            'keywords': keywords,
            'doi': dataset.get('identifier', ''),
            'qda_software': self.get_qda_software(filename),
        })
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific dataset."""
        qda_files = self._get_dataset_files(file_id)
        return qda_files[0] if qda_files else {}

