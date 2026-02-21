"""
Base scraper class for all repository scrapers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
from pathlib import Path


class BaseScraper(ABC):
    """Abstract base class for repository scrapers."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """
        Initialize scraper with QDA extensions configuration.
        
        Args:
            config_path: Path to QDA extensions configuration file
        """
        self.config_path = config_path
        self.qda_extensions = self._load_extensions()
        self.results = []
    
    def _load_extensions(self) -> List[str]:
        """Load QDA file extensions from configuration."""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            # Default extensions if config not found
            return [
                '.qdpx', '.qdc', '.mqda', '.nvp', '.nvpx', 
                '.atlasproj', '.hpr7', '.ppj', '.pprj', '.qlt', 
                '.f4p', '.qpd'
            ]
        
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config.get('all_extensions', [])
    
    def is_qda_file(self, filename: str) -> bool:
        """
        Check if filename has a QDA extension.
        
        Args:
            filename: Name of file to check
            
        Returns:
            True if file has QDA extension, False otherwise
        """
        filename_lower = filename.lower()
        return any(filename_lower.endswith(ext.lower()) for ext in self.qda_extensions)
    
    def get_qda_software(self, filename: str) -> Optional[str]:
        """
        Determine QDA software based on file extension.
        
        Args:
            filename: Name of file
            
        Returns:
            Name of QDA software or None
        """
        filename_lower = filename.lower()
        
        # Load full config for software mapping
        config_file = Path(self.config_path)
        if not config_file.exists():
            return None
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        for software, info in config.get('qda_software', {}).items():
            extensions = info.get('extensions', [])
            if any(filename_lower.endswith(ext.lower()) for ext in extensions):
                return software
        
        return None
    
    @abstractmethod
    def search(self, query: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Search repository for QDA files.
        
        Args:
            query: Optional search query
            **kwargs: Additional search parameters
            
        Returns:
            List of metadata dictionaries for found files
        """
        pass
    
    @abstractmethod
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific file.
        
        Args:
            file_id: Identifier for the file in the repository
            
        Returns:
            Dictionary with file metadata
        """
        pass
    
    def normalize_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize metadata to standard format.
        
        Args:
            raw_metadata: Raw metadata from repository
            
        Returns:
            Normalized metadata dictionary
        """
        # Base normalization - subclasses should override
        return {
            'filename': raw_metadata.get('filename'),
            'file_extension': raw_metadata.get('file_extension'),
            'download_url': raw_metadata.get('download_url'),
            'source_repository': self.__class__.__name__.replace('Scraper', ''),
            'source_url': raw_metadata.get('source_url'),
            'source_id': raw_metadata.get('source_id'),
            'license_type': raw_metadata.get('license_type'),
            'license_url': raw_metadata.get('license_url'),
            'project_title': raw_metadata.get('project_title'),
            'project_description': raw_metadata.get('project_description'),
            'authors': raw_metadata.get('authors'),
            'publication_date': raw_metadata.get('publication_date'),
            'keywords': raw_metadata.get('keywords'),
            'doi': raw_metadata.get('doi'),
            'qda_software': raw_metadata.get('qda_software'),
            'is_qda_file': raw_metadata.get('is_qda_file', True),  # Default to True for backward compatibility
        }
    
    def get_results(self) -> List[Dict[str, Any]]:
        """Get all search results."""
        return self.results
    
    def clear_results(self):
        """Clear stored results."""
        self.results = []
    
    def save_results(self, output_path: str):
        """
        Save results to JSON file.
        
        Args:
            output_path: Path to save results
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

