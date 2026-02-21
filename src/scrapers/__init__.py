"""
Scrapers package for different data repositories.
"""
from .base_scraper import BaseScraper
from .zenodo_scraper import ZenodoScraper
from .dryad_scraper import DryadScraper
from .dataverse_scraper import DataverseScraper
from .web_scraper import WebScraper
from .dans_scraper import DANSScraper
from .syracuse_qdr_scraper import SyracuseQDRScraper
from .ukds_scraper import UKDataServiceScraper
from .qualidata_scraper import QualidataScraper, QualiserviceScraper, QualiBiScraper

__all__ = [
    'BaseScraper',
    'ZenodoScraper',
    'DryadScraper',
    'DataverseScraper',
    'WebScraper',
    'DANSScraper',
    'SyracuseQDRScraper',
    'UKDataServiceScraper',
    'QualidataScraper',
    'QualiserviceScraper',
    'QualiBiScraper'
]

