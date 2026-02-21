# Downloading ALL Files from QDA Datasets

## Overview
The scraper now downloads **ALL files** from datasets that contain QDA files, not just the QDA files themselves. This includes supporting files like:
- Excel spreadsheets (`.xlsx`, `.xls`)
- Word documents (`.docx`, `.doc`)
- PDFs (`.pdf`)
- Data files (`.csv`, `.zip`)
- Images, transcripts, and other research materials

## How It Works

### 1. Detection
When the scraper finds a dataset/record:
1. It checks if the dataset contains ANY QDA files
2. If YES → Downloads **ALL files** from that dataset
3. If NO → Skips the entire dataset

### 2. File Classification
Each file is marked in the database:
- `is_qda_file = 1` → QDA software file (.qdpx, .mx24, .nvpx, etc.)
- `is_qda_file = 0` → Supporting file (.xlsx, .pdf, .docx, etc.)

### 3. Folder Organization
All files from the same dataset are stored together:
```
downloads/
└── zenodo/
    ├── supporting_data_for_scoping_review-16082705/
    │   ├── EFL_ILP_ScopingReview_CodedData_20250718.qdpx  (QDA file)
    │   ├── Theme_year.xlsx                                 (Supporting)
    │   ├── S2_Table_Data_Charting.docx                    (Supporting)
    │   └── Country_Article_counts.xlsx                    (Supporting)
    │
    ├── polish_debates_on_higher_education-14535515/
    │   ├── Description_of_the_data_set.pdf                (Supporting)
    │   ├── Polish_debates_party_manifestos.qdpx           (QDA file)
    │   ├── Polish_debates_party_manifestos.mx20           (QDA file)
    │   ├── DiscussData_description.pdf                    (Supporting)
    │   └── Polish_debates_party_manifestos.mx22           (QDA file)
    │
    └── planet4b_frame_analysis_dataset-17347915/
        ├── PLANET4B_QDPXProject_FrameAnalysis.qdpx        (QDA file)
        ├── Interview_Exploratory1_Transcript.docx         (Supporting)
        ├── Interview_Exploratory2_Transcript.docx         (Supporting)
        ├── GreyLiterature1.pdf                            (Supporting)
        ├── GreyLiterature2.pdf                            (Supporting)
        └── ... (27 supporting files total)
```

## Real Examples

### Example 1: Scoping Review Dataset
**Dataset**: Supporting Data for Scoping Review on Interlanguage Pragmatics
- **Total files**: 4
- **QDA files**: 1 (.qdpx file, 67 MB)
- **Supporting files**: 3
  - Theme_year.xlsx (20 KB)
  - Data Charting and CCAT Scores.docx (50 KB)
  - Country_Article counts.xlsx (17 KB)

### Example 2: Polish Debates Dataset
**Dataset**: Polish debates on higher education
- **Total files**: 5
- **QDA files**: 3 (.qdpx, .mx20, .mx22 files)
- **Supporting files**: 2
  - Description of the data set.pdf (350 KB)
  - DiscussData description.pdf (50 KB)

### Example 3: PLANET4B Frame Analysis
**Dataset**: PLANET4B Frame Analysis Dataset
- **Total files**: 28
- **QDA files**: 1 (.qdpx file, 92 MB)
- **Supporting files**: 27
  - Interview transcripts (.docx files)
  - Grey literature PDFs
  - Metadata documents
  - Processed data files

## Statistics

The system tracks both QDA and supporting files:

```bash
$ python main.py stats

============================================================
Archive Statistics
============================================================
Total files: 45
  QDA files: 12
  Supporting files: 33

By file extension:
  .qdpx: 5
  .mx24: 3
  .mx22: 2
  .mx20: 2
  .xlsx: 8
  .pdf: 15
  .docx: 7
  .zip: 3
```

## Benefits

### 1. Complete Research Context
- Get the full dataset, not just the QDA file
- Access original data, transcripts, and documentation
- Understand how the QDA analysis was conducted

### 2. Reproducibility
- All materials needed to reproduce the analysis
- Supporting documentation and metadata
- Original data files

### 3. Efficient Storage
- Files from same dataset grouped together
- Easy to browse and understand
- Clear separation between repositories and datasets

## Usage

```bash
# Search for QDA files (automatically finds all supporting files too)
python main.py search --scraper zenodo --max-results 20

# View statistics (shows QDA vs supporting files)
python main.py stats

# Download all files
python main.py download

# Export metadata (includes is_qda_file flag)
python main.py export --output archive.csv
```

## Database Fields

Each file record includes:
- `filename`: Original filename
- `file_extension`: File extension (.qdpx, .xlsx, .pdf, etc.)
- `is_qda_file`: Boolean (1 = QDA file, 0 = supporting file)
- `qda_software`: Software name (only for QDA files)
- `source_id`: Dataset/record ID
- `project_title`: Dataset title
- All other metadata fields

## Implementation Details

### Zenodo Scraper
The `_extract_qda_files()` method:
1. Checks if record contains any QDA files
2. If yes, extracts **ALL files** from the record
3. Marks each file as QDA or supporting
4. Returns complete file list

### Other Scrapers
The same logic can be applied to:
- Dryad
- Syracuse QDR
- DataverseNO
- DANS
- UK Data Service
- And all other scrapers

Simply update their `_extract_qda_files()` methods to return all files when a QDA file is found.

