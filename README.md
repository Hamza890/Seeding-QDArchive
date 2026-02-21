# Seeding QDArchive

A comprehensive pipeline for discovering, collecting, and archiving Qualitative Data Analysis (QDA) files from open-access repositories across the web.

## Overview

This project automates the collection of QDA files (from software like MaxQDA, NVivo, ATLAS.ti, etc.) from various open-access data repositories. It includes:

- **Multi-repository scrapers** for Zenodo, Dryad, Dataverse, and more
- **Metadata extraction** with comprehensive tracking
- **Automated downloads** with integrity verification (MD5/SHA256)
- **SQLite database** for metadata management
- **CSV export** for data analysis

## Supported QDA Software

The pipeline searches for files from these QDA software packages:

- **REFI-QDA** (.qdpx, .qdc)
- **MaxQDA** (.mqda, .mx24, .mx22, .mx20, etc.)
- **NVivo** (.nvp, .nvpx)
- **ATLAS.ti** (.atlasproj, .hpr7)
- **QDA Miner** (.ppj, .pprj, .qlt)
- **f4analyse** (.f4p)
- **Quirkos** (.qpd)

## Supported Data Repositories

- **Zenodo** - https://zenodo.org/ (API-based)
- **Dryad** - http://datadryad.org/ (API-based)
- **DataverseNO** - https://dataverse.no/ (API-based)
- **DANS** - https://dans.knaw.nl/ (OAI-PMH protocol)
- **Syracuse QDR** - https://qdr.syr.edu/ (Dataverse API)
- **UK Data Service** - https://ukdataservice.ac.uk/ (Web scraping)
- **Qualidata Network** - https://www.qualidatanet.com/ (Web scraping)
- **Qualiservice** - German qualitative data service (Web scraping)
- **QualiBi** - Qualitative data partner network (Web scraping)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://gitlab.rrze.fau.de/yz63yxuh/seeding-qdarchive.git
cd seeding-qdarchive
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The pipeline provides a command-line interface with several commands:

### Search for QDA Files

Search all repositories:
```bash
python main.py search --scraper all --max-results 50
```

Search a specific repository:
```bash
# Zenodo
python main.py search --scraper zenodo --max-results 100

# DANS (Netherlands)
python main.py search --scraper dans --max-results 50

# Syracuse QDR
python main.py search --scraper syracuse_qdr --max-results 50

# UK Data Service
python main.py search --scraper uk_data_service --max-results 30

# Qualidata Network
python main.py search --scraper qualidata --max-results 20
```

Search with custom query:
```bash
python main.py search --scraper zenodo --query "interview data" --max-results 50
```

Search and download immediately:
```bash
python main.py search --scraper all --max-results 50 --download
```

### Download Pending Files

Download all files that were found but not yet downloaded:
```bash
python main.py download
```

### Export Metadata

Export all metadata to CSV:
```bash
python main.py export --output metadata.csv
```

Export with filters:
```bash
python main.py export --output completed.csv --filter-status completed
python main.py export --output zenodo_files.csv --filter-repository Zenodo
```

### View Statistics

Show archive statistics:
```bash
python main.py stats
```

## Project Structure

```
seeding-qdarchive/
├── config/
│   ├── qda_extensions.json      # QDA file extensions configuration
│   └── data_sources.json        # Data repository configurations
├── src/
│   ├── database.py              # SQLite database management
│   ├── download_manager.py      # File download with verification
│   ├── pipeline.py              # Main pipeline orchestrator
│   └── scrapers/
│       ├── base_scraper.py      # Base scraper class
│       ├── zenodo_scraper.py    # Zenodo API scraper
│       ├── dryad_scraper.py     # Dryad API scraper
│       ├── dataverse_scraper.py # Dataverse API scraper
│       └── web_scraper.py       # Generic web scraper
├── Datasets/                    # Sample datasets
├── downloads/                   # Downloaded QDA files (created automatically)
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Database Schema

The SQLite database stores comprehensive metadata for each file:

- **File Information**: filename, extension, size, path, hashes (MD5/SHA256)
- **Source Information**: repository, URL, source ID
- **License Information**: license type and URL
- **Project Metadata**: title, description, scope, authors, keywords
- **Additional Metadata**: DOI, version, language, publication date
- **Download Status**: pending, completed, failed

## Features

### Intelligent Scraping
- API-based scrapers for repositories with public APIs
- Web scraping for repositories without APIs
- Automatic QDA file detection by extension
- Rate limiting and retry logic

### Metadata Collection
- Comprehensive metadata extraction
- License verification (only open-license files)
- Author and keyword tracking
- DOI and version information

### Download Management
- Chunked streaming downloads
- MD5 and SHA256 hash verification
- Automatic retry on failure
- Organized storage by repository

### Data Export
- CSV export for analysis
- Filtering by status or repository
- Complete metadata preservation

## Configuration

### Adding New QDA Extensions

Edit `config/qda_extensions.json` to add new file extensions:

```json
{
  "qda_software": {
    "NewSoftware": {
      "website": "https://example.com",
      "extensions": [".new", ".ext"]
    }
  }
}
```

### Adding New Repositories

Edit `config/data_sources.json` to add new repositories:

```json
{
  "repositories": {
    "new_repo": {
      "name": "New Repository",
      "url": "https://example.com",
      "api_url": "https://api.example.com",
      "type": "api"
    }
  }
}
```

## License Compliance

This pipeline only collects files with **open licenses**. The scrapers attempt to verify license information and record it in the database. Always verify license compliance before using downloaded data.

## Contributing

Contributions are welcome! Areas for improvement:

- Additional repository scrapers
- Enhanced metadata extraction
- Better license detection
- Performance optimizations
- Documentation improvements

## Acknowledgments

- REFI-QDA for QDA software standards
- All open-access repositories for making research data available
- The qualitative research community

## Project Status

Active development. The pipeline is functional and ready for use.
