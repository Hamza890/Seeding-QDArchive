# Quick Start Guide

Get started with the QDA Archive pipeline in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Run Your First Search

Search Zenodo for 10 QDA files:

```bash
python main.py search --scraper zenodo --max-results 10
```

This will:
- Search Zenodo for QDA files
- Save metadata to the database (`qda_archive.db`)
- Display found files

## Step 3: View Statistics

```bash
python main.py stats
```

You'll see:
- Total files found
- Files by status (pending/completed/failed)
- Files by repository
- Files by extension

## Step 4: Download Files

Download the files you found:

```bash
python main.py download
```

Files will be downloaded to the `downloads/` directory, organized by repository.

## Step 5: Export Metadata

Export metadata to CSV for analysis:

```bash
python main.py export --output my_archive.csv
```

## Next Steps

### Search Multiple Repositories

```bash
python main.py search --scraper all --max-results 50
```

### Search and Download in One Step

```bash
python main.py search --scraper zenodo --max-results 20 --download
```

### Search with Custom Query

```bash
python main.py search --scraper zenodo --query "interview data" --max-results 30
```

### Filter Exports

Export only completed downloads:
```bash
python main.py export --output completed.csv --filter-status completed
```

Export only Zenodo files:
```bash
python main.py export --output zenodo.csv --filter-repository Zenodo
```

## Available Scrapers

- `zenodo` - Zenodo repository
- `dryad` - Dryad repository
- `dataverse_no` - DataverseNO
- `uk_data_service` - UK Data Service
- `syracuse_qdr` - Syracuse QDR
- `all` - Run all scrapers

## Tips

1. **Start small**: Begin with `--max-results 10` to test
2. **Check licenses**: Always verify license information in the exported CSV
3. **Monitor progress**: Use `python main.py stats` to track your archive
4. **Backup database**: The `qda_archive.db` file contains all metadata

## Troubleshooting

### No files found?
- Try different scrapers
- Use custom queries
- Some repositories may have rate limits

### Download failed?
- Check your internet connection
- Some files may require authentication
- Check the error message in the database

### Database locked?
- Close any other programs accessing the database
- Only one pipeline instance can run at a time

## Example Workflow

```bash
# 1. Search all repositories
python main.py search --scraper all --max-results 100

# 2. Check what was found
python main.py stats

# 3. Download files
python main.py download

# 4. Export metadata
python main.py export --output archive_metadata.csv

# 5. Check statistics again
python main.py stats
```

## Programmatic Usage

See `examples/basic_usage.py` for examples of using the pipeline in your own Python scripts.

```python
from pipeline import QDAPipeline

pipeline = QDAPipeline()
results = pipeline.run_scraper('zenodo', max_results=10)
pipeline.export_metadata('output.csv')
pipeline.close()
```

## Need Help?

- Check the main README.md for detailed documentation
- Review the examples in the `examples/` directory
- Check the configuration files in `config/`

