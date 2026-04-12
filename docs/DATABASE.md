# Database Schema Documentation

The QDA Archive uses SQLite to store search and download metadata in `23101748-sq26.db`.

## Database file

- **Location**: project root as `23101748-sq26.db`
- **Type**: SQLite 3
- **Encoding**: UTF-8

## Current design

The database now uses a **compatibility-first normalized schema**.

That means:

- existing scripts can still read and write the `files` table
- normalized project metadata is also written to supporting tables
- raw source values are preserved during ingest rather than cleaned up early

## Tables

### `files`

This remains the main operational table used by the current search, download, export, and verification scripts.

It stores one row per discovered/downloaded file and includes both:

- file-specific fields such as `filename`, `download_url`, `file_path`, hashes, and status
- compatibility copies of project metadata such as `project_title`, `authors`, `keywords`, and `license_type`

Important compatibility columns include:

- `id`
- `project_id`
- `repository_id`
- `filename`
- `file_extension`
- `download_url`
- `source_repository`
- `source_url`
- `source_id`
- `license_type`
- `license_url`
- `project_title`
- `project_description`
- `project_scope`
- `authors`
- `publication_date`
- `keywords`
- `doi`
- `download_status`
- `error_message`
- `created_at`
- `updated_at`

### `projects`

Stores one logical project/dataset record per repository/project identity.

Key columns:

- `id`
- `repository_id`
- `source_repository`
- `source_url`
- `project_title`
- `project_description`
- `project_scope`
- `authors`
- `publication_date`
- `doi`
- `license_type`
- `license_url`
- `created_at`
- `updated_at`

### `keywords`

Stores project keywords as separate rows.

Key columns:

- `id`
- `project_id`
- `keyword`
- `created_at`

### `person_role`

Stores people associated with a project, currently populated from author metadata.

Key columns:

- `id`
- `project_id`
- `person`
- `role`
- `created_at`

### `licenses`

Stores project license rows.

Key columns:

- `id`
- `project_id`
- `license`
- `license_url`
- `created_at`

## Ingest rules

### Raw metadata preservation

Source metadata is preserved as provided by the repository whenever practical.

- license strings are stored exactly as seen in source metadata
- project/source text is not cleaned or standardized during ingest
- semicolon-delimited fields from scrapers are only split when populating normalized child tables

### Repository IDs

`repository_id` is populated using the exact repository slugs requested for this archive.

Examples:

- `zenodo`
- `dryad`
- `uk-data-service`
- `syracuse-qualitative-data-repository`
- `dans`
- `harvard-dataverse`
- `icpsr`
- `open-data-uni-halle`
- `columbia-oral-history-archive`
- `sikt`
- `hihsn`

### Project/file write behavior

Each call to `db.insert_file(...)` now does all of the following:

1. resolves `repository_id`
2. creates or merges a `projects` row
3. inserts the compatibility `files` row
4. inserts related `keywords`, `person_role`, and `licenses` rows

### Legacy DB compatibility

When an older database is opened:

- `project_id` and `repository_id` are added to `files` if missing
- normalized tables are created if missing
- existing `files` rows are backfilled into normalized tables

## Duplicate handling

Duplicate protection is now file-oriented so that multi-file projects are not incorrectly collapsed.

The database tries to treat rows as duplicates in this order:

1. same `repository_id` + same `download_url`
2. same `repository_id` + same `source_id` + same `filename`
3. same `repository_id` + same `source_url` + same `filename`

This is intentionally more specific than the older `source_repository + source_id` rule.

## Common API usage

### Get pending files

- `db.get_all_files({'download_status': 'pending'})`

### Get files from one repository

- `db.get_all_files({'repository_id': 'harvard-dataverse'})`
- `db.get_all_files({'source_repository': 'Zenodo'})`

### Insert a file

- `file_id = db.insert_file(metadata)`

If the file is a duplicate, `insert_file(...)` returns `None`.

### Update a file

- `db.update_file(file_id, {'download_status': 'completed'})`

Updating a file also re-syncs its related normalized project metadata.

### Export to CSV

- `db.export_to_csv('output.csv')`

Exports compatibility `files` rows.

### Get statistics

- `stats = db.get_statistics()`

Current statistics include:

- `total_files`
- `total_projects`
- `by_status`
- `by_repository`
- `by_extension`
- `qda_files`
- `supporting_files`

## Maintenance

### Backup

- simple copy of `23101748-sq26.db`
- or SQLite `.backup`

### Vacuum

Run SQLite `VACUUM` periodically if the DB is heavily updated.

### Size check

Use Python `Path('23101748-sq26.db').stat().st_size` or any SQLite browser.

## Data integrity notes

- normalized child tables use foreign keys to `projects`
- compatibility scripts still operate through `files`
- hashes and download state remain stored on file rows
- source attribution remains on both compatibility and normalized data

## Operational note

The repository-specific `scripts/search_*.py` entry points remain the main operational search path.

They continue to work with the compatibility `files` table while now also populating normalized project metadata behind the scenes.

