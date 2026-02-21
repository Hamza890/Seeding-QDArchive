"""
Database module for managing QDA file metadata.
"""
import sqlite3
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any


class MetadataDatabase:
    """Manages SQLite database for QDA file metadata."""
    
    def __init__(self, db_path: str = "qda_archive.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        """Create database tables for storing metadata."""
        cursor = self.conn.cursor()
        
        # Main files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
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
                is_qda_file BOOLEAN DEFAULT 1,

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
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Index for faster searches
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_file_extension 
            ON files(file_extension)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_repository 
            ON files(source_repository)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_download_status 
            ON files(download_status)
        """)
        
        self.conn.commit()
    
    def insert_file(self, metadata: Dict[str, Any]) -> int:
        """Insert a new file record into the database."""
        cursor = self.conn.cursor()
        
        columns = ', '.join(metadata.keys())
        placeholders = ', '.join(['?' for _ in metadata])
        
        query = f"INSERT INTO files ({columns}) VALUES ({placeholders})"
        cursor.execute(query, list(metadata.values()))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def update_file(self, file_id: int, updates: Dict[str, Any]):
        """Update an existing file record."""
        updates['updated_at'] = datetime.now().isoformat()
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE files SET {set_clause} WHERE id = ?"
        
        cursor = self.conn.cursor()
        cursor.execute(query, list(updates.values()) + [file_id])
        self.conn.commit()
    
    def get_file_by_id(self, file_id: int) -> Optional[Dict]:
        """Retrieve a file record by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_files(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Retrieve all files, optionally filtered."""
        cursor = self.conn.cursor()
        
        if filters:
            where_clause = ' AND '.join([f"{k} = ?" for k in filters.keys()])
            query = f"SELECT * FROM files WHERE {where_clause}"
            cursor.execute(query, list(filters.values()))
        else:
            cursor.execute("SELECT * FROM files")
        
        return [dict(row) for row in cursor.fetchall()]
    
    def export_to_csv(self, output_path: str, filters: Optional[Dict[str, Any]] = None):
        """Export database records to CSV file."""
        files = self.get_all_files(filters)
        
        if not files:
            print("No files to export")
            return
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = files[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(files)
        
        print(f"Exported {len(files)} records to {output_path}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the archive."""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total files
        cursor.execute("SELECT COUNT(*) as count FROM files")
        stats['total_files'] = cursor.fetchone()['count']
        
        # Files by status
        cursor.execute("""
            SELECT download_status, COUNT(*) as count 
            FROM files 
            GROUP BY download_status
        """)
        stats['by_status'] = {row['download_status']: row['count'] 
                             for row in cursor.fetchall()}
        
        # Files by repository
        cursor.execute("""
            SELECT source_repository, COUNT(*) as count 
            FROM files 
            GROUP BY source_repository
        """)
        stats['by_repository'] = {row['source_repository']: row['count'] 
                                  for row in cursor.fetchall()}
        
        # Files by extension
        cursor.execute("""
            SELECT file_extension, COUNT(*) as count
            FROM files
            GROUP BY file_extension
        """)
        stats['by_extension'] = {row['file_extension']: row['count']
                                for row in cursor.fetchall()}

        # QDA files vs supporting files
        cursor.execute("""
            SELECT
                SUM(CASE WHEN is_qda_file = 1 THEN 1 ELSE 0 END) as qda_files,
                SUM(CASE WHEN is_qda_file = 0 THEN 1 ELSE 0 END) as supporting_files
            FROM files
        """)
        row = cursor.fetchone()
        stats['qda_files'] = row['qda_files'] or 0
        stats['supporting_files'] = row['supporting_files'] or 0

        return stats
    
    def close(self):
        """Close database connection."""
        self.conn.close()

