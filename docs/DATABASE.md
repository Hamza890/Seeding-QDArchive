# Database Schema Documentation

The QDA Archive uses SQLite to store metadata about collected files.

## Database File

- **Location**: `qda_archive.db` (in project root)
- **Type**: SQLite 3
- **Encoding**: UTF-8

## Tables

### files

Main table storing metadata for all QDA files.

#### Schema

```sql
CREATE TABLE files (
    -- Primary key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- File information
    filename TEXT NOT NULL,
    file_extension TEXT,
    file_size INTEGER,
    file_path TEXT,
    download_url TEXT,
    download_date TIMESTAMP,
    md5_hash TEXT,
    sha256_hash TEXT,
    qda_software TEXT,
    
    -- Source information
    source_repository TEXT NOT NULL,
    source_url TEXT,
    source_id TEXT,
    
    -- License information
    license_type TEXT,
    license_url TEXT,
    
    -- Project metadata
    project_title TEXT,
    project_description TEXT,
    project_scope TEXT,
    authors TEXT,
    publication_date TEXT,
    keywords TEXT,
    
    -- Additional metadata
    doi TEXT,
    version TEXT,
    language TEXT,
    file_format_version TEXT,
    
    -- Status
    download_status TEXT DEFAULT 'pending',
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Indexes

```sql
CREATE INDEX idx_file_extension ON files(file_extension);
CREATE INDEX idx_source_repository ON files(source_repository);
CREATE INDEX idx_download_status ON files(download_status);
```

## Field Descriptions

### File Information

- **id**: Auto-incrementing primary key
- **filename**: Original filename (e.g., "study_data.qdpx")
- **file_extension**: File extension (e.g., ".qdpx")
- **file_size**: Size in bytes
- **file_path**: Local path to downloaded file
- **download_url**: URL where file was downloaded from
- **download_date**: ISO 8601 timestamp of download
- **md5_hash**: MD5 hash for integrity verification
- **sha256_hash**: SHA256 hash for integrity verification
- **qda_software**: QDA software name (e.g., "MaxQDA", "NVivo")

### Source Information

- **source_repository**: Repository name (e.g., "Zenodo", "Dryad")
- **source_url**: URL to the dataset/project page
- **source_id**: Repository-specific identifier

### License Information

- **license_type**: License identifier (e.g., "CC-BY-4.0", "CC0-1.0")
- **license_url**: URL to license text

### Project Metadata

- **project_title**: Title of the research project/dataset
- **project_description**: Description or abstract
- **project_scope**: Scope of the research (optional)
- **authors**: Semicolon-separated list of authors
- **publication_date**: Publication date (ISO 8601 format)
- **keywords**: Semicolon-separated keywords

### Additional Metadata

- **doi**: Digital Object Identifier
- **version**: Dataset/file version
- **language**: Language of the data
- **file_format_version**: QDA file format version

### Status Fields

- **download_status**: One of:
  - `pending`: Found but not downloaded
  - `completed`: Successfully downloaded
  - `failed`: Download failed
- **error_message**: Error message if download failed

### Timestamps

- **created_at**: When record was created
- **updated_at**: When record was last updated

## Common Queries

### Get all pending downloads

```python
db.get_all_files({'download_status': 'pending'})
```

### Get files from specific repository

```python
db.get_all_files({'source_repository': 'Zenodo'})
```

### Get files by extension

```python
db.get_all_files({'file_extension': '.qdpx'})
```

### Get statistics

```python
stats = db.get_statistics()
```

## Database Operations

### Insert a file

```python
metadata = {
    'filename': 'study.qdpx',
    'file_extension': '.qdpx',
    'source_repository': 'Zenodo',
    'download_status': 'pending'
}
file_id = db.insert_file(metadata)
```

### Update a file

```python
updates = {
    'download_status': 'completed',
    'file_path': '/path/to/file.qdpx',
    'md5_hash': 'abc123...'
}
db.update_file(file_id, updates)
```

### Export to CSV

```python
db.export_to_csv('output.csv')
```

## Backup and Maintenance

### Backup Database

```bash
# Simple copy
cp qda_archive.db qda_archive_backup.db

# Or use SQLite backup
sqlite3 qda_archive.db ".backup qda_archive_backup.db"
```

### Vacuum Database

```python
import sqlite3
conn = sqlite3.connect('qda_archive.db')
conn.execute('VACUUM')
conn.close()
```

### Check Database Size

```python
from pathlib import Path
size = Path('qda_archive.db').stat().st_size
print(f"Database size: {size / 1024 / 1024:.2f} MB")
```

## Performance Considerations

- **Indexes**: Created on frequently queried fields
- **Batch inserts**: Use transactions for multiple inserts
- **Regular vacuum**: Reclaim space after deletions

## Data Integrity

- **Hash verification**: MD5 and SHA256 hashes stored for verification
- **Foreign key constraints**: Not used (single table design)
- **NOT NULL constraints**: Applied to critical fields

## Privacy and Compliance

- **No personal data**: Only metadata about research datasets
- **License tracking**: All files should have license information
- **Source attribution**: Source repository and URL always recorded

