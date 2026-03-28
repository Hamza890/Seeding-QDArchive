import json
import tempfile
import unittest
from pathlib import Path

from src.search_utils import load_all_queries, load_smart_queries


class SearchQueryLoadingTests(unittest.TestCase):
    def make_config_dir(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        config_dir = Path(temp_dir.name)

        (config_dir / 'qda_extensions.json').write_text(
            json.dumps(
                {
                    'all_extensions': ['.qdpx', '.nvpx', '.qdpx'],
                }
            ),
            encoding='utf-8',
        )
        (config_dir / 'smart_queries.json').write_text(
            json.dumps(
                {
                    'qualitative_methods': {
                        'queries': ['qualitative research', 'shared query'],
                    },
                    'multilingual_terms': {
                        'description': 'Nested multilingual terms',
                        'german': ['qualitative Daten', 'shared query'],
                        'spanish': ['datos cualitativos'],
                    },
                    'priority_queries': {
                        'tier_1_extensions': ['priority-only'],
                    },
                }
            ),
            encoding='utf-8',
        )
        return config_dir

    def test_load_smart_queries_includes_multilingual_terms(self):
        config_dir = self.make_config_dir()

        queries = load_smart_queries(config_dir=config_dir)

        self.assertIn('qualitative research', queries)
        self.assertIn('qualitative Daten', queries)
        self.assertIn('datos cualitativos', queries)
        self.assertEqual(queries.count('shared query'), 1)
        self.assertNotIn('priority-only', queries)

    def test_load_all_queries_combines_extensions_and_multilingual_terms(self):
        config_dir = self.make_config_dir()

        queries = load_all_queries(config_dir=config_dir)

        self.assertIn('qdpx', queries)
        self.assertIn('nvpx', queries)
        self.assertNotIn('.qdpx', queries)
        self.assertIn('qualitative Daten', queries)
        self.assertIn('datos cualitativos', queries)
        self.assertEqual(queries.count('shared query'), 1)
