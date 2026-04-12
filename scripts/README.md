# QDA Archive Scripts

This folder contains scripts for harvesting, inspecting, and downloading QDA files across multiple repositories.

## Current Status

- **Database**: `23101748-sq26.db` — **13,108 records** (10,469 ICPSR + 2,639 UK Data Service), committed to the repo
- **21 named repository scripts** in `scripts/search_*.py`
- **ICPSR and UKDS** scrapers use the **DataCite public REST API** (no login required to harvest metadata)
- Shared components: `DataverseScraper`, `WebScraper`
- Rule of thumb: each `search_*.py` script imports and instantiates its matching scraper class

## 📁 Files Overview

### Individual Repository Scripts (21 total)

**API-Based Repositories (10):**
- `search_syracuse.py` - Syracuse QDR (1.0s delay)
- `search_harvard.py` - Harvard Dataverse (3.0s delay)
- `search_dataverseno.py` - DataverseNO (2.0s delay)
- `search_ada.py` - ADA Australian (2.0s delay)
- `search_aussda.py` - AUSSDA Austria (2.0s delay)
- `search_dans.py` - DANS Netherlands (2.0s delay)
- `search_zenodo.py` - Zenodo (5.0s delay)
- `search_dryad.py` - Dryad (2.0s delay)
- `search_cessda.py` - CESSDA (2.5s delay)
- `search_icpsr.py` - ICPSR (2.5s delay)

**Web/Site Repositories (11):**
- `search_sikt.py` - Sikt Norway (1.5s delay)
- `search_ukds.py` - UK Data Service (2.0s delay)
- `search_fsd.py` - FSD Finland (2.0s delay)
- `search_qualidata.py` - Qualidata (2.0s delay)
- `search_qualiservice.py` - Qualiservice (2.0s delay)
- `search_qualibi.py` - QualiBi (2.0s delay)
- `search_sada.py` - SADA South Africa (2.0s delay)
- `search_ihsn.py` - IHSN (2.0s delay)
- `search_opendatahalle.py` - Open Data Halle (2.0s delay)
- `search_murray.py` - Murray Archive (2.0s delay)
- `search_columbia.py` - Columbia Oral History (2.0s delay)

### Batch Scripts
- **`run_full_search.py`** - Search the current 5-repository batch set with all queries
- **`run_priority_search.py`** - Search the current 5-repository batch set with priority queries only

Shared generic components:
- `DataverseScraper` - used for Dataverse-based integrations such as DataverseNO
- `WebScraper` - shared support class for web/site scrapers

Examples of direct script-to-scraper mapping:
- `search_syracuse.py` -> `SyracuseQDRScraper`
- `search_harvard.py` -> `HarvardDataverseScraper`
- `search_dataverseno.py` -> `DataverseScraper`
- `search_zenodo.py` -> `ZenodoScraper`
- the rest follow the same one-script / one-scraper pattern

### Utility Scripts
- **`check_database.py`** — Inspect current database contents and record counts
- **`download_files.py`** — Download files or generate `links.txt` per project, organised as `downloads/<Repository>/<Project>/`

## 🚀 Usage

### Check What's Already in the Database

```bash
python scripts/check_database.py
```

### Generate Landing-Page Links for ICPSR / UK Data Service

ICPSR and UKDS require a free account and data-access agreement. The script creates one `links.txt` per project with the landing page URL and DOI:

```bash
python scripts/download_files.py --repos ICSPR UKDataService
```

Output: `downloads/ICSPR/<Project>/links.txt` and `downloads/UKDataService/<Project>/links.txt`

### Download Files from Open-Access Repositories

```bash
# Specific repos with direct URLs
python scripts/download_files.py --repos Zenodo "Harvard Dataverse" SyracuseQDR

# Everything at once
python scripts/download_files.py

# Custom output folder
python scripts/download_files.py --output C:\my_qda_files
```

### Harvest Metadata from Repositories (extends the database)

```bash
# Primary repositories (already in DB — re-run to refresh)
python scripts/search_icpsr.py         # ICPSR via DataCite (~10 min)
python scripts/search_ukds.py          # UK Data Service via DataCite (~6 min)

# Other repositories
python scripts/search_zenodo.py        # Zenodo (~13 min)
python scripts/search_harvard.py       # Harvard Dataverse (~8 min)
python scripts/search_syracuse.py      # Syracuse QDR (~3 min)
python scripts/search_dans.py          # DANS Netherlands (~5 min)
python scripts/search_dryad.py         # Dryad (~5 min)
python scripts/search_ada.py
python scripts/search_aussda.py
python scripts/search_sikt.py
# ... etc (see full list above)
```

### Run the 5-Repository Batch Set

```bash
python scripts/run_full_search.py
```

For full archive coverage, run the individual repository scripts listed above.

## 📊 Search Configuration

Each script searches with:
- **186 unique queries** (48 QDA software extensions + ~138 qualitative-methods keywords)
- **Unlimited results** — paginates until the API returns no more pages (ICPSR/UKDS use the DataCite API; results are exhaustive)
- **2.0 s courtesy delay** between queries (prevents rate-limiting; does not affect total records returned)
- **Automatic file-level deduplication**
- **Progress checkpoints** (saves every 25 queries)
- **Error handling** (continues on failures)

When results are saved to `23101748-sq26.db`, the database layer:

- writes the `files` table (used by all scripts and `download_files.py`)
- also writes normalized project metadata to `projects`, `keywords`, `person_role`, and `licenses`
- maps repository names to archive `repository_id` slugs during ingest
- stores raw license strings as returned by the source

## ⏱️ Estimated Times

| Repository Type | Count | Time per Repo | Total Time |
|----------------|-------|---------------|------------|
| API-based (fast) | 10 | 3-13 min | ~60 min |
| Web/site | 11 | 4-6 min | ~45-65 min |
| **All named repositories (individual scripts)** | 21 | varies | **~2 hours** |

*Times are for all 158 queries per repository*

## 🎯 Recommended Priority Order

**Already fully harvested (in committed database):**
1. ✅ **ICPSR** — 10,469 records via DataCite API
2. ✅ **UK Data Service** — 2,639 records via DataCite API

**High Priority (API-based, most reliable — extend the DB):**
3. Syracuse QDR — specialised in qualitative data
4. Harvard Dataverse — large general collection
5. Zenodo — massive multi-discipline repository
6. Dryad — research data focus
7. DANS — European repository

**Medium Priority:**
8. ADA Australian
9. AUSSDA Austria
10. CESSDA

**Lower Priority (web scraping, less stable):**
11–21. Sikt, FSD, Qualidata, Qualiservice, QualiBi, SADA, IHSN, Open Data Halle, Murray, Columbia, and others

## 📝 Notes

- Scripts save progress automatically every 25 queries
- Press Ctrl+C to stop gracefully (saves current progress)
- Zenodo has strict rate limiting — use the default 5 s delay
- ICPSR and UKDS use the DataCite public API; no credentials required to harvest metadata
- ICPSR and UKDS files require a free account + data-access agreement to download — use `download_files.py` to generate `links.txt` references
- All scripts update the same `23101748-sq26.db` database
- Duplicate filtering is file-oriented, so multi-file projects are not collapsed incorrectly

## 🔍 What Gets Searched

### QDA Software (48 extensions)
MaxQDA, NVivo, ATLAS.ti, QDA Miner, f4analyse, Quirkos, HyperRESEARCH, Transana, Ethnograph, Taguette, CAT, Weft QDA, Aquad, Cassandre, and more.

### Qualitative Methods (110+ terms)
- Qualitative data analysis
- Interview transcripts
- Thematic analysis
- Grounded theory
- Ethnography
- Phenomenology
- Case studies
- And many more...

