import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.database import MetadataDatabase


class NormalizedDatabaseTests(unittest.TestCase):
    def make_db(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        db_path = Path(temp_dir.name) / 'test.db'
        db = MetadataDatabase(str(db_path))
        self.addCleanup(db.close)
        return db, db_path

    def sample_metadata(self, **overrides):
        metadata = {
            'filename': 'interviews.qdpx',
            'file_extension': 'qdpx',
            'download_url': 'https://dataverse.harvard.edu/api/access/datafile/1',
            'source_repository': 'Harvard Dataverse',
            'source_url': 'https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.1/TEST',
            'source_id': 'doi:10.1/TEST',
            'license_type': 'CC-BY-4.0',
            'license_url': 'https://creativecommons.org/licenses/by/4.0/',
            'project_title': 'Interview Study',
            'project_description': 'Raw source metadata should stay intact.',
            'authors': 'Alice Example; Bob Example',
            'publication_date': '2024-01-01',
            'keywords': 'interview; coding',
            'doi': '10.1/TEST',
            'is_qda_file': True,
        }
        metadata.update(overrides)
        return metadata

    def test_insert_creates_project_and_child_rows(self):
        db, _ = self.make_db()

        file_id_1 = db.insert_file(self.sample_metadata())
        file_id_2 = db.insert_file(
            self.sample_metadata(
                filename='notes.pdf',
                file_extension='pdf',
                download_url='https://dataverse.harvard.edu/api/access/datafile/2',
            )
        )

        self.assertIsNotNone(file_id_1)
        self.assertIsNotNone(file_id_2)
        self.assertNotEqual(file_id_1, file_id_2)

        cursor = db.conn.cursor()
        self.assertEqual(cursor.execute('SELECT COUNT(*) FROM files').fetchone()[0], 2)
        self.assertEqual(cursor.execute('SELECT COUNT(*) FROM projects').fetchone()[0], 1)
        self.assertEqual(cursor.execute('SELECT COUNT(*) FROM keywords').fetchone()[0], 2)
        self.assertEqual(cursor.execute('SELECT COUNT(*) FROM person_role').fetchone()[0], 2)
        self.assertEqual(cursor.execute('SELECT COUNT(*) FROM licenses').fetchone()[0], 1)

        repository_id = cursor.execute('SELECT repository_id FROM projects').fetchone()[0]
        self.assertEqual(repository_id, 'harvard-dataverse')
        self.assertEqual(db.get_statistics()['total_projects'], 1)

    def test_duplicate_detection_keeps_distinct_files_from_same_project(self):
        db, _ = self.make_db()

        file_id_1 = db.insert_file(self.sample_metadata(download_url=None, filename='one.qdpx'))
        file_id_2 = db.insert_file(self.sample_metadata(download_url=None, filename='two.qdpx'))
        duplicate = db.insert_file(self.sample_metadata(download_url=None, filename='one.qdpx'))

        self.assertIsNotNone(file_id_1)
        self.assertIsNotNone(file_id_2)
        self.assertIsNone(duplicate)

        cursor = db.conn.cursor()
        self.assertEqual(cursor.execute('SELECT COUNT(*) FROM files').fetchone()[0], 2)
        self.assertEqual(cursor.execute('SELECT COUNT(*) FROM projects').fetchone()[0], 1)

    def test_existing_legacy_rows_are_backfilled(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        db_path = Path(temp_dir.name) / 'legacy.db'

        conn = sqlite3.connect(db_path)
        conn.execute(
            '''
            CREATE TABLE files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_extension TEXT,
                file_size INTEGER,
                file_path TEXT,
                download_url TEXT,
                download_date TIMESTAMP,
                md5_hash TEXT,
                sha256_hash TEXT,
                qda_software TEXT,
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
                is_qda_file BOOLEAN DEFAULT 1,
                is_qualitative_data BOOLEAN DEFAULT 0,
                download_status TEXT DEFAULT 'pending',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )
        conn.execute(
            '''
            INSERT INTO files (
                filename, source_repository, source_url, source_id, license_type,
                project_title, authors, keywords, doi
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                'legacy.qdpx', 'Harvard Dataverse',
                'https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.1/LEGACY',
                'doi:10.1/LEGACY', 'Restricted access', 'Legacy Study',
                'Legacy Author', 'legacy keyword', '10.1/LEGACY',
            ),
        )
        conn.commit()
        conn.close()

        db = MetadataDatabase(str(db_path))
        self.addCleanup(db.close)

        row = db.conn.execute(
            'SELECT project_id, repository_id FROM files WHERE filename = ?',
            ('legacy.qdpx',),
        ).fetchone()
        self.assertIsNotNone(row['project_id'])
        self.assertEqual(row['repository_id'], 'harvard-dataverse')
        self.assertEqual(db.conn.execute('SELECT COUNT(*) FROM projects').fetchone()[0], 1)


if __name__ == '__main__':
    unittest.main()