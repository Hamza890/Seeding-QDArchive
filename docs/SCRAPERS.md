# Scraper Documentation

This document provides detailed information about each scraper in the QDA Archive pipeline.

## Overview

The pipeline includes scrapers for different types of repositories:

1. **API-based scrapers**: Use official APIs (Zenodo, Dryad, Dataverse)
2. **Web scrapers**: Parse HTML for repositories without APIs (UK Data Service, etc.)

## Zenodo Scraper

**Repository**: https://zenodo.org/  
**Type**: API-based  
**API Documentation**: https://developers.zenodo.org/

### Features
- Searches using Zenodo REST API
- Supports pagination
- Extracts comprehensive metadata including DOI, authors, keywords
- Handles multiple file formats per record

### Usage
```python
from scrapers import ZenodoScraper

scraper = ZenodoScraper()
results = scraper.search(max_results=100)
```

### Metadata Extracted
- Filename and extension
- File size
- Download URL
- DOI
- License information
- Authors
- Publication date
- Keywords
- Project title and description

### Rate Limiting
- 1 second delay between page requests
- Respects Zenodo's rate limits

## Dryad Scraper

**Repository**: http://datadryad.org/  
**Type**: API-based  
**API Documentation**: https://datadryad.org/api/v2/docs/

### Features
- Uses Dryad API v2
- Searches datasets and extracts files
- Default license: CC0-1.0 (Dryad standard)

### Usage
```python
from scrapers import DryadScraper

scraper = DryadScraper()
results = scraper.search(query="qualitative data", max_results=50)
```

### Notes
- Dryad requires two API calls per dataset (metadata + files)
- 0.5 second delay between file requests
- Most Dryad datasets use CC0-1.0 license

## Dataverse Scraper

**Repository**: Multiple Dataverse instances  
**Type**: API-based  
**API Documentation**: https://guides.dataverse.org/en/latest/api/

### Features
- Works with any Dataverse installation
- Configurable base URL
- Supports DataverseNO, Harvard Dataverse, etc.

### Usage
```python
from scrapers import DataverseScraper

# DataverseNO
scraper = DataverseScraper(base_url="https://dataverse.no")
results = scraper.search(max_results=50)

# Harvard Dataverse
scraper = DataverseScraper(base_url="https://dataverse.harvard.edu")
results = scraper.search(max_results=50)
```

### Metadata Extracted
- Complete citation metadata
- Author information
- Keywords
- Persistent identifiers (DOI)
- License information
- File-level metadata

### Notes
- Requires two API calls per dataset
- Different Dataverse instances may have different metadata schemas

## Web Scraper

**Type**: HTML parsing  
**Used for**: Repositories without public APIs

### Features
- Recursive crawling with depth limit
- Automatic QDA file detection
- Same-domain restriction for safety
- Rate limiting (0.5s between requests)

### Usage
```python
from scrapers import WebScraper

scraper = WebScraper(
    base_url="https://ukdataservice.ac.uk/learning-hub/qualitative-data/",
    repository_name="UK Data Service"
)
results = scraper.search(max_depth=2, max_results=50)
```

### Limitations
- Cannot extract detailed metadata
- Depends on website structure
- May miss files behind authentication
- License information not available

### Configuration
- `max_depth`: How deep to crawl (default: 2)
- `max_results`: Maximum files to find
- Only crawls same domain as base URL

## Creating Custom Scrapers

All scrapers inherit from `BaseScraper`. To create a new scraper:

```python
from scrapers.base_scraper import BaseScraper

class MyCustomScraper(BaseScraper):
    def __init__(self, config_path="config/qda_extensions.json"):
        super().__init__(config_path)
        # Your initialization
    
    def search(self, query=None, max_results=100, **kwargs):
        # Implement search logic
        # Use self.is_qda_file() to check extensions
        # Use self.normalize_metadata() to format results
        return self.results
    
    def get_file_metadata(self, file_id):
        # Implement metadata retrieval
        return {}
```

### Required Methods
- `search()`: Search for QDA files
- `get_file_metadata()`: Get metadata for specific file

### Helper Methods (from BaseScraper)
- `is_qda_file(filename)`: Check if file has QDA extension
- `get_qda_software(filename)`: Determine QDA software from extension
- `normalize_metadata(raw_metadata)`: Convert to standard format

## Metadata Schema

All scrapers normalize metadata to this schema:

```python
{
    'filename': str,
    'file_extension': str,
    'file_size': int,
    'download_url': str,
    'source_repository': str,
    'source_url': str,
    'source_id': str,
    'license_type': str,
    'license_url': str,
    'project_title': str,
    'project_description': str,
    'authors': str,  # Semicolon-separated
    'publication_date': str,
    'keywords': str,  # Semicolon-separated
    'doi': str,
    'version': str,
    'qda_software': str
}
```

## Best Practices

1. **Rate Limiting**: Always include delays between requests
2. **Error Handling**: Catch and log API errors gracefully
3. **Metadata Validation**: Verify required fields are present
4. **License Checking**: Only collect openly licensed files
5. **User Agent**: Identify your bot in the User-Agent header

## Troubleshooting

### No results found
- Check if repository API is accessible
- Verify search query syntax
- Check rate limits

### Incomplete metadata
- Some repositories have sparse metadata
- Web scrapers have limited metadata extraction
- Check source repository directly

### Download failures
- Verify download URLs are accessible
- Check if authentication is required
- Verify file still exists in repository

