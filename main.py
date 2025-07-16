#!/usr/bin/env python3
"""
PDF to Markdown Converter Service (Console Version)
Main loop and job orchestration only (Single Responsibility Principle).
"""

import os
import time
from pathlib import Path
from service import PDF2MarkdownWorker
from logger import get_logger
from event_logger import write_service_event

DEFAULT_STORAGE_ROOT = Path("../storage")
STORAGE_ROOT = Path(os.environ.get("STORAGE_ROOT", str(DEFAULT_STORAGE_ROOT))).resolve()

if __name__ == "__main__":
    logger = get_logger(STORAGE_ROOT)
    logger.info(f"Using storage root: {STORAGE_ROOT}")
    try:
        logger.info("About to create PDF2MarkdownWorker instance.")
        worker = PDF2MarkdownWorker(STORAGE_ROOT)
        logger.info("PDF2MarkdownWorker instance created successfully.")
        logger.info("Starting PDF2MarkdownWorker loop...")
        while True:
            found_job = False
            for guid_dir, pdf_path in worker.find_jobs():
                found_job = True
                # Log service-start event for this book/job
                write_service_event("service-start", str(guid_dir), "pdf2markdown", storage_root=str(STORAGE_ROOT))
                try:
                    worker.process_pdf(guid_dir, pdf_path)
                    # Log service-stop event on success
                    write_service_event("service-stop", str(guid_dir), "pdf2markdown", storage_root=str(STORAGE_ROOT), result="success")
                except Exception as e:
                    # Log service-stop event on error
                    write_service_event("service-stop", str(guid_dir), "pdf2markdown", storage_root=str(STORAGE_ROOT), result="error", error=str(e))
                    logger.error_with_error(f"Error processing {guid_dir}: {e}", e)
            if not found_job:
                logger.info("No jobs found. Sleeping...")
            time.sleep(10)
    except Exception as e:
        logger.error_with_error(f"Fatal error in main: {e}", e)
        raise