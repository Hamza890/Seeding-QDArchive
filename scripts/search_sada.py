#!/usr/bin/env python3
"""Search SADA repository with all queries."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import time
import json
from src.scrapers import SADAScraper
from src.database import MetadataDatabase
from src.search_utils import get_result_identity, load_all_queries as shared_load_all_queries, save_results

def load_all_queries():
    """Load all extensions and smart queries."""
    return shared_load_all_queries()

def main():
    print("="*80)
    print("SEARCHING: SADA")
    print("="*80)
    
    db = MetadataDatabase()
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM files")
    start_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM files WHERE source_repository LIKE '%SADA%'")
    start_repo = cursor.fetchone()[0]
    print(f"[DB] Total files in database: {start_count}")
    print(f"[DB] SADA files: {start_repo}")
    
    queries = load_all_queries()
    print(f"[INFO] Total queries: {len(queries)}")
    print(f"[INFO] Delay: 2.0s per query")
    print(f"[INFO] Estimated time: ~{len(queries) * 2.0 / 60:.1f} minutes")
    
    scraper = SADAScraper()
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
                saved = save_results(db, results, log_prefix="[CHECKPOINT]")
                print(f"[CHECKPOINT] Saved {saved} files")
                results = []
                seen_ids.clear()
            
            time.sleep(2.0)
            
        except KeyboardInterrupt:
            print("\n[STOP] Interrupted by user")
            break
        except Exception as e:
            if i % 10 == 1:
                print("error", flush=True)
            time.sleep(2.0 + 1.0)
    
    # Save remaining
    if results:
        saved = save_results(db, results, log_prefix="[FINAL]")
        print(f"\n[FINAL] Saved {saved} files")

    cursor.execute("SELECT COUNT(*) FROM files")
    end_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM files WHERE source_repository LIKE '%SADA%'")
    end_repo = cursor.fetchone()[0]

    print(f"\n{'='*80}")
    print(f"[DONE] Total files: {start_count} -> {end_count} (+{end_count - start_count})")
    print(f"[DONE] SADA files: {start_repo} -> {end_repo} (+{end_repo - start_repo})")
    
    db.close()

if __name__ == "__main__":
    main()
