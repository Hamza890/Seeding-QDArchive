#!/usr/bin/env python3
"""Check database status and contents."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import MetadataDatabase

db = MetadataDatabase()
cursor = db.conn.cursor()

# Total counts
cursor.execute('SELECT COUNT(*) FROM files')
total = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM files WHERE is_qda_file = 1')
qda = cursor.fetchone()[0]

print(f"Total files: {total}")
print(f"QDA files: {qda}")
print(f"Other files: {total - qda}")

# By repository
cursor.execute('SELECT source_repository, COUNT(*) FROM files GROUP BY source_repository')
print("\nBy Repository:")
for row in cursor.fetchall():
    print(f"  {row[0]:25}: {row[1]:3} files")

# Sample QDA files
cursor.execute('SELECT filename, source_repository, file_extension FROM files WHERE is_qda_file = 1 LIMIT 10')
print("\nSample QDA Files:")
for row in cursor.fetchall():
    print(f"  {row[0][:50]:50} | {row[1]:20} | .{row[2]}")

db.close()

