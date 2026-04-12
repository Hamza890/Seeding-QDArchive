#!/usr/bin/env python3
"""
Priority search across all working repositories.
Uses priority queries + QDA extensions only.
Appends results to 23101748-sq26.db.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import time
import json
from src.scrapers import (
    ZenodoScraper,
    HarvardDataverseScraper,
    SyracuseQDRScraper,
    SiktScraper,
    DataverseScraper
)
from src.database import MetadataDatabase
from src.search_utils import get_result_identity, save_results

# All working repositories (excluding ADA Australian)
REPOSITORIES = [
    ('Harvard Dataverse', HarvardDataverseScraper),
    ('Zenodo', ZenodoScraper),
    ('Sikt Norway', SiktScraper),
    ('Syracuse QDR', SyracuseQDRScraper),
    ('DataverseNO', DataverseScraper),
]

def load_qda_extensions():
    """Load all QDA extensions from config."""
    with open('config/qda_extensions.json', 'r') as f:
        data = json.load(f)
        extensions = []
        for software, info in data.get('qda_software', {}).items():
            extensions.extend(info.get('extensions', []))
        return list(set([ext.lstrip('.') for ext in extensions]))

def search_repository(repo_name, scraper_class, db, max_results=1000, delay=2.0):
    """Search a single repository and save results."""
    print(f"\n{'='*80}")
    print(f"REPOSITORY: {repo_name}")
    print(f"{'='*80}")
    
    try:
        scraper = scraper_class()
        
        # Get priority queries
        priority_queries = scraper.get_all_search_queries(priority_only=True)
        qda_extensions = load_qda_extensions()
        
        # Combine queries
        all_queries = list(set(priority_queries + qda_extensions))
        
        print(f"[INFO] Priority queries: {len(priority_queries)}")
        print(f"[INFO] QDA extensions: {len(qda_extensions)}")
        print(f"[INFO] Total queries: {len(all_queries)}")
        
        repo_results = []
        seen_ids = set()
        
        for i, query in enumerate(all_queries, 1):
            if i % 5 == 1:
                print(f"[{i}/{len(all_queries)}] '{query}'...", end=' ', flush=True)
            
            try:
                results = scraper.search(query=query, max_results=max_results)
                
                new_count = 0
                for result in results:
                    result_id = get_result_identity(result)
                    if result_id and result_id not in seen_ids:
                        seen_ids.add(result_id)
                        repo_results.append(result)
                        new_count += 1
                
                if i % 5 == 1 and new_count > 0:
                    print(f"+{new_count}", flush=True)
                elif i % 5 == 1:
                    print("--", flush=True)
                
                time.sleep(delay)
                
            except KeyboardInterrupt:
                print("\n[WARN] Interrupted, saving progress...")
                break
            except Exception as e:
                if i % 5 == 1:
                    if 'timeout' in str(e).lower():
                        print("timeout", flush=True)
                    else:
                        print(f"err", flush=True)
                time.sleep(delay)
                continue
        
        # Save results
        print(f"\n[RESULTS] Found {len(repo_results)} unique files")
        
        if repo_results:
            qda_count = sum(1 for r in repo_results if r.get('is_qda_file'))
            print(f"[RESULTS] QDA files: {qda_count}")
            
            saved = save_results(db, repo_results, log_prefix="[SAVE]")
            print(f"[SAVE] Saved {saved}/{len(repo_results)} to database")
            return saved
        else:
            print(f"[WARN] No results found")
            return 0
            
    except Exception as e:
        print(f"[ERROR] {repo_name}: {e}")
        return 0

def main():
    print("="*80)
    print("PRIORITY QDA SEARCH - ALL REPOSITORIES")
    print("="*80)
    
    db = MetadataDatabase()
    print(f"\n[DB] Database: {db.db_path}")
    
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM files")
    start_count = cursor.fetchone()[0]
    print(f"[DB] Starting records: {start_count}")
    
    total_saved = 0
    
    for i, (repo_name, scraper_class) in enumerate(REPOSITORIES, 1):
        print(f"\n[{i}/{len(REPOSITORIES)}] Processing {repo_name}...")
        saved = search_repository(repo_name, scraper_class, db)
        total_saved += saved
        
        if i < len(REPOSITORIES):
            print(f"[WAIT] Pausing 5s before next repository...")
            time.sleep(5)
    
    cursor.execute("SELECT COUNT(*) FROM files")
    end_count = cursor.fetchone()[0]
    
    print(f"\n{'='*80}")
    print("FINAL SUMMARY")
    print(f"{'='*80}")
    print(f"[DB] Records before: {start_count}")
    print(f"[DB] Records after: {end_count}")
    print(f"[DB] New records: {end_count - start_count}")
    print(f"[DONE] Search complete!")
    
    db.close()

if __name__ == "__main__":
    main()

