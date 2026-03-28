"""
Scraper for Syracuse Qualitative Data Repository (QDR).
"""
import requests
import time
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper


class SyracuseQDRScraper(BaseScraper):
    """Scraper for Syracuse QDR - uses Dataverse API."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """Initialize Syracuse QDR scraper."""
        super().__init__(config_path)
        self.base_url = "https://data.qdr.syr.edu"
        self.api_base = f"{self.base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QDA-Archive-Bot/1.0 (Research Data Collection)'
        })
    
    def search(
        self,
        query: Optional[str] = None,
        max_results: int = 100,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search Syracuse QDR for QDA files.

        Args:
            query: Search query
            max_results: Maximum number of results
            **kwargs: Additional parameters

        Returns:
            List of metadata dictionaries
        """
        self.clear_results()

        # Search for specific QDA file extensions and software names
        if not query:
            search_terms = ["qdpx", "mqda", "nvp", "NVivo", "MaxQDA", "ATLAS.ti", "interview study"]
        else:
            search_terms = [query]

        total_fetched = 0

        for search_term in search_terms:
            if total_fetched >= max_results:
                break

            print(f"Searching Syracuse QDR for: '{search_term}'...")

            # Search both files and datasets
            for search_type in ['file', 'dataset']:
                if total_fetched >= max_results:
                    break

                params = {
                    'q': search_term,
                    'type': search_type,
                    'per_page': 100,
                    'start': 0
                }

                params.update(kwargs)

                try:
                    url = f"{self.api_base}/search"
                    response = self.session.get(url, params=params, timeout=60)  # Increased timeout
                    response.raise_for_status()

                    data = response.json()

                    if data.get('status') != 'OK':
                        continue

                    items = data.get('data', {}).get('items', [])

                    if not items:
                        continue

                    for item in items:
                        if total_fetched >= max_results:
                            break

                        if search_type == 'file':
                            # Direct file result
                            file_name = item.get('name', '')
                            if self.is_qda_file(file_name):
                                dataset_persistent_id = item.get('dataset_persistent_id', '')
                                dataset_url = (
                                    f"{self.base_url}/dataset.xhtml?persistentId={dataset_persistent_id}"
                                    if dataset_persistent_id else None
                                )
                                file_meta = {
                                    'filename': file_name,
                                    'file_extension': '.' + file_name.split('.')[-1].lower() if '.' in file_name else None,
                                    'download_url': item.get('url'),
                                    'source_url': dataset_url,
                                    'source_id': item.get('file_id') or item.get('file_persistent_id'),
                                    'project_title': item.get('dataset_name', 'Unknown'),
                                    'project_description': item.get('description', ''),
                                    'publication_date': item.get('releaseOrCreateDate') or item.get('published_at'),
                                    'doi': dataset_persistent_id or item.get('file_persistent_id'),
                                    'qda_software': self.get_qda_software(file_name),
                                    'source_repository': 'Syracuse QDR',
                                }
                                self.results.append(self.normalize_metadata(file_meta))
                                total_fetched += 1
                                print(f"Found QDA file: {file_name}")
                        else:
                            # Dataset result - check files
                            dataset_id = item.get('global_id') or item.get('entity_id')
                            if dataset_id:
                                qda_files = self._get_dataset_files(dataset_id)

                                for file_meta in qda_files:
                                    self.results.append(file_meta)
                                    total_fetched += 1

                                    if total_fetched >= max_results:
                                        break

                    time.sleep(2)  # Increased rate limiting for slow API

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching from Syracuse QDR ({search_term}, {search_type}): {e}")
                    continue

        return self.results
    
    def _get_dataset_files(self, dataset_id: str) -> List[Dict[str, Any]]:
        """Get files from a QDR dataset."""
        all_files = []

        try:
            # Get dataset metadata
            url = f"{self.api_base}/datasets/:persistentId/?persistentId={dataset_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('status') != 'OK':
                return all_files

            dataset = data.get('data', {})
            latest_version = dataset.get('latestVersion', {})
            files = latest_version.get('files', [])

            # First, check if this dataset contains any QDA files
            has_qda_file = False
            for file_info in files:
                datafile = file_info.get('dataFile', {})
                filename = datafile.get('filename', '')
                if self.is_qda_file(filename):
                    has_qda_file = True
                    break

            # If dataset has QDA files, extract ALL files from it
            if has_qda_file:
                print(f"Found {len(files)} file(s) in dataset!")
                for file_info in files:
                    datafile = file_info.get('dataFile', {})
                    filename = datafile.get('filename', '')
                    file_meta = self._build_file_metadata(file_info, dataset)
                    file_meta['is_qda_file'] = self.is_qda_file(filename)
                    all_files.append(file_meta)

            time.sleep(0.5)  # Rate limiting

        except requests.exceptions.RequestException as e:
            print(f"Error fetching dataset {dataset_id}: {e}")

        return all_files
    
    def _build_file_metadata(self, file_info: Dict[str, Any], dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Build normalized metadata for a file."""
        datafile = file_info.get('dataFile', {})
        latest_version = dataset.get('latestVersion', {})
        metadata_blocks = latest_version.get('metadataBlocks', {})
        citation = metadata_blocks.get('citation', {})
        
        # Extract authors
        authors_list = citation.get('fields', [])
        authors = ''
        for field in authors_list:
            if field.get('typeName') == 'author':
                author_values = field.get('value', [])
                authors = '; '.join([
                    a.get('authorName', {}).get('value', '') 
                    for a in author_values
                ])
                break
        
        # Extract keywords
        keywords = ''
        for field in citation.get('fields', []):
            if field.get('typeName') == 'keyword':
                keyword_values = field.get('value', [])
                keywords = '; '.join([
                    k.get('keywordValue', {}).get('value', '') 
                    for k in keyword_values
                ])
                break
        
        # Extract title and description
        title = ''
        description = ''
        for field in citation.get('fields', []):
            if field.get('typeName') == 'title':
                title = field.get('value', '')
            elif field.get('typeName') == 'dsDescription':
                desc_values = field.get('value', [])
                if desc_values:
                    description = desc_values[0].get('dsDescriptionValue', {}).get('value', '')
        
        filename = datafile.get('filename', '')
        file_extension = '.' + filename.split('.')[-1] if '.' in filename else ''
        file_id = datafile.get('id', '')
        
        # Build download URL
        download_url = f"{self.api_base}/access/datafile/{file_id}" if file_id else ''
        
        # Get persistent ID (DOI)
        persistent_id = (
            dataset.get('persistentId')
            or latest_version.get('datasetPersistentId')
            or ''
        )
        
        license_info = latest_version.get('license') or {}
        if isinstance(license_info, dict):
            license_type = license_info.get('name') or 'Unknown'
            license_url = license_info.get('uri')
        else:
            license_type = license_info or 'Unknown'
            license_url = 'https://creativecommons.org/licenses/by/4.0/'
        
        return self.normalize_metadata({
            'filename': filename,
            'file_extension': file_extension.lower(),
            'file_size': datafile.get('filesize'),
            'download_url': download_url,
            'source_repository': 'Syracuse QDR',
            'source_url': f"{self.base_url}/dataset.xhtml?persistentId={persistent_id}",
            'source_id': str(file_id),
            'license_type': license_type,
            'license_url': license_url,
            'project_title': title,
            'project_description': description,
            'authors': authors,
            'publication_date': latest_version.get('releaseTime', ''),
            'keywords': keywords,
            'doi': persistent_id,
            'qda_software': self.get_qda_software(filename),
        })
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific dataset."""
        qda_files = self._get_dataset_files(file_id)
        return qda_files[0] if qda_files else {}

