# Seeding QDArchive

A comprehensive pipeline for discovering, collecting, and archiving Qualitative Data Analysis (QDA) files from open-access repositories across the web.

## Overview

This project automates the collection of QDA files (from software like MaxQDA, NVivo, ATLAS.ti, etc.) from various open-access data repositories. It includes:

- **Multi-repository scrapers** for Zenodo, Dryad, Dataverse, and more
- **Metadata extraction** with comprehensive tracking
- **Automated downloads** with integrity verification (MD5/SHA256)
- **SQLite database** for metadata management
- **CSV export** for data analysis

## Documentation

To keep the docs set small, the project now uses a minimal documentation structure:

- `README.md` - project overview, repository coverage, install, and quick start
- `scripts/README.md` - operational script usage and current search workflow
- `docs/SCRAPERS.md` - scraper architecture and implementation notes
- `docs/DATABASE.md` - SQLite metadata schema and database operations

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

**Total: 21 named repositories** across multiple countries and disciplines.

### API-Based Repositories (10)

1. **Zenodo** - https://zenodo.org/ (REST API)
2. **Dryad** - http://datadryad.org/ (REST API v2)
3. **Syracuse QDR** - https://qdr.syr.edu/ (Dataverse API)
4. **DANS** - https://dans.knaw.nl/ (OAI-PMH)
5. **DataverseNO** - https://dataverse.no/ (Dataverse API)
6. **ADA** - https://dataverse.ada.edu.au/ (Australian Data Archive - Dataverse API)
7. **Harvard Dataverse** - https://dataverse.harvard.edu/ (Dataverse API)
8. **AUSSDA** - https://data.aussda.at/ (Austrian Social Science Data Archive - Dataverse API)
9. **CESSDA** - https://datacatalogue.cessda.eu/ (European Social Science Data - REST API)
10. **ICPSR** - https://www.icpsr.umich.edu/ (Inter-university Consortium - Metadata API)

### Web/Site Repositories (11)

11. **UK Data Service** - https://ukdataservice.ac.uk/
12. **Qualidata Network** - https://www.qualidatanet.com/
13. **Qualiservice** - German qualitative data service
14. **QualiBi** - Qualitative data partner network
15. **FSD** - https://www.fsd.tuni.fi/ (Finnish Social Science Data Archive)
16. **SADA** - http://www.sada.nrf.ac.za/ (South African Data Archive)
17. **IHSN** - http://www.ihsn.org/ (International Household Survey Network)
18. **Sikt** - https://sikt.no/ (Norwegian Agency for Shared Services)
19. **Open Data Uni Halle** - https://opendata.uni-halle.de/
20. **Murray Research Archive** - https://www.murray.harvard.edu/
21. **Columbia Oral History** - https://library.columbia.edu/libraries/ccoh.html

Shared components such as `DataverseScraper` and `WebScraper` support multiple repositories internally, but they are not counted as separate named repositories.

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

### Quick Start: Search for QDA Files

**Recommended: Search Individual Repositories**

Use the dedicated search scripts in the `scripts/` folder. Each script searches with 158 queries (48 QDA extensions + 110 smart keywords):

```bash
# High-priority API-based repositories (most reliable)
python scripts/search_syracuse.py      # Syracuse QDR (~3 min)
python scripts/search_harvard.py       # Harvard Dataverse (~8 min)
python scripts/search_zenodo.py        # Zenodo (~13 min)
python scripts/search_dryad.py         # Dryad (~5 min)
python scripts/search_dans.py          # DANS Netherlands (~5 min)

# Additional API-based repositories
python scripts/search_ada.py           # ADA Australian
python scripts/search_aussda.py        # AUSSDA Austria
python scripts/search_cessda.py        # CESSDA
python scripts/search_icpsr.py         # ICPSR

# Web scraping repositories
python scripts/search_sikt.py          # Sikt Norway
python scripts/search_ukds.py          # UK Data Service
python scripts/search_fsd.py           # FSD Finland
# ... and 8 more (see scripts/README.md)
```

**Run the current shared batch set (5 repositories):**

```bash
python scripts/run_full_search.py      # Syracuse, Sikt, DataverseNO, Harvard, Zenodo
```

For full coverage, run the individual `scripts/search_*.py` files listed in `scripts/README.md`.

### Check Database Status

View current database contents and statistics:
```bash
python scripts/check_database.py
```

This shows:
- Total files found
- Files by repository
- QDA files vs other qualitative data
- Recent additions

### Download Files (Optional)

Download all files that were found:
```bash
python main.py download
```

Download from specific repository:
```bash
python main.py download --repository zenodo
```

### Export Metadata

Export all metadata to CSV:
```bash
python main.py export --output metadata.csv
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

The SQLite database now uses a **compatibility-first normalized design**.

- The existing `files` table is still the main operational table used by current scripts.
- Normalized project metadata is also written to:
  - `projects`
  - `keywords`
  - `person_role`
  - `licenses`
- Existing/older databases are backfilled automatically when opened.

In practice this means each saved search result can write:

- **File data**: filename, extension, download URL, path, hashes, status
- **Source data**: repository label, repository ID slug, source URL, source ID
- **Project data**: title, description, scope, authors, publication date, DOI
- **Normalized child data**: project keywords, people/roles, and raw license rows

The `files` table remains available for compatibility, while normalized tables support project-level analysis.

## Features

### Intelligent Scraping
- API-based scrapers for repositories with public APIs
- Web scraping for repositories without APIs
- Automatic QDA file detection by extension
- Rate limiting and retry logic

### Metadata Collection
- Comprehensive metadata extraction
- Raw license string preservation as provided by the source
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

The pipeline records license metadata as provided by each source and stores the raw license string in the database. Always verify license terms and access conditions yourself before using downloaded data.

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
