"""
Main entry point for QDA Archive pipeline.
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from pipeline import QDAPipeline


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='QDA Archive Pipeline - Collect and download qualitative data analysis files'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for QDA files')
    search_parser.add_argument(
        '--scraper',
        type=str,
        choices=[
            'zenodo', 'dryad', 'dataverse_no', 'dans', 'syracuse_qdr',
            'uk_data_service', 'qualidata', 'qualiservice', 'qualibi', 'all'
        ],
        default='all',
        help='Which scraper to run'
    )
    search_parser.add_argument(
        '--max-results',
        type=int,
        default=50,
        help='Maximum results per scraper'
    )
    search_parser.add_argument(
        '--download',
        action='store_true',
        help='Download files immediately after finding them'
    )
    search_parser.add_argument(
        '--query',
        type=str,
        help='Search query (optional)'
    )
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download pending files')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export metadata to CSV')
    export_parser.add_argument(
        '--output',
        type=str,
        default='metadata_export.csv',
        help='Output CSV file path'
    )
    export_parser.add_argument(
        '--filter-status',
        type=str,
        help='Filter by download status'
    )
    export_parser.add_argument(
        '--filter-repository',
        type=str,
        help='Filter by source repository'
    )
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show archive statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize pipeline
    pipeline = QDAPipeline()
    
    try:
        if args.command == 'search':
            if args.scraper == 'all':
                pipeline.run_all_scrapers(
                    max_results_per_scraper=args.max_results,
                    download=args.download
                )
            else:
                kwargs = {}
                if args.query:
                    kwargs['query'] = args.query
                
                pipeline.run_scraper(
                    args.scraper,
                    max_results=args.max_results,
                    download=args.download,
                    **kwargs
                )
        
        elif args.command == 'download':
            pipeline.download_pending_files()
        
        elif args.command == 'export':
            filters = {}
            if args.filter_status:
                filters['download_status'] = args.filter_status
            if args.filter_repository:
                filters['source_repository'] = args.filter_repository
            
            pipeline.export_metadata(args.output)
        
        elif args.command == 'stats':
            pipeline.print_statistics()
    
    finally:
        pipeline.close()


if __name__ == '__main__':
    main()

