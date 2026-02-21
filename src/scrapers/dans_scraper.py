"""
Scraper for DANS (Data Archiving and Networked Services).
"""
import requests
import time
from typing import List, Dict, Any, Optional
from xml.etree import ElementTree as ET
from .base_scraper import BaseScraper


class DANSScraper(BaseScraper):
    """Scraper for DANS repository using OAI-PMH protocol."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """Initialize DANS scraper."""
        super().__init__(config_path)
        self.oai_base = "https://easy.dans.knaw.nl/oai"
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
        Search DANS for QDA files using OAI-PMH.
        
        Args:
            query: Search query (not used for OAI-PMH)
            max_results: Maximum number of results
            **kwargs: Additional parameters
            
        Returns:
            List of metadata dictionaries
        """
        self.clear_results()
        
        # OAI-PMH ListRecords request
        params = {
            'verb': 'ListRecords',
            'metadataPrefix': 'oai_dc',
            'set': kwargs.get('set', None)  # Optional set specification
        }
        
        total_fetched = 0
        resumption_token = None
        
        while total_fetched < max_results:
            try:
                if resumption_token:
                    params = {
                        'verb': 'ListRecords',
                        'resumptionToken': resumption_token
                    }
                
                response = self.session.get(self.oai_base, params=params, timeout=30)
                response.raise_for_status()
                
                # Parse XML response
                root = ET.fromstring(response.content)
                
                # Define namespace
                ns = {'oai': 'http://www.openarchives.org/OAI/2.0/',
                      'dc': 'http://purl.org/dc/elements/1.1/'}
                
                # Find all records
                records = root.findall('.//oai:record', ns)
                
                if not records:
                    break
                
                for record in records:
                    if total_fetched >= max_results:
                        break
                    
                    # Extract metadata
                    metadata_elem = record.find('.//oai:metadata', ns)
                    if metadata_elem is not None:
                        file_meta = self._extract_metadata(record, ns)
                        
                        # Check if it's qualitative data (heuristic)
                        if self._is_qualitative_data(file_meta):
                            self.results.append(file_meta)
                            total_fetched += 1
                
                # Check for resumption token
                resumption_elem = root.find('.//oai:resumptionToken', ns)
                if resumption_elem is not None and resumption_elem.text:
                    resumption_token = resumption_elem.text
                else:
                    break
                
                time.sleep(1)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching from DANS: {e}")
                break
            except ET.ParseError as e:
                print(f"Error parsing XML from DANS: {e}")
                break
        
        return self.results
    
    def _extract_metadata(self, record: ET.Element, ns: Dict[str, str]) -> Dict[str, Any]:
        """Extract metadata from OAI-PMH record."""
        metadata = record.find('.//oai:metadata', ns)
        dc = metadata.find('.//{http://purl.org/dc/elements/1.1/}' if metadata is not None else '')
        
        # Extract Dublin Core elements
        def get_dc_element(name: str) -> str:
            elem = metadata.find(f'.//dc:{name}', ns) if metadata is not None else None
            return elem.text if elem is not None and elem.text else ''
        
        def get_all_dc_elements(name: str) -> str:
            elems = metadata.findall(f'.//dc:{name}', ns) if metadata is not None else []
            return '; '.join([e.text for e in elems if e.text])
        
        # Get identifier
        identifier_elem = record.find('.//oai:header/oai:identifier', ns)
        identifier = identifier_elem.text if identifier_elem is not None else ''
        
        # Build metadata
        title = get_dc_element('title')
        description = get_dc_element('description')
        creators = get_all_dc_elements('creator')
        subjects = get_all_dc_elements('subject')
        date = get_dc_element('date')
        rights = get_dc_element('rights')
        
        # Try to extract DOI or URL
        identifiers = get_all_dc_elements('identifier')
        doi = ''
        source_url = ''
        for ident in identifiers.split('; '):
            if 'doi.org' in ident or ident.startswith('10.'):
                doi = ident
            elif ident.startswith('http'):
                source_url = ident
        
        return self.normalize_metadata({
            'filename': f"{identifier.split(':')[-1]}.dat",  # Placeholder
            'file_extension': '',
            'download_url': source_url,
            'source_repository': 'DANS',
            'source_url': source_url,
            'source_id': identifier,
            'license_type': rights,
            'license_url': '',
            'project_title': title,
            'project_description': description,
            'authors': creators,
            'publication_date': date,
            'keywords': subjects,
            'doi': doi,
            'qda_software': '',
        })
    
    def _is_qualitative_data(self, metadata: Dict[str, Any]) -> bool:
        """Check if metadata suggests qualitative data."""
        qualitative_keywords = [
            'qualitative', 'interview', 'focus group', 'ethnograph',
            'case study', 'narrative', 'discourse', 'content analysis',
            'grounded theory', 'phenomenolog', 'hermeneutic'
        ]
        
        text_to_check = (
            metadata.get('project_title', '').lower() + ' ' +
            metadata.get('project_description', '').lower() + ' ' +
            metadata.get('keywords', '').lower()
        )
        
        return any(keyword in text_to_check for keyword in qualitative_keywords)
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific record."""
        try:
            params = {
                'verb': 'GetRecord',
                'identifier': file_id,
                'metadataPrefix': 'oai_dc'
            }
            
            response = self.session.get(self.oai_base, params=params, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            ns = {'oai': 'http://www.openarchives.org/OAI/2.0/',
                  'dc': 'http://purl.org/dc/elements/1.1/'}
            
            record = root.find('.//oai:record', ns)
            if record is not None:
                return self._extract_metadata(record, ns)
            
            return {}
            
        except Exception as e:
            print(f"Error fetching record {file_id}: {e}")
            return {}

