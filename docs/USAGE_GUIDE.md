# Complete Usage Guide

This guide covers all features and usage patterns of the QDA Archive Pipeline.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Advanced Usage](#advanced-usage)
4. [Programmatic Usage](#programmatic-usage)
5. [Maintenance](#maintenance)
6. [Troubleshooting](#troubleshooting)

## Installation

### Step 1: Clone Repository

```bash
git clone https://gitlab.rrze.fau.de/yz63yxuh/seeding-qdarchive.git
cd seeding-qdarchive
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
python test_setup.py
```

You should see all tests pass.

## Basic Usage

### Search for Files

#### Search All Repositories

```bash
python main.py search --scraper all --max-results 50
```

#### Search Specific Repository

```bash
# API-based repositories
python main.py search --scraper zenodo --max-results 100
python main.py search --scraper dryad --max-results 50
python main.py search --scraper syracuse_qdr --max-results 50
python main.py search --scraper dans --max-results 50
python main.py search --scraper dataverse_no --max-results 50
python main.py search --scraper ada --max-results 50
python main.py search --scraper harvard_dataverse --max-results 50
python main.py search --scraper aussda --max-results 50
python main.py search --scraper cessda --max-results 50
python main.py search --scraper icpsr --max-results 50

# Web scraping repositories
python main.py search --scraper uk_data_service --max-results 30
python main.py search --scraper qualidata --max-results 20
python main.py search --scraper fsd --max-results 30
python main.py search --scraper sada --max-results 30
python main.py search --scraper ihsn --max-results 30
python main.py search --scraper databrary --max-results 20
python main.py search --scraper sikt --max-results 30
python main.py search --scraper opendata_halle --max-results 30
python main.py search --scraper cis_spain --max-results 30
python main.py search --scraper murray --max-results 30
python main.py search --scraper columbia_oral_history --max-results 30
```

#### Search with Custom Query

```bash
python main.py search --scraper zenodo --query "qualitative interview" --max-results 30
```

### Download Files

#### Download Pending Files

```bash
python main.py download
```

This downloads all files that were found but not yet downloaded.

#### Search and Download Immediately

```bash
python main.py search --scraper zenodo --max-results 20 --download
```

### Export Metadata

#### Export All Metadata

```bash
python main.py export --output metadata.csv
```

#### Export with Filters

```bash
# Only completed downloads
python main.py export --output completed.csv --filter-status completed

# Only Zenodo files
python main.py export --output zenodo.csv --filter-repository Zenodo

# Only failed downloads
python main.py export --output failed.csv --filter-status failed
```

### View Statistics

```bash
python main.py stats
```

Shows:
- Total files in database
- Files by status (pending/completed/failed)
- Files by repository
- Files by extension

## Advanced Usage

### Custom Scraper Configuration

Create a custom scraper for a new repository:

```python
from scrapers.base_scraper import BaseScraper

class MyCustomScraper(BaseScraper):
    def search(self, query=None, max_results=100, **kwargs):
        # Your search logic
        for file_data in found_files:
            if self.is_qda_file(file_data['filename']):
                metadata = self.normalize_metadata(file_data)
                self.results.append(metadata)
        return self.results
    
    def get_file_metadata(self, file_id):
        # Get metadata for specific file
        return {}
```

### Batch Processing

Process multiple searches in sequence:

```bash
# Create a batch script
python main.py search --scraper zenodo --max-results 100
python main.py search --scraper dryad --max-results 100
python main.py download
python main.py export --output batch_results.csv
```

### Filtering and Analysis

Use Python to analyze the database:

```python
from database import MetadataDatabase

db = MetadataDatabase()

# Get all NVivo files
nvivo_files = [f for f in db.get_all_files() 
               if f.get('qda_software') == 'NVivo']

# Get files by license
cc0_files = [f for f in db.get_all_files() 
             if f.get('license_type') == 'CC0-1.0']

# Get files from 2024
recent_files = [f for f in db.get_all_files() 
                if f.get('publication_date', '').startswith('2024')]

db.close()
```

## Programmatic Usage

### Basic Pipeline Usage

```python
from pipeline import QDAPipeline

# Initialize pipeline
pipeline = QDAPipeline()

# Search Zenodo
results = pipeline.run_scraper('zenodo', max_results=50)

# Download files
pipeline.download_pending_files()

# Export metadata
pipeline.export_metadata('output.csv')

# Get statistics
stats = pipeline.db.get_statistics()
print(f"Total files: {stats['total_files']}")

# Clean up
pipeline.close()
```

### Direct Scraper Usage

```python
from scrapers import ZenodoScraper
from database import MetadataDatabase

# Create scraper
scraper = ZenodoScraper()

# Search with custom parameters
results = scraper.search(
    query="qualitative research",
    max_results=100,
    page_size=50
)

# Save to database
db = MetadataDatabase()
for file_meta in results:
    file_id = db.insert_file(file_meta)
    print(f"Saved: {file_meta['filename']} (ID: {file_id})")

db.close()
```

### Custom Download Logic

```python
from download_manager import DownloadManager
from database import MetadataDatabase

dm = DownloadManager(download_dir="custom_downloads")
db = MetadataDatabase()

# Get specific files
files = db.get_all_files({'qda_software': 'MaxQDA'})

for file_meta in files:
    if file_meta.get('download_url'):
        result = dm.download_file(
            url=file_meta['download_url'],
            filename=file_meta['filename'],
            subfolder='maxqda_files'
        )
        
        if result['success']:
            db.update_file(file_meta['id'], {
                'download_status': 'completed',
                'file_path': result['file_path']
            })

db.close()
```

## Maintenance

### Verify Archive Integrity

```bash
# Verify all downloaded files
python utils/verify_archive.py --verify

# Check database integrity
python utils/verify_archive.py --check-db

# Clean failed downloads
python utils/verify_archive.py --clean

# Run all checks
python utils/verify_archive.py --all
```

### Backup Database

```bash
# Simple copy
cp qda_archive.db backups/qda_archive_$(date +%Y%m%d).db

# Or use SQLite backup
sqlite3 qda_archive.db ".backup backups/qda_archive_backup.db"
```

### Clean Up

```python
from database import MetadataDatabase
from pathlib import Path

db = MetadataDatabase()

# Remove duplicate entries
# (Keep first occurrence of each filename)
all_files = db.get_all_files()
seen = set()
for f in all_files:
    filename = f['filename']
    if filename in seen:
        # This is a duplicate
        db.update_file(f['id'], {'download_status': 'duplicate'})
    else:
        seen.add(filename)

db.close()
```

## Troubleshooting

### No Files Found

**Problem**: Scraper returns no results

**Solutions**:
1. Try different search queries
2. Check repository is accessible
3. Verify API endpoints are working
4. Try different repositories

### Download Failures

**Problem**: Files fail to download

**Solutions**:
1. Check internet connection
2. Verify download URL is accessible
3. Check if file requires authentication
4. Look at error message in database
5. Try manual download to test URL

### Database Locked

**Problem**: "Database is locked" error

**Solutions**:
1. Close other programs accessing the database
2. Only run one pipeline instance at a time
3. Check for zombie processes

### Import Errors

**Problem**: Module not found errors

**Solutions**:
1. Verify dependencies installed: `pip install -r requirements.txt`
2. Check Python version (3.8+)
3. Verify you're in correct directory

### Memory Issues

**Problem**: Out of memory with large downloads

**Solutions**:
1. Reduce `max_results` parameter
2. Download in batches
3. Use `--download` flag sparingly

## Best Practices

1. **Start Small**: Begin with `--max-results 10` to test
2. **Verify Licenses**: Always check license information
3. **Regular Backups**: Backup database regularly
4. **Monitor Progress**: Use `stats` command frequently
5. **Verify Downloads**: Run verification after downloads
6. **Document Queries**: Keep track of search queries used
7. **Export Regularly**: Export metadata for analysis

## Performance Tips

1. **Batch Operations**: Search first, download later
2. **Use Filters**: Export only needed data
3. **Index Usage**: Database is indexed for fast queries
4. **Rate Limiting**: Built-in delays prevent API blocks
5. **Parallel Scrapers**: Run different scrapers separately

## Getting Help

- Check documentation in `docs/` directory
- Review examples in `examples/` directory
- Run `python main.py --help` for CLI help
- Check PROJECT_SUMMARY.md for overview

