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
from .ada_scraper import ADAScraper
from .harvard_dataverse_scraper import HarvardDataverseScraper
from .aussda_scraper import AUSSDAScraper
from .cessda_scraper import CESSDAScraper
from .icpsr_scraper import ICSPRScraper
from .fsd_scraper import FSDScraper
from .sada_scraper import SADAScraper
from .ihsn_scraper import IHSNScraper
from .databrary_scraper import DatabraryScraper
from .sikt_scraper import SiktScraper
from .opendata_halle_scraper import OpenDataHalleScraper
from .cis_spain_scraper import CISSpainScraper
from .murray_scraper import MurrayScraper
from .columbia_oral_history_scraper import ColumbiaOralHistoryScraper

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
    'QualiBiScraper',
    'ADAScraper',
    'HarvardDataverseScraper',
    'AUSSDAScraper',
    'CESSDAScraper',
    'ICSPRScraper',
    'FSDScraper',
    'SADAScraper',
    'IHSNScraper',
    'DatabraryScraper',
    'SiktScraper',
    'OpenDataHalleScraper',
    'CISSpainScraper',
    'MurrayScraper',
    'ColumbiaOralHistoryScraper'
]

