"""
Download manager for QDA files with metadata tracking.
"""
import os
import hashlib
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import time


class DownloadManager:
    """Manages file downloads with retry logic and metadata tracking."""
    
    def __init__(self, download_dir: str = "downloads", chunk_size: int = 8192):
        """
        Initialize download manager.
        
        Args:
            download_dir: Directory to save downloaded files
            chunk_size: Size of chunks for streaming downloads
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.chunk_size = chunk_size
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QDA-Archive-Bot/1.0 (Research Data Collection)'
        })
    
    def download_file(
        self, 
        url: str, 
        filename: Optional[str] = None,
        subfolder: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Download a file from URL with retry logic.
        
        Args:
            url: URL to download from
            filename: Optional custom filename
            subfolder: Optional subfolder within download_dir
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with download metadata
        """
        result = {
            'success': False,
            'url': url,
            'filename': None,
            'file_path': None,
            'file_size': None,
            'md5_hash': None,
            'sha256_hash': None,
            'download_date': datetime.now().isoformat(),
            'error_message': None
        }
        
        # Determine filename
        if not filename:
            filename = self._extract_filename_from_url(url)
        
        # Create full path
        if subfolder:
            save_dir = self.download_dir / subfolder
            save_dir.mkdir(parents=True, exist_ok=True)
        else:
            save_dir = self.download_dir
        
        file_path = save_dir / filename
        
        # Download with retries
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, stream=True, timeout=timeout)
                response.raise_for_status()
                
                # Get file size from headers
                file_size = int(response.headers.get('content-length', 0))
                
                # Download and compute hashes
                md5_hash = hashlib.md5()
                sha256_hash = hashlib.sha256()
                downloaded_size = 0
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        if chunk:
                            f.write(chunk)
                            md5_hash.update(chunk)
                            sha256_hash.update(chunk)
                            downloaded_size += len(chunk)
                
                # Update result
                result['success'] = True
                result['filename'] = filename
                result['file_path'] = str(file_path)
                result['file_size'] = downloaded_size
                result['md5_hash'] = md5_hash.hexdigest()
                result['sha256_hash'] = sha256_hash.hexdigest()
                
                return result
                
            except requests.exceptions.RequestException as e:
                result['error_message'] = str(e)
                
                if attempt < max_retries - 1:
                    # Wait before retry (exponential backoff)
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    # Final attempt failed
                    if file_path.exists():
                        file_path.unlink()  # Remove partial download
        
        return result
    
    def _extract_filename_from_url(self, url: str) -> str:
        """Extract filename from URL."""
        from urllib.parse import urlparse, unquote
        
        parsed = urlparse(url)
        filename = unquote(parsed.path.split('/')[-1])
        
        if not filename or '.' not in filename:
            # Generate filename from URL hash
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"file_{url_hash}.dat"
        
        return filename
    
    def verify_file(self, file_path: str, expected_hash: str, hash_type: str = 'md5') -> bool:
        """
        Verify file integrity using hash.
        
        Args:
            file_path: Path to file
            expected_hash: Expected hash value
            hash_type: Type of hash ('md5' or 'sha256')
            
        Returns:
            True if hash matches, False otherwise
        """
        if hash_type == 'md5':
            hasher = hashlib.md5()
        elif hash_type == 'sha256':
            hasher = hashlib.sha256()
        else:
            raise ValueError(f"Unsupported hash type: {hash_type}")
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(self.chunk_size), b''):
                hasher.update(chunk)
        
        return hasher.hexdigest() == expected_hash
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about a downloaded file."""
        path = Path(file_path)
        
        if not path.exists():
            return {'exists': False}
        
        # Compute hashes
        md5_hash = hashlib.md5()
        sha256_hash = hashlib.sha256()
        
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(self.chunk_size), b''):
                md5_hash.update(chunk)
                sha256_hash.update(chunk)
        
        return {
            'exists': True,
            'filename': path.name,
            'file_path': str(path),
            'file_size': path.stat().st_size,
            'md5_hash': md5_hash.hexdigest(),
            'sha256_hash': sha256_hash.hexdigest(),
            'modified_time': datetime.fromtimestamp(path.stat().st_mtime).isoformat()
        }

