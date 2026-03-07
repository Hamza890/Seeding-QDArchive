"""
Scraper for Harvard Dataverse - Dataverse-based repository.
"""
from .dataverse_scraper import DataverseScraper


class HarvardDataverseScraper(DataverseScraper):
    """Scraper for Harvard Dataverse."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """
        Initialize Harvard Dataverse scraper.
        
        Args:
            config_path: Path to QDA extensions config
        """
        super().__init__(
            base_url="https://dataverse.harvard.edu",
            config_path=config_path
        )
    
    def _build_file_metadata(self, file_info: dict, dataset: dict) -> dict:
        """Build normalized metadata for a file."""
        metadata = super()._build_file_metadata(file_info, dataset)
        metadata['source_repository'] = 'Harvard Dataverse'
        return metadata

