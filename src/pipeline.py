"""
Main pipeline orchestrator for QDA file collection.
"""
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from database import MetadataDatabase
from download_manager import DownloadManager
from scrapers import (
    ZenodoScraper,
    DryadScraper,
    DataverseScraper,
    WebScraper,
    DANSScraper,
    SyracuseQDRScraper,
    UKDataServiceScraper,
    QualidataScraper,
    QualiserviceScraper,
    QualiBiScraper
)


class QDAPipeline:
    """Main pipeline for discovering and downloading QDA files."""
    
    def __init__(
        self, 
        db_path: str = "qda_archive.db",
        download_dir: str = "downloads",
        config_dir: str = "config"
    ):
        """
        Initialize pipeline.
        
        Args:
            db_path: Path to SQLite database
            download_dir: Directory for downloaded files
            config_dir: Directory containing configuration files
        """
        self.db = MetadataDatabase(db_path)
        self.downloader = DownloadManager(download_dir)
        self.config_dir = Path(config_dir)
        
        # Load data sources configuration
        sources_config = self.config_dir / "data_sources.json"
        with open(sources_config, 'r') as f:
            self.sources_config = json.load(f)
        
        # Initialize scrapers
        self.scrapers = self._initialize_scrapers()
    
    def _initialize_scrapers(self) -> Dict[str, Any]:
        """Initialize all scrapers."""
        scrapers = {}

        # Zenodo
        scrapers['zenodo'] = ZenodoScraper()

        # Dryad
        scrapers['dryad'] = DryadScraper()

        # DataverseNO
        scrapers['dataverse_no'] = DataverseScraper(
            base_url="https://dataverse.no"
        )

        # DANS (Data Archiving and Networked Services)
        scrapers['dans'] = DANSScraper()

        # Syracuse QDR (Qualitative Data Repository)
        scrapers['syracuse_qdr'] = SyracuseQDRScraper()

        # UK Data Service
        scrapers['uk_data_service'] = UKDataServiceScraper()

        # Qualidata Network repositories
        scrapers['qualidata'] = QualidataScraper()
        scrapers['qualiservice'] = QualiserviceScraper()
        scrapers['qualibi'] = QualiBiScraper()

        return scrapers
    
    def run_scraper(
        self, 
        scraper_name: str, 
        max_results: int = 100,
        download: bool = False,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Run a specific scraper.
        
        Args:
            scraper_name: Name of scraper to run
            max_results: Maximum results to collect
            download: Whether to download files immediately
            **kwargs: Additional scraper parameters
            
        Returns:
            List of found file metadata
        """
        if scraper_name not in self.scrapers:
            print(f"Unknown scraper: {scraper_name}")
            return []
        
        print(f"\n{'='*60}")
        print(f"Running {scraper_name} scraper...")
        print(f"{'='*60}")
        
        scraper = self.scrapers[scraper_name]
        results = scraper.search(max_results=max_results, **kwargs)
        
        print(f"Found {len(results)} QDA files")
        
        # Save to database
        for file_meta in results:
            file_id = self.db.insert_file(file_meta)
            print(f"  - {file_meta.get('filename')} (ID: {file_id})")
            
            # Download if requested
            if download:
                self._download_file(file_id, file_meta)
        
        return results
    
    def run_all_scrapers(
        self, 
        max_results_per_scraper: int = 50,
        download: bool = False
    ):
        """
        Run all scrapers.
        
        Args:
            max_results_per_scraper: Max results per scraper
            download: Whether to download files
        """
        print(f"\n{'#'*60}")
        print(f"# Running all scrapers")
        print(f"# Max results per scraper: {max_results_per_scraper}")
        print(f"# Download files: {download}")
        print(f"{'#'*60}")
        
        for scraper_name in self.scrapers.keys():
            try:
                self.run_scraper(
                    scraper_name, 
                    max_results=max_results_per_scraper,
                    download=download
                )
            except Exception as e:
                print(f"Error running {scraper_name}: {e}")
        
        # Print statistics
        self.print_statistics()
    
    def _download_file(self, file_id: int, file_meta: Dict[str, Any]):
        """Download a file and update database."""
        download_url = file_meta.get('download_url')

        if not download_url:
            print(f"    No download URL for file {file_id}")
            return

        print(f"    Downloading {file_meta.get('filename')}...")

        # Create hierarchical folder structure: repository/dataset_id/
        repository = file_meta.get('source_repository', 'unknown')
        dataset_id = file_meta.get('source_id', file_meta.get('dataset_id', 'unknown_dataset'))

        # Use project title as folder name if available (more readable)
        project_title = file_meta.get('project_title', '')
        if project_title and len(project_title) > 0:
            # Use title-id format for better readability
            dataset_folder_name = f"{project_title}-{dataset_id}"
        else:
            dataset_folder_name = dataset_id

        # Clean folder names (remove special characters)
        repository_folder = self._sanitize_folder_name(repository)
        dataset_folder = self._sanitize_folder_name(dataset_folder_name)

        # Create path: downloads/repository/dataset_id/
        subfolder = f"{repository_folder}/{dataset_folder}"

        result = self.downloader.download_file(
            url=download_url,
            filename=file_meta.get('filename'),
            subfolder=subfolder
        )
        
        # Update database with download results
        updates = {
            'file_path': result.get('file_path'),
            'file_size': result.get('file_size'),
            'md5_hash': result.get('md5_hash'),
            'sha256_hash': result.get('sha256_hash'),
            'download_date': result.get('download_date'),
            'download_status': 'completed' if result.get('success') else 'failed',
            'error_message': result.get('error_message')
        }
        
        self.db.update_file(file_id, updates)
        
        if result.get('success'):
            print(f"    ✓ Downloaded successfully")
        else:
            print(f"    ✗ Download failed: {result.get('error_message')}")
    
    def _sanitize_folder_name(self, name: str) -> str:
        """
        Sanitize folder name by removing/replacing invalid characters.

        Args:
            name: Original folder name

        Returns:
            Sanitized folder name safe for filesystem
        """
        import re
        # Replace spaces and special characters with underscores
        sanitized = re.sub(r'[^\w\-.]', '_', name)
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        return sanitized.lower()

    def download_pending_files(self):
        """Download all files with pending status."""
        pending_files = self.db.get_all_files({'download_status': 'pending'})

        print(f"\nDownloading {len(pending_files)} pending files...")

        for file_meta in pending_files:
            file_id = file_meta['id']
            self._download_file(file_id, file_meta)
    
    def export_metadata(self, output_path: str = "metadata_export.csv"):
        """Export metadata to CSV."""
        print(f"\nExporting metadata to {output_path}...")
        self.db.export_to_csv(output_path)
    
    def print_statistics(self):
        """Print archive statistics."""
        stats = self.db.get_statistics()
        
        print(f"\n{'='*60}")
        print(f"Archive Statistics")
        print(f"{'='*60}")
        print(f"Total files: {stats['total_files']}")
        print(f"  QDA files: {stats.get('qda_files', 0)}")
        print(f"  Supporting files: {stats.get('supporting_files', 0)}")

        print(f"\nBy status:")
        for status, count in stats.get('by_status', {}).items():
            print(f"  {status}: {count}")

        print(f"\nBy repository:")
        for repo, count in stats.get('by_repository', {}).items():
            print(f"  {repo}: {count}")
        
        print(f"\nBy file extension:")
        for ext, count in stats.get('by_extension', {}).items():
            print(f"  {ext}: {count}")
    
    def close(self):
        """Clean up resources."""
        self.db.close()

