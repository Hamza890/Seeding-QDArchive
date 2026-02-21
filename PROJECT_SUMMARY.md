# QDA Archive Pipeline - Project Summary

## Project Overview

The QDA Archive Pipeline is a comprehensive, automated system for discovering, collecting, and archiving Qualitative Data Analysis (QDA) files from open-access repositories worldwide. The pipeline supports multiple QDA software formats and data repositories, with built-in metadata tracking and integrity verification.

## Key Features

### 1. Multi-Repository Support
- **Zenodo**: General-purpose open-access repository
- **Dryad**: Curated research data repository
- **DataverseNO**: Norwegian Dataverse network
- **UK Data Service**: UK's largest data collection
- **Syracuse QDR**: Dedicated qualitative data repository
- **Extensible**: Easy to add new repositories

### 2. QDA Software Coverage
Supports 40+ file extensions from major QDA software:
- REFI-QDA Standard (.qdpx, .qdc)
- MaxQDA (.mqda, .mx24, .mx22, etc.)
- NVivo (.nvp, .nvpx)
- ATLAS.ti (.atlasproj, .hpr7)
- QDA Miner (.ppj, .pprj, .qlt)
- f4analyse (.f4p)
- Quirkos (.qpd)

### 3. Comprehensive Metadata Tracking
- File information (name, size, extension, hashes)
- Source information (repository, URL, ID)
- License information (type, URL)
- Project metadata (title, description, authors, keywords)
- Additional metadata (DOI, version, publication date)
- Download status tracking

### 4. Robust Download Management
- Streaming downloads with chunked transfer
- MD5 and SHA256 hash verification
- Automatic retry with exponential backoff
- Organized storage by repository
- Error tracking and reporting

### 5. Data Export and Analysis
- CSV export for metadata analysis
- Filtering by status or repository
- Statistical summaries
- Database integrity verification

## Project Structure

```
seeding-qdarchive/
├── config/                      # Configuration files
│   ├── qda_extensions.json     # QDA file extensions
│   └── data_sources.json       # Repository configurations
├── src/                        # Source code
│   ├── database.py            # SQLite database management
│   ├── download_manager.py    # File download utilities
│   ├── pipeline.py            # Main pipeline orchestrator
│   └── scrapers/              # Repository scrapers
│       ├── base_scraper.py    # Base scraper class
│       ├── zenodo_scraper.py  # Zenodo API scraper
│       ├── dryad_scraper.py   # Dryad API scraper
│       ├── dataverse_scraper.py # Dataverse API scraper
│       └── web_scraper.py     # Generic web scraper
├── docs/                       # Documentation
│   ├── DATABASE.md            # Database schema docs
│   └── SCRAPERS.md            # Scraper documentation
├── examples/                   # Usage examples
│   └── basic_usage.py         # Example scripts
├── utils/                      # Utility scripts
│   └── verify_archive.py      # Archive verification
├── main.py                     # CLI entry point
├── test_setup.py              # Setup verification
├── requirements.txt           # Python dependencies
├── README.md                  # Main documentation
└── QUICKSTART.md              # Quick start guide
```

## Technical Architecture

### Scraper Layer
- **API-based scrapers**: Use official REST APIs (Zenodo, Dryad, Dataverse)
- **Web scrapers**: Parse HTML for repositories without APIs
- **Base scraper**: Common functionality and metadata normalization

### Core Pipeline
- **QDAPipeline**: Orchestrates all scrapers and operations
- **DownloadManager**: Handles file downloads with verification
- **MetadataDatabase**: SQLite database for metadata storage

### User Interfaces
- **Command-line interface**: Full-featured CLI with subcommands
- **Python API**: Programmatic access for custom workflows

## Usage Examples

### Command Line

```bash
# Search all repositories
python main.py search --scraper all --max-results 50

# Download pending files
python main.py download

# Export metadata
python main.py export --output metadata.csv

# View statistics
python main.py stats
```

### Python API

```python
from pipeline import QDAPipeline

pipeline = QDAPipeline()
results = pipeline.run_scraper('zenodo', max_results=100)
pipeline.export_metadata('output.csv')
pipeline.close()
```

## Database Schema

SQLite database with comprehensive metadata:
- 30+ fields per file
- Indexed for fast queries
- CSV export capability
- Statistics generation

## Quality Assurance

### Data Integrity
- MD5 and SHA256 hash verification
- Download status tracking
- Error message logging
- Verification utilities

### License Compliance
- License type tracking
- License URL recording
- Open-license focus

### Code Quality
- Modular architecture
- Comprehensive error handling
- Rate limiting for APIs
- Retry logic for failures

## Performance Characteristics

- **Scalability**: Handles thousands of files
- **Rate limiting**: Respects repository limits
- **Efficient storage**: Organized by repository
- **Fast queries**: Indexed database fields

## Extensibility

### Adding New Scrapers
1. Inherit from `BaseScraper`
2. Implement `search()` and `get_file_metadata()`
3. Use helper methods for QDA file detection
4. Register in pipeline

### Adding New QDA Extensions
1. Edit `config/qda_extensions.json`
2. Add software name and extensions
3. Automatic detection in all scrapers

### Adding New Repositories
1. Edit `config/data_sources.json`
2. Create scraper (API or web-based)
3. Add to pipeline initialization

## Testing and Verification

- **Setup test**: `python test_setup.py`
- **Archive verification**: `python utils/verify_archive.py --all`
- **Example scripts**: `python examples/basic_usage.py`

## Dependencies

- **requests**: HTTP client for API calls
- **beautifulsoup4**: HTML parsing for web scraping
- **lxml**: XML/HTML parser
- **sqlite3**: Built-in database (no install needed)

## Future Enhancements

Potential areas for expansion:
- Additional repository scrapers (DANS, more Dataverse instances)
- Enhanced license detection
- Parallel downloads
- Web interface
- API rate limit optimization
- Machine learning for metadata extraction
- Duplicate detection
- File format validation

## License Compliance

The pipeline is designed to collect only openly-licensed data. All scrapers attempt to extract and record license information. Users should verify license compliance before using downloaded data.

## Use Cases

1. **Research**: Build datasets of QDA files for analysis
2. **Archiving**: Create backups of open qualitative data
3. **Discovery**: Find QDA files for specific research topics
4. **Metadata analysis**: Study trends in qualitative research
5. **Format preservation**: Archive files in various QDA formats

## Success Metrics

- Number of repositories supported: 5+
- QDA software formats: 9+
- File extensions recognized: 40+
- Metadata fields tracked: 30+
- Lines of code: ~2000+

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Test setup: `python test_setup.py`
3. Run first search: `python main.py search --scraper zenodo --max-results 10`
4. View results: `python main.py stats`
5. Read QUICKSTART.md for more examples

## Documentation

- **README.md**: Main documentation and overview
- **QUICKSTART.md**: Quick start guide with examples
- **docs/DATABASE.md**: Database schema documentation
- **docs/SCRAPERS.md**: Scraper implementation details
- **PROJECT_SUMMARY.md**: This file

## Support and Contribution

The project is designed to be:
- **Easy to understand**: Clear code structure and documentation
- **Easy to extend**: Modular architecture with base classes
- **Easy to use**: Both CLI and Python API
- **Well-documented**: Comprehensive documentation

## Conclusion

The QDA Archive Pipeline provides a robust, extensible solution for collecting and archiving qualitative data analysis files from open-access repositories. With support for multiple repositories and QDA software formats, comprehensive metadata tracking, and built-in verification, it serves as a solid foundation for building a qualitative data archive.

