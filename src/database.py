"""Database module for managing QDA file metadata."""

import csv
import re
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional


class MetadataDatabase:
    """Manages SQLite database for QDA file metadata."""

    REPOSITORY_ID_MAP = {
        'zenodo': 'zenodo',
        'dryad': 'dryad',
        'uk data service': 'uk-data-service',
        'syracuse qdr': 'syracuse-qualitative-data-repository',
        'dans': 'dans',
        'dataverse (https://dataverse.no)': 'dataverse-no',
        'ada - australian data archive': 'ada',
        'sada - south african data archive': 'sada',
        'ihsn - international household survey network': 'ihsn',
        'harvard dataverse': 'harvard-dataverse',
        'fsd - finnish social science data archive': 'finnish-social-science-data-archive',
        'aussda - austrian social science data archive': 'aussda',
        'cessda': 'cessda',
        'icpsr': 'icpsr',
        'open data uni halle': 'open-data-uni-halle',
        'murray research archive': 'harvard-murray-archive',
        'columbia oral history archives': 'columbia-oral-history-archive',
        'sikt norway': 'sikt',
    }

    URL_REPOSITORY_ID_MAP = {
        'zenodo.org': 'zenodo',
        'datadryad.org': 'dryad',
        'ukdataservice.ac.uk': 'uk-data-service',
        'qdr.syr.edu': 'syracuse-qualitative-data-repository',
        'data.qdr.syr.edu': 'syracuse-qualitative-data-repository',
        'dans.knaw.nl': 'dans',
        'dataverse.no': 'dataverse-no',
        'ada.edu.au': 'ada',
        'datafirst.uct.ac.za': 'sada',
        'ihsn.org': 'ihsn',
        'dataverse.harvard.edu': 'harvard-dataverse',
        'fsd.tuni.fi': 'finnish-social-science-data-archive',
        'services.fsd.tuni.fi': 'finnish-social-science-data-archive',
        'aussda.at': 'aussda',
        'data.aussda.at': 'aussda',
        'cessda.eu': 'cessda',
        'icpsr.umich.edu': 'icpsr',
        'opendata.uni-halle.de': 'open-data-uni-halle',
        'murray.harvard.edu': 'harvard-murray-archive',
        'guides.library.columbia.edu': 'columbia-oral-history-archive',
        'sikt.no': 'sikt',
    }

    PROJECT_FIELDS = [
        'repository_id',
        'source_repository',
        'source_url',
        'project_title',
        'project_description',
        'project_scope',
        'authors',
        'publication_date',
        'doi',
        'license_type',
        'license_url',
    ]

    def __init__(self, db_path: str = "23101748-sq26.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.file_columns: set[str] = set()
        self.create_tables()

    def create_tables(self):
        """Create the compatibility and normalized tables."""
        cursor = self.conn.cursor()
        self._create_files_table(cursor)
        self._ensure_files_columns(cursor)
        self._create_normalized_tables(cursor)
        self._create_indexes(cursor)
        self._create_duplicate_protection(cursor)
        self.conn.commit()

        self.file_columns = set(self._get_table_columns('files'))
        self._migrate_existing_files_to_normalized_tables()

    def _create_files_table(self, cursor):
        """Create the legacy-compatible files table."""
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                repository_id TEXT,
                filename TEXT NOT NULL,
                file_extension TEXT,
                file_size INTEGER,
                file_path TEXT,
                download_url TEXT,
                download_date TIMESTAMP,
                md5_hash TEXT,
                sha256_hash TEXT,
                qda_software TEXT,
                is_qda_file BOOLEAN DEFAULT 1,
                is_qualitative_data BOOLEAN DEFAULT 0,

                source_repository TEXT NOT NULL,
                source_url TEXT,
                source_id TEXT,

                license_type TEXT,
                license_url TEXT,

                project_title TEXT,
                project_description TEXT,
                project_scope TEXT,
                authors TEXT,
                publication_date TEXT,
                keywords TEXT,

                doi TEXT,
                version TEXT,
                language TEXT,
                file_format_version TEXT,

                download_status TEXT DEFAULT 'pending',
                error_message TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    def _ensure_files_columns(self, cursor):
        """Add compatibility columns needed by the normalized design."""
        existing_columns = set(self._get_table_columns('files'))

        if 'project_id' not in existing_columns:
            cursor.execute("ALTER TABLE files ADD COLUMN project_id INTEGER")
        if 'repository_id' not in existing_columns:
            cursor.execute("ALTER TABLE files ADD COLUMN repository_id TEXT")

    def _create_normalized_tables(self, cursor):
        """Create normalized project metadata tables."""
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repository_id TEXT NOT NULL,
                source_repository TEXT NOT NULL,
                source_url TEXT NOT NULL DEFAULT '',
                project_title TEXT NOT NULL DEFAULT '',
                project_description TEXT NOT NULL DEFAULT '',
                project_scope TEXT NOT NULL DEFAULT '',
                authors TEXT NOT NULL DEFAULT '',
                publication_date TEXT NOT NULL DEFAULT '',
                doi TEXT NOT NULL DEFAULT '',
                license_type TEXT NOT NULL DEFAULT '',
                license_url TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                keyword TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(project_id, keyword),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS person_role (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                person TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(project_id, person, role),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                license TEXT NOT NULL,
                license_url TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(project_id, license, license_url),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """
        )

    def _create_indexes(self, cursor):
        """Create indexes for common queries."""
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_extension ON files(file_extension)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_repository ON files(source_repository)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_download_status ON files(download_status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_repository_id ON files(repository_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_project_id ON files(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_repo_download_url ON files(repository_id, download_url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_repo_source_id_filename ON files(repository_id, source_id, filename)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_repo_source_url_filename ON files(repository_id, source_url, filename)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_repository_id ON projects(repository_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_source_url ON projects(source_url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_doi ON projects(doi)")

    def _create_duplicate_protection(self, cursor):
        """Create duplicate protection that still allows multi-file projects."""
        for trigger_name in (
            'trg_files_ignore_duplicate_source_id',
            'trg_files_ignore_duplicate_download_url',
            'trg_files_ignore_duplicate_fallback',
            'trg_files_ignore_duplicate_source_id_filename',
        ):
            cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")

        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trg_files_ignore_duplicate_download_url
            BEFORE INSERT ON files
            WHEN NEW.repository_id IS NOT NULL
             AND NEW.repository_id != ''
             AND NEW.download_url IS NOT NULL
             AND NEW.download_url != ''
             AND EXISTS (
                 SELECT 1
                 FROM files
                 WHERE repository_id = NEW.repository_id
                   AND download_url = NEW.download_url
             )
            BEGIN
                SELECT RAISE(IGNORE);
            END;
            """
        )

        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trg_files_ignore_duplicate_source_id_filename
            BEFORE INSERT ON files
            WHEN NEW.repository_id IS NOT NULL
             AND NEW.repository_id != ''
             AND (NEW.download_url IS NULL OR NEW.download_url = '')
             AND NEW.source_id IS NOT NULL
             AND NEW.source_id != ''
             AND NEW.filename IS NOT NULL
             AND NEW.filename != ''
             AND EXISTS (
                 SELECT 1
                 FROM files
                 WHERE repository_id = NEW.repository_id
                   AND source_id = NEW.source_id
                   AND filename = NEW.filename
             )
            BEGIN
                SELECT RAISE(IGNORE);
            END;
            """
        )

        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trg_files_ignore_duplicate_fallback
            BEFORE INSERT ON files
            WHEN NEW.repository_id IS NOT NULL
             AND NEW.repository_id != ''
             AND (NEW.download_url IS NULL OR NEW.download_url = '')
             AND (NEW.source_id IS NULL OR NEW.source_id = '')
             AND NEW.filename IS NOT NULL
             AND NEW.filename != ''
             AND NEW.source_url IS NOT NULL
             AND NEW.source_url != ''
             AND EXISTS (
                 SELECT 1
                 FROM files
                 WHERE repository_id = NEW.repository_id
                   AND source_url = NEW.source_url
                   AND filename = NEW.filename
             )
            BEGIN
                SELECT RAISE(IGNORE);
            END;
            """
        )

    def _get_table_columns(self, table_name: str) -> List[str]:
        """Return the columns present in the requested table."""
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [row['name'] for row in cursor.fetchall()]

    def _migrate_existing_files_to_normalized_tables(self):
        """Backfill normalized rows from existing compatibility rows.

        Only processes rows that have not yet been linked to a project so that
        the migration is effectively a no-op on subsequent startups once all
        rows are backfilled.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM files WHERE project_id IS NULL ORDER BY id")
        rows = cursor.fetchall()
        if not rows:
            return
        for row in rows:
            self._sync_project_from_file(row['id'])
        self.conn.commit()

    def _normalize_scalar(self, value: Any) -> Any:
        """Convert compound values into SQLite-friendly scalar values."""
        if value is None:
            return None
        if isinstance(value, (list, tuple, set)):
            return '; '.join(str(item).strip() for item in value if str(item).strip())
        if isinstance(value, dict):
            return str(value)
        return value

    def _prepare_file_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize incoming metadata to supported files-table columns."""
        prepared: Dict[str, Any] = {}
        candidate_columns = self.file_columns or set(self._get_table_columns('files'))

        for key, value in metadata.items():
            if key in candidate_columns:
                prepared[key] = self._normalize_scalar(value)

        prepared['repository_id'] = self._resolve_repository_id(metadata)
        prepared['source_repository'] = str(
            prepared.get('source_repository')
            or metadata.get('source_repository')
            or prepared['repository_id']
        )
        prepared['filename'] = str(
            prepared.get('filename')
            or metadata.get('filename')
            or metadata.get('source_id')
            or metadata.get('project_title')
            or 'unnamed'
        )

        if self._is_blank(prepared.get('download_status')):
            prepared['download_status'] = 'pending'
        if prepared.get('is_qda_file') is None:
            prepared['is_qda_file'] = True
        if prepared.get('is_qualitative_data') is None:
            prepared['is_qualitative_data'] = False

        return prepared

    def _resolve_repository_id(self, metadata: Dict[str, Any]) -> str:
        """Map scraper names/URLs to the exact repository_id slugs requested by the user."""
        source_repository = str(metadata.get('source_repository') or '').strip().lower()
        source_url = str(metadata.get('source_url') or metadata.get('download_url') or '').strip().lower()

        if source_repository in self.REPOSITORY_ID_MAP:
            return self.REPOSITORY_ID_MAP[source_repository]

        for fragment, repository_id in self.URL_REPOSITORY_ID_MAP.items():
            if fragment in source_url:
                return repository_id

        if source_repository.startswith('dataverse (') and 'dataverse.no' in source_repository:
            return 'dataverse-no'

        return self._slugify(source_repository or source_url or 'unknown')

    def _slugify(self, value: str) -> str:
        """Build a stable fallback slug for unknown repositories."""
        slug = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
        return slug or 'unknown'

    def _find_existing_file_id(self, metadata: Dict[str, Any]) -> Optional[int]:
        """Return an existing file ID if the file is already present."""
        cursor = self.conn.cursor()
        repository_id = metadata.get('repository_id')
        download_url = metadata.get('download_url')
        source_id = metadata.get('source_id')
        source_url = metadata.get('source_url')
        filename = metadata.get('filename')

        if repository_id and download_url:
            cursor.execute(
                "SELECT id FROM files WHERE repository_id = ? AND download_url = ? LIMIT 1",
                (repository_id, download_url),
            )
            row = cursor.fetchone()
            if row:
                return row['id']

        if repository_id and source_id and filename:
            cursor.execute(
                "SELECT id FROM files WHERE repository_id = ? AND source_id = ? AND filename = ? LIMIT 1",
                (repository_id, source_id, filename),
            )
            row = cursor.fetchone()
            if row:
                return row['id']

        if repository_id and source_url and filename:
            cursor.execute(
                "SELECT id FROM files WHERE repository_id = ? AND source_url = ? AND filename = ? LIMIT 1",
                (repository_id, source_url, filename),
            )
            row = cursor.fetchone()
            if row:
                return row['id']

        return None

    def _find_existing_project_id(self, metadata: Dict[str, Any]) -> Optional[int]:
        """Return an existing project ID when a logical project match is found."""
        cursor = self.conn.cursor()
        repository_id = metadata.get('repository_id')
        doi = metadata.get('doi')
        source_url = metadata.get('source_url')
        source_id = metadata.get('source_id')
        project_title = metadata.get('project_title')
        authors = metadata.get('authors')

        if repository_id and doi:
            cursor.execute(
                "SELECT id FROM projects WHERE repository_id = ? AND doi = ? LIMIT 1",
                (repository_id, doi),
            )
            row = cursor.fetchone()
            if row:
                return row['id']

        if repository_id and source_url:
            cursor.execute(
                "SELECT id FROM projects WHERE repository_id = ? AND source_url = ? LIMIT 1",
                (repository_id, source_url),
            )
            row = cursor.fetchone()
            if row:
                return row['id']

        if repository_id and source_id:
            cursor.execute(
                """
                SELECT project_id
                FROM files
                WHERE repository_id = ?
                  AND source_id = ?
                  AND project_id IS NOT NULL
                LIMIT 1
                """,
                (repository_id, source_id),
            )
            row = cursor.fetchone()
            if row and row['project_id']:
                return row['project_id']

        if repository_id and project_title and authors:
            cursor.execute(
                "SELECT id FROM projects WHERE repository_id = ? AND project_title = ? AND authors = ? LIMIT 1",
                (repository_id, project_title, authors),
            )
            row = cursor.fetchone()
            if row:
                return row['id']

        if repository_id and project_title:
            cursor.execute(
                "SELECT id FROM projects WHERE repository_id = ? AND project_title = ? LIMIT 1",
                (repository_id, project_title),
            )
            row = cursor.fetchone()
            if row:
                return row['id']

        return None

    def _build_project_data(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build a normalized project row from file metadata."""
        return {
            'repository_id': metadata.get('repository_id') or 'unknown',
            'source_repository': metadata.get('source_repository') or 'unknown',
            'source_url': metadata.get('source_url') or '',
            'project_title': metadata.get('project_title') or '',
            'project_description': metadata.get('project_description') or '',
            'project_scope': metadata.get('project_scope') or '',
            'authors': metadata.get('authors') or '',
            'publication_date': metadata.get('publication_date') or '',
            'doi': metadata.get('doi') or '',
            'license_type': metadata.get('license_type') or '',
            'license_url': metadata.get('license_url') or '',
        }

    def _upsert_project(self, metadata: Dict[str, Any]) -> int:
        """Create or merge a project row and return its ID."""
        cursor = self.conn.cursor()
        project_data = self._build_project_data(metadata)
        project_id = self._find_existing_project_id(metadata)

        if project_id is not None:
            self._merge_project(project_id, project_data)
            return project_id

        columns = ', '.join(self.PROJECT_FIELDS)
        placeholders = ', '.join(['?' for _ in self.PROJECT_FIELDS])
        cursor.execute(
            f"INSERT INTO projects ({columns}) VALUES ({placeholders})",
            [project_data[field] for field in self.PROJECT_FIELDS],
        )
        return cursor.lastrowid

    def _merge_project(self, project_id: int, project_data: Dict[str, Any]):
        """Fill missing project values when a project already exists."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        if not row:
            return

        existing = dict(row)
        updates = {}
        for field in self.PROJECT_FIELDS:
            if field == 'repository_id':
                continue
            if self._is_blank(existing.get(field)) and not self._is_blank(project_data.get(field)):
                updates[field] = project_data[field]

        if updates:
            updates['updated_at'] = datetime.now().isoformat()
            set_clause = ', '.join(f"{key} = ?" for key in updates)
            cursor.execute(
                f"UPDATE projects SET {set_clause} WHERE id = ?",
                list(updates.values()) + [project_id],
            )

    def _sync_project_children(self, project_id: int, metadata: Dict[str, Any]):
        """Populate normalized child tables without altering the raw source strings."""
        cursor = self.conn.cursor()
        self._insert_license(project_id, metadata.get('license_type'), metadata.get('license_url'))

        for keyword in self._split_semicolon_values(metadata.get('keywords')):
            cursor.execute(
                "INSERT OR IGNORE INTO keywords (project_id, keyword) VALUES (?, ?)",
                (project_id, keyword),
            )

        for author in self._split_semicolon_values(metadata.get('authors')):
            cursor.execute(
                "INSERT OR IGNORE INTO person_role (project_id, person, role) VALUES (?, ?, ?)",
                (project_id, author, 'author'),
            )

    def _insert_license(self, project_id: int, license_value: Any, license_url: Any):
        """Insert the raw license string exactly as supplied by the source."""
        if self._is_blank(license_value):
            return
        self.conn.execute(
            "INSERT OR IGNORE INTO licenses (project_id, license, license_url) VALUES (?, ?, ?)",
            (project_id, str(license_value), str(license_url or '')),
        )

    def _split_semicolon_values(self, value: Any) -> List[str]:
        """Split scraper-produced semicolon-delimited values only."""
        if self._is_blank(value):
            return []
        if isinstance(value, (list, tuple, set)):
            return [str(item).strip() for item in value if str(item).strip()]
        return [item.strip() for item in str(value).split(';') if item.strip()]

    def _is_blank(self, value: Any) -> bool:
        """Return True when a value should be treated as empty."""
        return value is None or str(value).strip() == ''

    def _link_file_to_project(self, file_id: int, project_id: int, repository_id: str):
        """Ensure a compatibility file row is linked to its normalized project."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT project_id, repository_id FROM files WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        if not row:
            return

        updates = {}
        if row['project_id'] != project_id:
            updates['project_id'] = project_id
        if row['repository_id'] != repository_id:
            updates['repository_id'] = repository_id

        if updates:
            updates['updated_at'] = datetime.now().isoformat()
            set_clause = ', '.join(f"{key} = ?" for key in updates)
            cursor.execute(
                f"UPDATE files SET {set_clause} WHERE id = ?",
                list(updates.values()) + [file_id],
            )

    def _sync_project_from_file(self, file_id: int):
        """Refresh normalized tables from a compatibility file row."""
        file_row = self.get_file_by_id(file_id)
        if not file_row:
            return

        prepared = self._prepare_file_metadata(file_row)
        project_id = self._upsert_project(prepared)
        self._link_file_to_project(file_id, project_id, prepared['repository_id'])
        self._sync_project_children(project_id, prepared)

    def insert_file(self, metadata: Dict[str, Any]) -> Optional[int]:
        """Insert a file row and populate the normalized schema in parallel."""
        prepared = self._prepare_file_metadata(metadata)
        project_id = self._upsert_project(prepared)
        prepared['project_id'] = project_id

        existing_file_id = self._find_existing_file_id(prepared)
        if existing_file_id is not None:
            self._link_file_to_project(existing_file_id, project_id, prepared['repository_id'])
            self._sync_project_children(project_id, prepared)
            self.conn.commit()
            return None

        columns = [column for column in prepared if column in self.file_columns]
        placeholders = ', '.join(['?' for _ in columns])
        query = f"INSERT INTO files ({', '.join(columns)}) VALUES ({placeholders})"

        cursor = self.conn.cursor()
        changes_before = self.conn.total_changes
        cursor.execute(query, [prepared[column] for column in columns])

        if self.conn.total_changes == changes_before:
            existing_file_id = self._find_existing_file_id(prepared)
            if existing_file_id is not None:
                self._link_file_to_project(existing_file_id, project_id, prepared['repository_id'])
            self._sync_project_children(project_id, prepared)
            self.conn.commit()
            return None

        self._sync_project_children(project_id, prepared)
        self.conn.commit()
        return cursor.lastrowid

    def update_file(self, file_id: int, updates: Dict[str, Any]):
        """Update an existing compatibility file record."""
        filtered_updates = {
            key: self._normalize_scalar(value)
            for key, value in updates.items()
            if key in self.file_columns
        }
        filtered_updates['updated_at'] = datetime.now().isoformat()

        set_clause = ', '.join(f"{key} = ?" for key in filtered_updates)
        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE files SET {set_clause} WHERE id = ?",
            list(filtered_updates.values()) + [file_id],
        )
        self._sync_project_from_file(file_id)
        self.conn.commit()

    def get_file_by_id(self, file_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a file record by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_files(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve all compatibility file rows, optionally filtered."""
        cursor = self.conn.cursor()
        if filters:
            where_clause = ' AND '.join(f"{key} = ?" for key in filters)
            cursor.execute(f"SELECT * FROM files WHERE {where_clause}", list(filters.values()))
        else:
            cursor.execute("SELECT * FROM files")
        return [dict(row) for row in cursor.fetchall()]

    def export_to_csv(self, output_path: str, filters: Optional[Dict[str, Any]] = None):
        """Export compatibility file rows to a CSV file."""
        files = self.get_all_files(filters)
        if not files:
            print("No files to export")
            return

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=files[0].keys())
            writer.writeheader()
            writer.writerows(files)

        print(f"Exported {len(files)} records to {output_path}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the archive."""
        cursor = self.conn.cursor()
        stats: Dict[str, Any] = {}

        cursor.execute("SELECT COUNT(*) AS count FROM files")
        stats['total_files'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) AS count FROM projects")
        stats['total_projects'] = cursor.fetchone()['count']

        cursor.execute(
            """
            SELECT download_status, COUNT(*) AS count
            FROM files
            GROUP BY download_status
            """
        )
        stats['by_status'] = {row['download_status']: row['count'] for row in cursor.fetchall()}

        cursor.execute(
            """
            SELECT source_repository, COUNT(*) AS count
            FROM files
            GROUP BY source_repository
            """
        )
        stats['by_repository'] = {row['source_repository']: row['count'] for row in cursor.fetchall()}

        cursor.execute(
            """
            SELECT file_extension, COUNT(*) AS count
            FROM files
            GROUP BY file_extension
            """
        )
        stats['by_extension'] = {row['file_extension']: row['count'] for row in cursor.fetchall()}

        cursor.execute(
            """
            SELECT
                SUM(CASE WHEN is_qda_file = 1 THEN 1 ELSE 0 END) AS qda_files,
                SUM(CASE WHEN is_qda_file = 0 THEN 1 ELSE 0 END) AS supporting_files
            FROM files
            """
        )
        row = cursor.fetchone()
        stats['qda_files'] = row['qda_files'] or 0
        stats['supporting_files'] = row['supporting_files'] or 0
        return stats

    def close(self):
        """Close database connection."""
        self.conn.close()

