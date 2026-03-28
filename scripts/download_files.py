#!/usr/bin/env python3
"""
Download files from the database organised by repository and project.

Folder hierarchy:
    downloads/
    └── <repository>/
        └── <project_title>/
            ├── <file1>
            ├── <file2>
            └── links.txt   ← for access-controlled repos (ICPSR, UKDS)

Usage:
    # Download everything that is directly downloadable
    python scripts/download_files.py

    # Limit to specific repositories
    python scripts/download_files.py --repos Zenodo "Harvard Dataverse" SyracuseQDR

    # Include ICPSR / UKDS (creates links.txt files instead of downloading)
    python scripts/download_files.py --repos ICSPR UKDataService

    # Change output folder
    python scripts/download_files.py --output my_downloads
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import argparse
import re
import time
import requests
from pathlib import Path
from collections import defaultdict
from src.database import MetadataDatabase

# Repositories where files sit behind a login wall.
# We can't download them automatically; we save a links.txt instead.
ACCESS_CONTROLLED = {'icspr', 'ukdataservice', 'ukds'}

# Placeholder extensions written by scrapers when no real file exists
PLACEHOLDER_EXTENSIONS = {'.study', '.dataset'}


def safe_name(text: str, max_len: int = 80) -> str:
    """Turn arbitrary text into a safe folder / file name (Windows-compatible)."""
    text = re.sub(r'[\\/:*?"<>|]', '_', text or 'Unknown')
    text = re.sub(r'\s+', ' ', text).strip()
    text = text[:max_len]
    # Windows forbids names ending with a space or a dot
    text = text.rstrip(' .')
    return text or 'Unknown'


def is_access_controlled(repo: str) -> bool:
    return repo.lower().replace(' ', '') in ACCESS_CONTROLLED


def group_by_repo_and_project(files):
    """Return {repo: {project_title: [file_rows]}}."""
    grouped = defaultdict(lambda: defaultdict(list))
    for f in files:
        repo = f.get('source_repository') or 'Unknown'
        project = f.get('project_title') or f.get('filename') or 'Unknown'
        grouped[repo][project].append(f)
    return grouped


def download_file(url: str, dest: Path, session: requests.Session) -> bool:
    """Stream-download *url* to *dest*. Returns True on success."""
    try:
        resp = session.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, 'wb') as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                fh.write(chunk)
        return True
    except Exception as e:
        print(f"    [ERROR] {e}")
        return False


def write_links_file(project_dir: Path, files: list):
    """Write a links.txt with landing-page URLs for access-controlled studies."""
    project_dir.mkdir(parents=True, exist_ok=True)
    links_path = project_dir / 'links.txt'
    with open(links_path, 'w', encoding='utf-8') as fh:
        fh.write("# These studies require registration to access.\n")
        fh.write("# Visit each URL, create a free account, and request access.\n\n")
        seen = set()
        for f in files:
            url = f.get('download_url') or f.get('source_url') or ''
            doi = f.get('doi') or ''
            title = f.get('project_title') or f.get('filename') or ''
            if url and url not in seen:
                seen.add(url)
                fh.write(f"Title : {title}\n")
                if doi:
                    fh.write(f"DOI   : https://doi.org/{doi}\n")
                fh.write(f"URL   : {url}\n\n")
    return links_path


def main():
    parser = argparse.ArgumentParser(description="Download QDA archive files.")
    parser.add_argument('--repos', nargs='+', metavar='REPO',
                        help='Limit to these repository names (default: all downloadable)')
    parser.add_argument('--output', default='downloads',
                        help='Root output folder (default: downloads/)')
    parser.add_argument('--delay', type=float, default=0.5,
                        help='Seconds to wait between downloads (default: 0.5)')
    args = parser.parse_args()

    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)

    db = MetadataDatabase()
    all_files = db.get_all_files()
    db.close()

    # Filter by requested repos if given
    if args.repos:
        wanted = {r.lower() for r in args.repos}
        all_files = [f for f in all_files
                     if (f.get('source_repository') or '').lower() in wanted]

    grouped = group_by_repo_and_project(all_files)
    session = requests.Session()
    session.headers['User-Agent'] = 'QDA-Archive-Downloader/1.0'

    total_ok = total_skip = total_err = total_links = 0

    for repo, projects in sorted(grouped.items()):
        repo_dir = output_root / safe_name(repo)
        controlled = is_access_controlled(repo)
        print(f"\n{'='*70}")
        print(f"  {repo}  ({'access-controlled → links.txt' if controlled else 'downloading'})")
        print(f"{'='*70}")

        for project_title, files in sorted(projects.items()):
            project_dir = repo_dir / safe_name(project_title)

            if controlled:
                links_path = write_links_file(project_dir, files)
                total_links += 1
                print(f"  [LINKS] {project_dir.name}/ → links.txt ({len(files)} studies)")
                continue

            project_dir.mkdir(parents=True, exist_ok=True)
            for f in files:
                url = f.get('download_url') or ''
                filename = f.get('filename') or 'unknown'
                ext = (f.get('file_extension') or '').lower()

                if not url or ext in PLACEHOLDER_EXTENSIONS:
                    total_skip += 1
                    continue

                dest = project_dir / safe_name(filename, max_len=200)
                if dest.exists():
                    total_skip += 1
                    continue

                print(f"  ↓ {filename[:60]}", end=' ', flush=True)
                ok = download_file(url, dest, session)
                if ok:
                    total_ok += 1
                    print("✓")
                else:
                    total_err += 1
                time.sleep(args.delay)

    print(f"\n{'='*70}")
    print(f"  Downloaded : {total_ok}")
    print(f"  Skipped    : {total_skip}  (already exists or placeholder)")
    print(f"  Errors     : {total_err}")
    print(f"  Links files: {total_links}  (access-controlled repos)")
    print(f"  Output     : {output_root.resolve()}")


if __name__ == '__main__':
    main()

