"""
Scraper for ADA (Australian Data Archive) - Dataverse-based repository.
"""
from .dataverse_scraper import DataverseScraper


class ADAScraper(DataverseScraper):
    """Scraper for Australian Data Archive (ADA)."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """
        Initialize ADA scraper.
        
        Args:
            config_path: Path to QDA extensions config
        """
        super().__init__(
            base_url="https://dataverse.ada.edu.au",
            config_path=config_path
        )
    
    def _build_file_metadata(self, file_info: dict, dataset: dict) -> dict:
        """Build normalized metadata for a file."""
        metadata = super()._build_file_metadata(file_info, dataset)
        metadata['source_repository'] = 'ADA - Australian Data Archive'
        return metadata

