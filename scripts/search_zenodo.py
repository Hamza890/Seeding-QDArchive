#!/usr/bin/env python3
"""Search Zenodo repository with all queries (with rate limiting)."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import time
from src.scrapers import ZenodoScraper
from src.database import MetadataDatabase
from src.search_utils import get_result_identity, load_all_queries as shared_load_all_queries, save_results

def load_all_queries():
    """Load all extensions and smart queries."""
    return shared_load_all_queries()

def main():
    print("="*80)
    print("SEARCHING: Zenodo (with 5s delay for rate limiting)")
    print("="*80)
    
    db = MetadataDatabase()
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM files")
    start_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM files WHERE source_repository LIKE '%Zenodo%'")
    start_repo = cursor.fetchone()[0]
    print(f"[DB] Total files in database: {start_count}")
    print(f"[DB] Zenodo files: {start_repo}")
    
    queries = load_all_queries()
    print(f"[INFO] Total queries: {len(queries)}")
    print(f"[INFO] Delay: 5.0s per query (to avoid rate limiting)")
    print(f"[INFO] Estimated time: ~{len(queries) * 5 / 60:.1f} minutes")
    
    scraper = ZenodoScraper()
    results = []
    seen_ids = set()
    rate_limit_count = 0
    
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
            
            # Save every 20 queries (keep seen_ids intact so dedup spans the whole run)
            if i % 20 == 0 and results:
                saved = save_results(db, results, log_prefix="[CHECKPOINT]")
                print(f"[CHECKPOINT] Saved {saved} files (rate limits: {rate_limit_count})")
                results = []
            
            time.sleep(5.0)
            
        except KeyboardInterrupt:
            print("\n[STOP] Interrupted by user")
            break
        except Exception as e:
            if '429' in str(e) or 'too many' in str(e).lower():
                rate_limit_count += 1
                if i % 10 == 1:
                    print("rate-limit", flush=True)
                time.sleep(10.0)  # Extra delay on rate limit
            else:
                if i % 10 == 1:
                    print("error", flush=True)
                time.sleep(5.0)
    
    # Save remaining
    if results:
        saved = save_results(db, results, log_prefix="[FINAL]")
        print(f"\n[FINAL] Saved {saved} files")
    
    cursor.execute("SELECT COUNT(*) FROM files")
    end_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM files WHERE source_repository LIKE '%Zenodo%'")
    end_repo = cursor.fetchone()[0]
    
    print(f"\n{'='*80}")
    print(f"[DONE] Total files: {start_count} -> {end_count} (+{end_count - start_count})")
    print(f"[DONE] Zenodo files: {start_repo} -> {end_repo} (+{end_repo - start_repo})")
    print(f"[INFO] Rate limit errors: {rate_limit_count}")
    
    db.close()

if __name__ == "__main__":
    main()

