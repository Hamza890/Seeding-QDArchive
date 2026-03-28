#!/usr/bin/env python3
"""
Search a single repository with all queries.
Usage: python search_single_repo.py <repo_name>
Repos: syracuse, sikt, dataverseno, harvard, zenodo
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
from src.search_utils import get_result_identity, load_all_queries as shared_load_all_queries, save_results

REPOS = {
    'syracuse': ('Syracuse QDR', SyracuseQDRScraper, 1.0),
    'sikt': ('Sikt Norway', SiktScraper, 1.5),
    'dataverseno': ('DataverseNO', DataverseScraper, 2.0),
    'harvard': ('Harvard Dataverse', HarvardDataverseScraper, 3.0),
    'zenodo': ('Zenodo', ZenodoScraper, 5.0),
}

def load_all_queries():
    """Load all extensions and smart queries."""
    return shared_load_all_queries()

def main():
    if len(sys.argv) < 2:
        print("Usage: python search_single_repo.py <repo_name>")
        print("Available repos:", ', '.join(REPOS.keys()))
        sys.exit(1)
    
    repo_key = sys.argv[1].lower()
    if repo_key not in REPOS:
        print(f"Unknown repository: {repo_key}")
        print("Available repos:", ', '.join(REPOS.keys()))
        sys.exit(1)
    
    repo_name, scraper_class, delay = REPOS[repo_key]
    
    print("="*80)
    print(f"SEARCHING: {repo_name}")
    print("="*80)
    
    db = MetadataDatabase()
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM files")
    start_count = cursor.fetchone()[0]
    print(f"[DB] Starting files: {start_count}")
    
    # Load queries
    queries = load_all_queries()
    print(f"[INFO] Total queries: {len(queries)}")
    print(f"[INFO] Delay: {delay}s")
    
    # Search
    scraper = scraper_class()
    results = []
    seen_ids = set()
    
    for i, query in enumerate(queries, 1):
        if i % 10 == 1:
            print(f"[{i}/{len(queries)}] '{query[:30]}'...", end=' ', flush=True)
        
        try:
            search_results = scraper.search(query=query, max_results=1000)
            
            new_count = 0
            for result in search_results:
                result_id = get_result_identity(result)
                if result_id and result_id not in seen_ids:
                    seen_ids.add(result_id)
                    results.append(result)
                    new_count += 1
            
            if i % 10 == 1 and new_count > 0:
                print(f"+{new_count}", flush=True)
            elif i % 10 == 1:
                print("--", flush=True)
            
            # Save every 25 queries
            if i % 25 == 0 and results:
                saved = save_results(db, results, log_prefix="[SAVE]")
                print(f"[SAVE] Checkpoint: {saved} files saved")
                results = []
                seen_ids.clear()
            
            time.sleep(delay)
            
        except KeyboardInterrupt:
            print("\n[STOP] Interrupted")
            break
        except Exception as e:
            if i % 10 == 1:
                if '429' in str(e) or 'too many' in str(e).lower():
                    print("rate-limit", flush=True)
                else:
                    print("error", flush=True)
            time.sleep(delay * 2)
    
    # Save remaining
    if results:
        saved = save_results(db, results, log_prefix="[SAVE]")
        print(f"\n[SAVE] Final: {saved} files saved")
    
    cursor.execute("SELECT COUNT(*) FROM files")
    end_count = cursor.fetchone()[0]
    print(f"\n[DONE] Files: {start_count} -> {end_count} (+{end_count - start_count})")
    
    db.close()

if __name__ == "__main__":
    main()

