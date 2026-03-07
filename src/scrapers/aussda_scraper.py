"""
Scraper for AUSSDA (Austrian Social Science Data Archive) - Dataverse-based repository.
"""
from .dataverse_scraper import DataverseScraper


class AUSSDAScraper(DataverseScraper):
    """Scraper for Austrian Social Science Data Archive (AUSSDA)."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """
        Initialize AUSSDA scraper.
        
        Args:
            config_path: Path to QDA extensions config
        """
        super().__init__(
            base_url="https://data.aussda.at",
            config_path=config_path
        )
    
    def _build_file_metadata(self, file_info: dict, dataset: dict) -> dict:
        """Build normalized metadata for a file."""
        metadata = super()._build_file_metadata(file_info, dataset)
        metadata['source_repository'] = 'AUSSDA - Austrian Social Science Data Archive'
        return metadata

