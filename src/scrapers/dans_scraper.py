"""
Scraper for DANS (Data Archiving and Networked Services).

DANS migrated from their legacy EASY/OAI-PMH platform to a new Dataverse-based
"Data Station" architecture.  The Social Sciences and Humanities station is the
primary destination for qualitative research data:
    https://ssh.datastations.nl

The old endpoint (easy.dans.knaw.nl/oai) now returns an HTML page, which
caused the previous XML parser to fail with "mismatched tag" errors.

Performance note
----------------
The DANS server is slow when handling individual ``datasets/:persistentId``
calls (the secondary lookup done by the base DataverseScraper for every
dataset result). This override searches ``type=dataset`` only and builds
metadata *directly* from the search result fields, avoiding the expensive
secondary API call entirely.
"""
import time
import requests
from typing import List, Dict, Any, Optional
from .dataverse_scraper import DataverseScraper


class DANSScraper(DataverseScraper):
    """Scraper for DANS Data Station (SSH) — Dataverse-based."""

    # Smaller page size keeps each request fast on the slow DANS server.
    _PAGE_SIZE = 25

    def __init__(self, config_path: str = "config/qda_extensions.json"):
        """Initialize DANS scraper pointing at the SSH Data Station."""
        super().__init__(
            base_url="https://ssh.datastations.nl",
            config_path=config_path,
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def search(
        self,
        query: Optional[str] = None,
        max_results: int = 100,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """Search DANS Data Station for files and datasets matching *query*.

        Two search passes are made — both without any secondary API call:

        1. ``type=file``   — finds individual files whose *name* matches the
           query term (e.g. "qdpx", "nvp", "MaxQDA").  Only files whose
           extension is recognised as a QDA format are kept.
        2. ``type=dataset`` — finds datasets whose metadata matches the query.
           Metadata is built directly from the search result (title, DOI,
           authors, subjects) without calling ``datasets/:persistentId``.

        Args:
            query: Search term (defaults to "qualitative" when omitted).
            max_results: Maximum number of records to return across both passes.
            **kwargs: Extra params forwarded to the API (e.g. ``fq``).

        Returns:
            List of normalised metadata dicts.
        """
        self.clear_results()

        q = query or "qualitative"

        # Only search type=file for single-token queries (extensions / software
        # names like "qdpx", "NVivo").  Phrase queries ("qualitative interview")
        # rarely match file names and would page through thousands of PDFs.
        is_phrase = " " in q.strip()
        if not is_phrase:
            half = max_results // 2 or max_results
            self._search_by_type(q, "file", half, max_file_pages=5, **kwargs)

        remaining = max_results - len(self.results)
        if remaining > 0:
            self._search_by_type(q, "dataset", remaining, **kwargs)

        return self.results

    # ------------------------------------------------------------------
    # Internal search helper
    # ------------------------------------------------------------------

    def _search_by_type(
        self,
        q: str,
        search_type: str,
        limit: int,
        max_file_pages: int = 999,
        **kwargs,
    ) -> None:
        """Paginate through DANS search results for *search_type* and append to self.results."""
        start = 0
        fetched = 0
        pages_fetched = 0

        while fetched < limit and pages_fetched < max_file_pages:
            params: Dict[str, Any] = {
                "q": q,
                "type": search_type,
                "per_page": self._PAGE_SIZE,
                "start": start,
            }
            params.update(kwargs)

            try:
                url = f"{self.api_base}/search"
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                if data.get("status") != "OK":
                    break

                items = data.get("data", {}).get("items", [])
                if not items:
                    break

                for item in items:
                    if fetched >= limit:
                        break
                    if search_type == "file":
                        meta = self._file_item_to_metadata(item)
                        if meta is None:
                            continue  # skip non-QDA files
                    else:
                        meta = self._dataset_item_to_metadata(item)
                    self.results.append(meta)
                    fetched += 1

                start += self._PAGE_SIZE
                pages_fetched += 1
                time.sleep(0.5)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching from DANS (q={q!r}, type={search_type}): {e}")
                break

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _file_item_to_metadata(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert a file search result to normalised metadata.

        Returns *None* if the file is not a recognised QDA format.
        """
        file_name = item.get("name", "")
        if not self.is_qda_file(file_name):
            return None

        file_extension = ("." + file_name.rsplit(".", 1)[-1]) if "." in file_name else ""
        file_id = str(item.get("file_id", item.get("entity_id", "")))
        dataset_pid = item.get("dataset_persistent_id", "")
        download_url = item.get("url", f"{self.api_base}/access/datafile/{file_id}" if file_id else "")

        return self.normalize_metadata({
            "filename": file_name,
            "file_extension": file_extension.lower(),
            "file_size": item.get("size_in_bytes"),
            "download_url": download_url,
            "source_repository": "DANS",
            "source_url": f"{self.base_url}/dataset.xhtml?persistentId={dataset_pid}",
            "source_id": file_id or dataset_pid,
            "license_type": "",
            "license_url": "",
            "project_title": item.get("dataset_name", ""),
            "project_description": item.get("description", ""),
            "authors": "",
            "publication_date": item.get("published_at", ""),
            "keywords": "",
            "doi": dataset_pid,
            "qda_software": self.get_qda_software(file_name),
        })

    def _dataset_item_to_metadata(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a single dataset search-result item to normalised metadata."""
        doi = item.get("global_id", "")
        dataset_url = item.get("url", "")
        authors = "; ".join(item.get("authors", []))
        subjects = "; ".join(item.get("subjects", []))
        title = item.get("name", "")
        description = item.get("description", "")
        published_at = item.get("published_at", "")

        # Derive a stable synthetic filename from the DOI so dedup works.
        safe_doi = doi.replace("doi:", "").replace("/", "_").replace(".", "_")
        filename = f"{safe_doi}.dataset" if safe_doi else "dans_dataset.dataset"

        return self.normalize_metadata({
            "filename": filename,
            "file_extension": ".dataset",
            "file_size": None,
            "download_url": dataset_url,
            "source_repository": "DANS",
            "source_url": dataset_url,
            "source_id": doi,
            "license_type": "",
            "license_url": "",
            "project_title": title,
            "project_description": description,
            "authors": authors,
            "publication_date": published_at,
            "keywords": subjects,
            "doi": doi,
            "qda_software": "",
        })


