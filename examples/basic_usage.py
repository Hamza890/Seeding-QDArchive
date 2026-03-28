"""
Example: Basic usage of the QDA Archive pipeline.

This script demonstrates how to use the pipeline programmatically.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pipeline import QDAPipeline


def example_search_zenodo():
    """Example: Search Zenodo for QDA files."""
    print("=" * 60)
    print("Example 1: Search Zenodo for QDA files")
    print("=" * 60)
    
    pipeline = QDAPipeline()
    
    try:
        # Search Zenodo for up to 10 QDA files
        results = pipeline.run_scraper('zenodo', max_results=10, download=False)
        
        print(f"\nFound {len(results)} files")
        
        # Print details of first result
        if results:
            first = results[0]
            print("\nFirst result:")
            print(f"  Filename: {first.get('filename')}")
            print(f"  Software: {first.get('qda_software')}")
            print(f"  Title: {first.get('project_title')}")
            print(f"  DOI: {first.get('doi')}")
            print(f"  License: {first.get('license_type')}")
    
    finally:
        pipeline.close()


def example_search_and_download():
    """Example: Search and download files."""
    print("\n" + "=" * 60)
    print("Example 2: Search and download files")
    print("=" * 60)
    
    pipeline = QDAPipeline()
    
    try:
        # Search and download immediately
        results = pipeline.run_scraper('zenodo', max_results=5, download=True)
        
        print(f"\nSearched and downloaded {len(results)} files")
    
    finally:
        pipeline.close()


def example_export_metadata():
    """Example: Export metadata to CSV."""
    print("\n" + "=" * 60)
    print("Example 3: Export metadata to CSV")
    print("=" * 60)
    
    pipeline = QDAPipeline()
    
    try:
        # Export all metadata
        pipeline.export_metadata("example_export.csv")
        
        # Show statistics
        pipeline.print_statistics()
    
    finally:
        pipeline.close()


def example_custom_scraper():
    """Example: Use a custom scraper configuration."""
    print("\n" + "=" * 60)
    print("Example 4: Custom scraper usage")
    print("=" * 60)
    
    from scrapers import ZenodoScraper
    from database import MetadataDatabase
    
    # Create scraper directly
    scraper = ZenodoScraper()
    
    # Search with custom query
    results = scraper.search(query="qualitative interview", max_results=5)
    
    print(f"Found {len(results)} files matching 'qualitative interview'")
    
    # Save results to database
    db = MetadataDatabase()
    
    for file_meta in results:
        file_id = db.insert_file(file_meta)
        if file_id is None:
            print(f"  Skipped duplicate: {file_meta.get('filename')}")
        else:
            print(f"  Saved: {file_meta.get('filename')} (ID: {file_id})")
    
    db.close()


def example_download_pending():
    """Example: Download all pending files."""
    print("\n" + "=" * 60)
    print("Example 5: Download pending files")
    print("=" * 60)
    
    pipeline = QDAPipeline()
    
    try:
        # Download all files that were found but not yet downloaded
        pipeline.download_pending_files()
    
    finally:
        pipeline.close()


if __name__ == '__main__':
    print("QDA Archive Pipeline - Usage Examples")
    print("=" * 60)
    
    # Run examples
    # Uncomment the examples you want to run
    
    example_search_zenodo()
    # example_search_and_download()
    # example_export_metadata()
    # example_custom_scraper()
    # example_download_pending()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)

