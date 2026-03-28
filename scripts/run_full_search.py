#!/usr/bin/env python3
"""
Full comprehensive search using ALL queries across all repositories.
Designed to maximize QDA file discovery with proper rate limiting.
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

# Repositories ordered by reliability (Syracuse QDR is most reliable)
REPOSITORIES = [
    ('Syracuse QDR', SyracuseQDRScraper, 1.0),  # Fast, reliable
    ('Sikt Norway', SiktScraper, 1.5),  # Fast, reliable
    ('DataverseNO', DataverseScraper, 2.0),  # Moderate
    ('Harvard Dataverse', HarvardDataverseScraper, 3.0),  # Slower
    ('Zenodo', ZenodoScraper, 5.0),  # Rate limited, needs longer delays
]

def load_all_queries():
    """Load all queries from config, including multilingual terms."""
    return shared_load_all_queries()

def search_repository(repo_name, scraper_class, db, delay, max_results=1000):
    """Search a single repository with all queries."""
    print(f"\n{'='*80}")
    print(f"REPOSITORY: {repo_name}")
    print(f"{'='*80}")
    
    try:
        scraper = scraper_class()
        
        # Get all queries
        all_queries = load_all_queries()
        
        print(f"[INFO] Total unique queries: {len(all_queries)}")
        print(f"[INFO] Delay between queries: {delay}s")
        print(f"[INFO] Max results per query: {max_results}")
        
        repo_results = []
        seen_ids = set()
        errors = 0
        
        for i, query in enumerate(all_queries, 1):
            # Progress indicator every 10 queries
            if i % 10 == 1 or i == len(all_queries):
                print(f"[{i}/{len(all_queries)}] '{query[:30]}'...", end=' ', flush=True)
            
            try:
                results = scraper.search(query=query, max_results=max_results)
                
                new_count = 0
                for result in results:
                    result_id = get_result_identity(result)
                    if result_id and result_id not in seen_ids:
                        seen_ids.add(result_id)
                        repo_results.append(result)
                        new_count += 1
                
                if (i % 10 == 1 or i == len(all_queries)) and new_count > 0:
                    print(f"+{new_count}", flush=True)
                elif i % 10 == 1 or i == len(all_queries):
                    print("--", flush=True)
                
                # Save progress every 50 queries
                if i % 50 == 0 and repo_results:
                    saved = save_results(db, repo_results)
                    print(f"[CHECKPOINT] Saved {saved} files to database")
                    repo_results = []  # Clear saved results
                    seen_ids.clear()
                
                time.sleep(delay)
                
            except KeyboardInterrupt:
                print("\n[WARN] Interrupted by user")
                break
            except Exception as e:
                errors += 1
                if i % 10 == 1 or i == len(all_queries):
                    error_str = str(e).lower()
                    if '429' in error_str or 'too many' in error_str:
                        print("rate-limit", flush=True)
                    elif 'timeout' in error_str:
                        print("timeout", flush=True)
                    else:
                        print("error", flush=True)
                time.sleep(delay * 2)  # Double delay on error
                continue
        
        # Save remaining results
        if repo_results:
            saved = save_results(db, repo_results)
            print(f"\n[FINAL] Saved {saved} files from {repo_name}")
        
        print(f"[STATS] Errors: {errors}/{len(all_queries)}")
        return len(repo_results)
        
    except Exception as e:
        print(f"[ERROR] {repo_name} failed: {e}")
        return 0

def main():
    print("="*80)
    print("FULL QDA SEARCH - ALL QUERIES, ALL REPOSITORIES")
    print("="*80)
    
    db = MetadataDatabase()
    print(f"\n[DB] Database: {db.db_path}")
    
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM files")
    start_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM files WHERE is_qda_file = 1")
    start_qda = cursor.fetchone()[0]
    print(f"[DB] Starting: {start_count} total files, {start_qda} QDA files")
    
    for i, (repo_name, scraper_class, delay) in enumerate(REPOSITORIES, 1):
        print(f"\n[{i}/{len(REPOSITORIES)}] Starting {repo_name}...")
        search_repository(repo_name, scraper_class, db, delay)
        
        if i < len(REPOSITORIES):
            print(f"[WAIT] Pausing 10s before next repository...")
            time.sleep(10)
    
    cursor.execute("SELECT COUNT(*) FROM files")
    end_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM files WHERE is_qda_file = 1")
    end_qda = cursor.fetchone()[0]
    
    print(f"\n{'='*80}")
    print("FINAL SUMMARY")
    print(f"{'='*80}")
    print(f"[DB] Total files: {start_count} -> {end_count} (+{end_count - start_count})")
    print(f"[DB] QDA files: {start_qda} -> {end_qda} (+{end_qda - start_qda})")
    print(f"[DONE] Search complete!")
    
    db.close()

if __name__ == "__main__":
    main()

