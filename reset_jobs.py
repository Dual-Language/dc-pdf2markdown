#!/usr/bin/env python3
"""
Reset PDF to Markdown processing status for all jobs
This script removes progress files to allow reprocessing of existing PDFs
"""

import os
import json
from pathlib import Path

def reset_pdf2markdown_jobs(storage_root):
    """Reset all pdf2markdown jobs by removing progress files"""
    storage_path = Path(storage_root)
    if not storage_path.exists():
        print(f"Storage path does not exist: {storage_root}")
        return
    
    print(f"Scanning storage directory: {storage_root}")
    
    reset_count = 0
    for job_dir in storage_path.iterdir():
        if not job_dir.is_dir():
            continue
            
        # Check if this job has an originalbook.pdf
        pdf_file = job_dir / "originalbook.pdf"
        if not pdf_file.exists():
            continue
            
        # Check if there's a progress file
        progress_file = job_dir / "pdf2markdown-progress.json"
        if progress_file.exists():
            print(f"Resetting job: {job_dir.name}")
            try:
                # Remove the progress file to trigger reprocessing
                progress_file.unlink()
                reset_count += 1
                print(f"  Removed progress file for {job_dir.name}")
            except Exception as e:
                print(f"  Error removing progress file for {job_dir.name}: {e}")
        else:
            print(f"Job {job_dir.name} has no progress file - will be processed")
    
    print(f"\nReset {reset_count} jobs for reprocessing")
    return reset_count

if __name__ == "__main__":
    # Use the storage directory relative to the script location
    storage_root = Path(__file__).parent.parent / "storage"
    reset_pdf2markdown_jobs(storage_root)
