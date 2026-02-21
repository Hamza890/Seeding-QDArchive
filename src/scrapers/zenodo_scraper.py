"""
Scraper for Zenodo repository.
"""
import requests
import time
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper


class ZenodoScraper(BaseScraper):
    """Scraper for Zenodo open-access repository."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """Initialize Zenodo scraper."""
        super().__init__(config_path)
        self.api_base = "https://zenodo.org/api/records/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QDA-Archive-Bot/1.0 (Research Data Collection)'
        })
    
    def search(
        self,
        query: Optional[str] = None,
        max_results: int = 100,
        page_size: int = 100,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search Zenodo for QDA files.

        Args:
            query: Search query (if None, searches for qualitative data)
            max_results: Maximum number of results to return
            page_size: Number of results per page
            **kwargs: Additional search parameters

        Returns:
            List of metadata dictionaries for found files
        """
        self.clear_results()

        # Build search query for QDA files
        if not query:
            # Search for specific QDA software names - more likely to find actual QDA files
            # Try multiple searches with different keywords
            search_terms = [
                'MaxQDA OR NVivo OR ATLAS.ti',
                'qualitative data analysis software',
                'QDA OR CAQDAS'
            ]
            query = search_terms[0]  # Start with software names

        params = {
            'q': query,
            'size': min(page_size, 25),  # Zenodo max is 25 for anonymous users
            'page': 1
        }

        params.update(kwargs)

        total_fetched = 0

        while total_fetched < max_results:
            try:
                print(f"Fetching page {params['page']} from Zenodo...")
                response = self.session.get(self.api_base, params=params, timeout=15)
                response.raise_for_status()

                data = response.json()
                hits = data.get('hits', {}).get('hits', [])
                print(f"Got {len(hits)} records from Zenodo")
                
                if not hits:
                    break
                
                records_checked = 0
                for record in hits:
                    records_checked += 1

                    if total_fetched >= max_results:
                        break

                    # Check if record has QDA files
                    qda_files = self._extract_qda_files(record)

                    if qda_files:
                        print(f"Found {len(qda_files)} QDA file(s) in record!")
                        for file_meta in qda_files:
                            self.results.append(file_meta)
                            total_fetched += 1

                            if total_fetched >= max_results:
                                break

                print(f"Checked {records_checked} records, found {len(self.results)} QDA files so far")
                
                # Stop if we've checked enough pages without finding anything
                if params['page'] >= 5 and len(self.results) == 0:
                    print("Checked 5 pages without finding QDA files. Stopping search.")
                    break

                # Check if there are more pages
                total_hits = data.get('hits', {}).get('total', 0)
                if params['page'] * params['size'] >= total_hits:
                    break

                params['page'] += 1
                time.sleep(1)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching from Zenodo: {e}")
                break
        
        return self.results
    
    def _extract_qda_files(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract ALL files from a Zenodo record that contains QDA files.

        When a QDA file is found in a dataset, we download ALL files from that dataset
        including supporting files (PDFs, Word docs, Excel files, etc.)

        Args:
            record: Zenodo record data

        Returns:
            List of metadata dictionaries for ALL files in records containing QDA files
        """
        all_files = []

        files = record.get('files', [])
        metadata = record.get('metadata', {})

        # First, check if this record contains any QDA files
        has_qda_file = False
        for file_info in files:
            filename = file_info.get('key', '')
            if self.is_qda_file(filename):
                has_qda_file = True
                break

        # If record has QDA files, extract ALL files from it
        if has_qda_file:
            for file_info in files:
                file_meta = self._build_file_metadata(file_info, record)
                # Mark whether this specific file is a QDA file
                filename = file_info.get('key', '')
                file_meta['is_qda_file'] = self.is_qda_file(filename)
                all_files.append(file_meta)

        return all_files
    
    def _build_file_metadata(self, file_info: Dict[str, Any], record: Dict[str, Any]) -> Dict[str, Any]:
        """Build normalized metadata for a file."""
        metadata = record.get('metadata', {})
        
        # Extract authors
        creators = metadata.get('creators', [])
        authors = '; '.join([c.get('name', '') for c in creators])
        
        # Extract keywords
        keywords_list = metadata.get('keywords', [])
        keywords = '; '.join(keywords_list) if isinstance(keywords_list, list) else keywords_list
        
        # Extract license
        license_info = metadata.get('license', {})
        license_type = license_info.get('id', '') if isinstance(license_info, dict) else str(license_info)
        
        filename = file_info.get('key', '')
        file_extension = '.' + filename.split('.')[-1] if '.' in filename else ''
        
        return self.normalize_metadata({
            'filename': filename,
            'file_extension': file_extension.lower(),
            'file_size': file_info.get('size'),
            'download_url': file_info.get('links', {}).get('self'),
            'source_repository': 'Zenodo',
            'source_url': record.get('links', {}).get('html', ''),
            'source_id': str(record.get('id', '')),
            'license_type': license_type,
            'license_url': license_info.get('url', '') if isinstance(license_info, dict) else '',
            'project_title': metadata.get('title', ''),
            'project_description': metadata.get('description', ''),
            'authors': authors,
            'publication_date': metadata.get('publication_date', ''),
            'keywords': keywords,
            'doi': metadata.get('doi', ''),
            'version': metadata.get('version', ''),
            'qda_software': self.get_qda_software(filename),
        })
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific Zenodo record.
        
        Args:
            file_id: Zenodo record ID
            
        Returns:
            Dictionary with file metadata
        """
        try:
            url = f"{self.api_base}/{file_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            record = response.json()
            qda_files = self._extract_qda_files(record)
            
            return qda_files[0] if qda_files else {}
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching record {file_id}: {e}")
            return {}

