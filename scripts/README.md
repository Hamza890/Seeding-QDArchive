# QDA Archive Search Scripts

This folder contains scripts for searching QDA files across multiple repositories.

## Current Status

- **21 named repository scripts** in `scripts/search_*.py`
- **22 scraper classes** in `src/scrapers/` when shared components are included
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
- **`check_database.py`** - Check current database status and contents

## 🚀 Usage

### Search Individual Repositories (Recommended)

Start with high-priority API-based repositories:

```bash
# From project root
python scripts/search_syracuse.py      # ~3 min
python scripts/search_harvard.py       # ~8 min
python scripts/search_zenodo.py        # ~13 min
python scripts/search_dryad.py         # ~5 min
python scripts/search_dans.py          # ~5 min

# Then try others (see list above for all 21 named repositories)
python scripts/search_ada.py
python scripts/search_aussda.py
python scripts/search_sikt.py
# ... etc
```

### Run the Current 5-Repository Batch Set

```bash
python scripts/run_full_search.py
```

For full archive coverage, run the individual repository scripts listed above.

### Check Database Status

```bash
python scripts/check_database.py
```

## 📊 Search Configuration

Each script searches with:
- **158 unique queries** (48 extensions + 110 smart queries)
- **10 results per query maximum**
- **Automatic file-level deduplication**
- **Progress checkpoints** (saves every 25 queries)
- **Error handling** (continues on failures)

When results are saved to `qda_archive.db`, the current database layer:

- still writes the compatibility `files` table used by existing scripts
- also writes normalized project metadata to `projects`, `keywords`, `person_role`, and `licenses`
- maps repository names to archive `repository_id` slugs during ingest
- stores raw license strings as returned by the source metadata

## ⏱️ Estimated Times

| Repository Type | Count | Time per Repo | Total Time |
|----------------|-------|---------------|------------|
| API-based (fast) | 10 | 3-13 min | ~60 min |
| Web/site | 11 | 4-6 min | ~45-65 min |
| **All named repositories (individual scripts)** | 21 | varies | **~2 hours** |

*Times are for all 158 queries per repository*

## 🎯 Recommended Priority Order

**High Priority (API-based, most reliable):**
1. Syracuse QDR - Specialized in qualitative data
2. Harvard Dataverse - Large collection
3. Zenodo - Massive repository
4. Dryad - Research data focus
5. DANS - European repository

**Medium Priority:**
6. ADA Australian
7. AUSSDA Austria
8. CESSDA
9. ICPSR
10. UK Data Service

**Lower Priority (Web scraping):**
11-21. Other web/site repositories

## 📝 Notes

- Scripts save progress automatically every 25 queries
- Press Ctrl+C to stop gracefully (saves current progress)
- Zenodo has strict rate limiting - use 5s delay minimum
- All scripts update the same `qda_archive.db` database
- Duplicate filtering is file-oriented, so multi-file projects are less likely to be collapsed incorrectly
- Search scripts now populate both compatibility file rows and normalized project metadata behind the scenes

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

