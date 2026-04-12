# Seeding QDArchive

A pipeline for discovering, collecting, and archiving Qualitative Data Analysis (QDA) files from research data repositories.

## Overview

This project automates the collection of QDA file metadata (from software like MaxQDA, NVivo, ATLAS.ti, etc.) from research data repositories. It includes:

- **Multi-repository scrapers** for ICPSR, UK Data Service, Zenodo, Harvard Dataverse, and more — using the DataCite REST API and repository-specific APIs
- **Metadata extraction** with comprehensive tracking per project and file
- **SQLite database** (`23101748-sq26.db`) — committed to the repo, currently holding **13,108 records** from ICPSR and UK Data Service
- **Organised download tool** (`scripts/download_files.py`) — downloads files or generates `links.txt` landing-page references, organised as `downloads/<Repository>/<Project>/`
- **CSV export** for data analysis

## Current Database State

| Repository | Records | Access |
|---|---|---|
| ICPSR | 10,469 | Login required → `links.txt` |
| UK Data Service | 2,639 | Login required → `links.txt` |
| **Total** | **13,108** | |

The database (`23101748-sq26.db`, ~89 MB) is committed directly to this repository and is ready to use without running any scrapers.

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

Scripts exist for **21 named repositories**. The two primary repositories — ICPSR and UK Data Service — are fully harvested via the **DataCite public API** and their records are included in the committed database.

### Primary Repositories (fully harvested, in database)

| Repository | Records | API |
|---|---|---|
| **ICPSR** — https://www.icpsr.umich.edu/ | 10,469 | DataCite REST API |
| **UK Data Service** — https://ukdataservice.ac.uk/ | 2,639 | DataCite REST API |

### Additional Repositories (scrapers available, not in current database)

**API-Based:**
- **Zenodo** — https://zenodo.org/ (REST API)
- **Dryad** — http://datadryad.org/ (REST API v2)
- **Syracuse QDR** — https://qdr.syr.edu/ (Dataverse API)
- **DANS** — https://dans.knaw.nl/ (OAI-PMH)
- **DataverseNO** — https://dataverse.no/ (Dataverse API)
- **ADA** — https://dataverse.ada.edu.au/ (Dataverse API)
- **Harvard Dataverse** — https://dataverse.harvard.edu/ (Dataverse API)
- **AUSSDA** — https://data.aussda.at/ (Dataverse API)
- **CESSDA** — https://datacatalogue.cessda.eu/ (REST API)

**Web/Site Scrapers:**
- Sikt (Norway), FSD (Finland), Qualidata, Qualiservice, QualiBi, SADA, IHSN, Open Data Halle, Murray Archive, Columbia Oral History

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

### 1. Use the Committed Database (no scraping needed)

The repository includes `23101748-sq26.db` with **13,108 records** already harvested from ICPSR and UK Data Service. You can query or export it immediately without running any scrapers:

```bash
python scripts/check_database.py
```

### 2. Generate Download Links for ICPSR / UK Data Service

ICPSR and UKDS require a free account and data-access agreement. The download script creates a `downloads/` folder with `links.txt` files per project containing the landing page URL and DOI:

```bash
# Generate links.txt files for ICPSR and UK Data Service
python scripts/download_files.py --repos ICSPR UKDataService
```

Output structure:
```
downloads/
├── ICSPR/
│   └── <Project Title>/
│       └── links.txt   ← landing page URL + DOI (login required)
└── UKDataService/
    └── <Project Title>/
        └── links.txt
```

### 3. Download Files from Open-Access Repositories

For repositories with direct download links (Zenodo, Harvard Dataverse, SyracuseQDR), the script downloads files automatically:

```bash
# Download from all directly-downloadable repositories
python scripts/download_files.py --repos Zenodo "Harvard Dataverse" SyracuseQDR

# Custom output folder
python scripts/download_files.py --output C:\my_qda_files

# All repos at once (links.txt for controlled, files for open-access)
python scripts/download_files.py
```

### 4. Run Scrapers to Harvest Additional Repositories

To extend the database with records from other repositories, run the individual search scripts:

```bash
# Primary (already in DB — re-run to refresh)
python scripts/search_icpsr.py         # ICPSR via DataCite API (~10 min)
python scripts/search_ukds.py          # UK Data Service via DataCite API (~6 min)

# Other API-based repositories
python scripts/search_zenodo.py        # Zenodo (~13 min)
python scripts/search_harvard.py       # Harvard Dataverse (~8 min)
python scripts/search_syracuse.py      # Syracuse QDR (~3 min)
python scripts/search_dans.py          # DANS Netherlands (~5 min)
python scripts/search_dryad.py         # Dryad (~5 min)
# ... and more (see scripts/README.md)
```

### Check Database Status

```bash
python scripts/check_database.py
```

## Project Structure

```
seeding-qdarchive/
├── config/
│   ├── qda_extensions.json      # QDA file extensions configuration
│   └── data_sources.json        # Data repository configurations
├── docs/
│   ├── DATABASE.md              # SQLite schema and database operations
│   └── SCRAPERS.md              # Scraper architecture and notes
├── src/
│   ├── database.py              # SQLite database management
│   ├── download_manager.py      # File download with verification
│   ├── pipeline.py              # Main pipeline orchestrator
│   └── scrapers/
│       ├── base_scraper.py      # Base scraper class
│       ├── icpsr_scraper.py     # ICPSR via DataCite API
│       ├── ukds_scraper.py      # UK Data Service via DataCite API
│       ├── zenodo_scraper.py    # Zenodo API scraper
│       ├── dataverse_scraper.py # Dataverse API scraper (Harvard, SyracuseQDR, etc.)
│       └── ...                  # Other repository scrapers
├── scripts/
│   ├── download_files.py        # Download files / generate links.txt per project
│   ├── search_icpsr.py          # Harvest ICPSR via DataCite
│   ├── search_ukds.py           # Harvest UK Data Service via DataCite
│   ├── search_zenodo.py         # Harvest Zenodo
│   ├── check_database.py        # Inspect database contents
│   └── ...                      # One script per repository
├── downloads/                   # Output folder (repo → project → files / links.txt)
├── 23101748-sq26.db             # SQLite database (13,108 records, committed to repo)
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
