"""
Base scraper class for all repository scrapers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from src.search_utils import get_result_identity


class BaseScraper(ABC):
    """Abstract base class for repository scrapers."""
    
    def __init__(self, config_path: str = "config/qda_extensions.json",
                 smart_queries_path: str = "config/smart_queries.json"):
        """
        Initialize scraper with QDA extensions configuration.

        Args:
            config_path: Path to QDA extensions configuration file
            smart_queries_path: Path to smart queries configuration file
        """
        self.config_path = config_path
        self.smart_queries_path = smart_queries_path
        self.qda_extensions = self._load_extensions()
        self.smart_queries = self._load_smart_queries()
        self._software_extension_map = self._build_software_extension_map()
        self.results = []
    
    def _load_extensions(self) -> List[str]:
        """Load QDA file extensions from configuration."""
        config_file = Path(self.config_path)

        if not config_file.exists():
            # Default extensions if config not found
            return [
                '.qdpx', '.qdc', '.mqda', '.nvp', '.nvpx',
                '.atlasproj', '.hpr7', '.ppj', '.pprj', '.qlt',
                '.f4p', '.qpd'
            ]

        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('all_extensions', [])

    def _load_smart_queries(self) -> Dict[str, Any]:
        """Load smart queries from configuration."""
        queries_file = Path(self.smart_queries_path)

        if not queries_file.exists():
            # Return empty dict if config not found
            return {}

        with open(queries_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def is_qda_file(self, filename: str) -> bool:
        """
        Check if filename has a QDA extension.
        
        Args:
            filename: Name of file to check
            
        Returns:
            True if file has QDA extension, False otherwise
        """
        filename_lower = filename.lower()
        return any(filename_lower.endswith(ext.lower()) for ext in self.qda_extensions)
    
    def _build_software_extension_map(self) -> dict:
        """Build a cached mapping of lowercase extension -> software name."""
        config_file = Path(self.config_path)
        if not config_file.exists():
            return {}
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        ext_map = {}
        for software, info in config.get('qda_software', {}).items():
            for ext in info.get('extensions', []):
                ext_map[ext.lower()] = software
        return ext_map

    def get_qda_software(self, filename: str) -> Optional[str]:
        """
        Determine QDA software based on file extension.

        Uses the cached extension map built at init time — no file I/O per call.

        Args:
            filename: Name of file

        Returns:
            Name of QDA software or None
        """
        filename_lower = filename.lower()
        for ext, software in self._software_extension_map.items():
            if filename_lower.endswith(ext):
                return software
        return None

    def get_all_search_queries(self, priority_only: bool = False) -> List[str]:
        """
        Get all search queries from smart queries configuration.

        Args:
            priority_only: If True, return only priority queries

        Returns:
            List of search query strings
        """
        if not self.smart_queries:
            return []

        if priority_only:
            # Return only priority queries
            priority = self.smart_queries.get('priority_queries', {})
            queries = []
            queries.extend(priority.get('tier_1_extensions', []))
            queries.extend(priority.get('tier_2_software', []))
            queries.extend(priority.get('tier_3_methods', []))
            return queries

        # Return all queries from all categories
        all_queries = []

        # Add extension queries
        all_queries.extend(self.smart_queries.get('qda_file_extensions', {}).get('queries', []))

        # Add software names
        all_queries.extend(self.smart_queries.get('qda_software_names', {}).get('queries', []))

        # Add qualitative methods
        all_queries.extend(self.smart_queries.get('qualitative_methods', {}).get('queries', []))

        # Add data types
        all_queries.extend(self.smart_queries.get('data_types', {}).get('queries', []))

        # Add coding terms
        all_queries.extend(self.smart_queries.get('coding_terms', {}).get('queries', []))

        # Add file type hints
        all_queries.extend(self.smart_queries.get('file_type_hints', {}).get('queries', []))

        # Add combined queries
        all_queries.extend(self.smart_queries.get('combined_queries', {}).get('queries', []))

        # Add multilingual terms
        multilingual = self.smart_queries.get('multilingual_terms', {})
        for lang, terms in multilingual.items():
            if lang != 'description' and isinstance(terms, list):
                all_queries.extend(terms)

        return all_queries

    def get_queries_by_category(self, category: str) -> List[str]:
        """
        Get search queries for a specific category.

        Args:
            category: Category name (e.g., 'qda_file_extensions', 'qualitative_methods')

        Returns:
            List of queries for that category
        """
        if not self.smart_queries:
            return []

        category_data = self.smart_queries.get(category, {})

        # Handle multilingual categories
        if category == 'multilingual_terms':
            queries = []
            for lang, terms in category_data.items():
                if lang != 'description' and isinstance(terms, list):
                    queries.extend(terms)
            return queries

        return category_data.get('queries', [])

    def is_qualitative_data(self, metadata: Dict[str, Any]) -> bool:
        """
        Check if metadata suggests qualitative data or QDA files.

        Args:
            metadata: Metadata dictionary to check

        Returns:
            True if appears to be qualitative data, False otherwise
        """
        # First check if it's a QDA file by extension
        filename = metadata.get('filename', '')
        if filename and self.is_qda_file(filename):
            return True

        # Check text fields for qualitative keywords
        text_to_check = ' '.join([
            str(metadata.get('project_title', '')),
            str(metadata.get('project_description', '')),
            str(metadata.get('keywords', '')),
            str(metadata.get('filename', ''))
        ]).lower()

        # Get all qualitative-related keywords
        keywords = []

        # Add software names
        keywords.extend([q.lower() for q in self.get_queries_by_category('qda_software_names')])

        # Add qualitative methods
        keywords.extend([q.lower() for q in self.get_queries_by_category('qualitative_methods')])

        # Add data types
        keywords.extend([q.lower() for q in self.get_queries_by_category('data_types')])

        # Add coding terms
        keywords.extend([q.lower() for q in self.get_queries_by_category('coding_terms')])

        # Add file type hints
        keywords.extend([q.lower() for q in self.get_queries_by_category('file_type_hints')])

        # Check if any keyword appears in the text
        return any(keyword in text_to_check for keyword in keywords)
    
    def search_with_smart_queries(
        self,
        priority_only: bool = True,
        max_results_per_query: int = 10,
        categories: Optional[List[str]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search repository using smart queries.

        Args:
            priority_only: If True, use only priority queries
            max_results_per_query: Maximum results per individual query
            categories: Specific categories to search (None = all)
            **kwargs: Additional search parameters

        Returns:
            List of unique metadata dictionaries for found files
        """
        all_results = []
        seen_ids = set()

        # Get queries to use
        if categories:
            queries = []
            for category in categories:
                queries.extend(self.get_queries_by_category(category))
        else:
            queries = self.get_all_search_queries(priority_only=priority_only)

        print(f"Searching with {len(queries)} smart queries...")

        for i, query in enumerate(queries, 1):
            try:
                print(f"  [{i}/{len(queries)}] Searching: '{query}'...", end=' ')

                # Call the repository-specific search method
                results = self.search(query=query, max_results=max_results_per_query, **kwargs)

                # Deduplicate based on source_id
                new_results = 0
                for result in results:
                    result_id = get_result_identity(result)
                    if result_id and result_id not in seen_ids:
                        seen_ids.add(result_id)
                        all_results.append(result)
                        new_results += 1

                if new_results > 0:
                    print(f"✅ {new_results} new results")
                else:
                    print("⚪ No new results")

            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}")
                continue

        print(f"\n📊 Total unique results: {len(all_results)}")

        # Store results
        self.results = all_results
        return all_results

    @abstractmethod
    def search(self, query: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Search repository for QDA files.

        Args:
            query: Optional search query
            **kwargs: Additional search parameters

        Returns:
            List of metadata dictionaries for found files
        """
        pass
    
    @abstractmethod
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific file.
        
        Args:
            file_id: Identifier for the file in the repository
            
        Returns:
            Dictionary with file metadata
        """
        pass
    
    def normalize_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize metadata to standard format.

        Args:
            raw_metadata: Raw metadata from repository

        Returns:
            Normalized metadata dictionary
        """
        # Base normalization - subclasses should override
        normalized = {
            'filename': raw_metadata.get('filename'),
            'file_extension': raw_metadata.get('file_extension'),
            'download_url': raw_metadata.get('download_url'),
            'source_repository': self.__class__.__name__.replace('Scraper', ''),
            'source_url': raw_metadata.get('source_url'),
            'source_id': raw_metadata.get('source_id'),
            'license_type': raw_metadata.get('license_type'),
            'license_url': raw_metadata.get('license_url'),
            'project_title': raw_metadata.get('project_title'),
            'project_description': raw_metadata.get('project_description'),
            'authors': raw_metadata.get('authors'),
            'publication_date': raw_metadata.get('publication_date'),
            'keywords': raw_metadata.get('keywords'),
            'doi': raw_metadata.get('doi'),
            'qda_software': raw_metadata.get('qda_software'),
            'is_qda_file': raw_metadata.get('is_qda_file', True),  # Default to True for backward compatibility
        }

        # Auto-detect if it's qualitative data
        normalized['is_qualitative_data'] = self.is_qualitative_data(normalized)

        return normalized
    
    def get_results(self) -> List[Dict[str, Any]]:
        """Get all search results."""
        return self.results
    
    def clear_results(self):
        """Clear stored results."""
        self.results = []
    
    def save_results(self, output_path: str):
        """
        Save results to JSON file.
        
        Args:
            output_path: Path to save results
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

