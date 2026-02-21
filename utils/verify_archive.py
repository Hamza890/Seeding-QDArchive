"""
Utility script to verify downloaded files and database integrity.
"""
import sys
from pathlib import Path
import hashlib

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import MetadataDatabase


def verify_file_hash(file_path: str, expected_hash: str, hash_type: str = 'md5') -> bool:
    """Verify file hash."""
    if not Path(file_path).exists():
        return False
    
    if hash_type == 'md5':
        hasher = hashlib.md5()
    elif hash_type == 'sha256':
        hasher = hashlib.sha256()
    else:
        return False
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    
    return hasher.hexdigest() == expected_hash


def verify_archive():
    """Verify all downloaded files in the archive."""
    print("=" * 60)
    print("QDA Archive Verification")
    print("=" * 60)
    
    db = MetadataDatabase()
    
    # Get all completed downloads
    completed_files = db.get_all_files({'download_status': 'completed'})
    
    print(f"\nVerifying {len(completed_files)} downloaded files...")
    
    verified = 0
    missing = 0
    corrupted = 0
    
    for file_meta in completed_files:
        file_id = file_meta['id']
        file_path = file_meta.get('file_path')
        filename = file_meta.get('filename')
        md5_hash = file_meta.get('md5_hash')
        
        if not file_path or not Path(file_path).exists():
            print(f"  ✗ MISSING: {filename} (ID: {file_id})")
            missing += 1
            
            # Update status
            db.update_file(file_id, {
                'download_status': 'failed',
                'error_message': 'File not found during verification'
            })
            continue
        
        # Verify hash if available
        if md5_hash:
            if verify_file_hash(file_path, md5_hash, 'md5'):
                print(f"  ✓ OK: {filename}")
                verified += 1
            else:
                print(f"  ✗ CORRUPTED: {filename} (ID: {file_id})")
                corrupted += 1
                
                # Update status
                db.update_file(file_id, {
                    'download_status': 'failed',
                    'error_message': 'Hash verification failed'
                })
        else:
            # No hash to verify, just check existence
            print(f"  ? EXISTS: {filename} (no hash to verify)")
            verified += 1
    
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    print(f"Total files checked: {len(completed_files)}")
    print(f"Verified: {verified}")
    print(f"Missing: {missing}")
    print(f"Corrupted: {corrupted}")
    
    db.close()
    
    return verified, missing, corrupted


def check_database_integrity():
    """Check database for inconsistencies."""
    print("\n" + "=" * 60)
    print("Database Integrity Check")
    print("=" * 60)
    
    db = MetadataDatabase()
    
    # Check for files without download URLs
    all_files = db.get_all_files()
    no_url = [f for f in all_files if not f.get('download_url')]
    
    print(f"\nFiles without download URL: {len(no_url)}")
    
    # Check for files without license info
    no_license = [f for f in all_files if not f.get('license_type')]
    print(f"Files without license info: {len(no_license)}")
    
    # Check for duplicate files
    filenames = {}
    for f in all_files:
        filename = f.get('filename')
        if filename:
            if filename in filenames:
                filenames[filename].append(f['id'])
            else:
                filenames[filename] = [f['id']]
    
    duplicates = {k: v for k, v in filenames.items() if len(v) > 1}
    print(f"Duplicate filenames: {len(duplicates)}")
    
    if duplicates:
        print("\nDuplicate files:")
        for filename, ids in list(duplicates.items())[:5]:  # Show first 5
            print(f"  {filename}: {len(ids)} copies (IDs: {ids})")
    
    db.close()


def clean_failed_downloads():
    """Remove failed download entries from filesystem."""
    print("\n" + "=" * 60)
    print("Cleaning Failed Downloads")
    print("=" * 60)
    
    db = MetadataDatabase()
    
    failed_files = db.get_all_files({'download_status': 'failed'})
    
    print(f"\nFound {len(failed_files)} failed downloads")
    
    removed = 0
    for file_meta in failed_files:
        file_path = file_meta.get('file_path')
        if file_path and Path(file_path).exists():
            try:
                Path(file_path).unlink()
                print(f"  Removed: {file_path}")
                removed += 1
            except Exception as e:
                print(f"  Error removing {file_path}: {e}")
    
    print(f"\nRemoved {removed} failed download files")
    
    db.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify QDA Archive integrity')
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify downloaded files'
    )
    parser.add_argument(
        '--check-db',
        action='store_true',
        help='Check database integrity'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean failed downloads'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all checks'
    )
    
    args = parser.parse_args()
    
    if args.all or args.verify:
        verify_archive()
    
    if args.all or args.check_db:
        check_database_integrity()
    
    if args.all or args.clean:
        clean_failed_downloads()
    
    if not any([args.verify, args.check_db, args.clean, args.all]):
        parser.print_help()

