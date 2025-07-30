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

# --- Flask server for health check ---
from flask import Flask, jsonify
import threading

DEFAULT_STORAGE_ROOT = Path("../storage")
STORAGE_ROOT = Path(os.environ.get("STORAGE_ROOT", str(DEFAULT_STORAGE_ROOT))).resolve()

# Flag to indicate if the worker loop has started
worker_loop_started = threading.Event()

app = Flask(__name__)

@app.route('/ping')
def ping():
    if worker_loop_started.is_set():
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({"status": "starting"}), 503

def run_worker():
    logger = get_logger(STORAGE_ROOT)
    logger.info(f"Using storage root: {STORAGE_ROOT}")
    try:
        logger.debug("About to create PDF2MarkdownWorker instance.")
        worker = PDF2MarkdownWorker(STORAGE_ROOT)
        logger.debug("PDF2MarkdownWorker instance created successfully.")
        logger.debug("Starting PDF2MarkdownWorker loop...")
        worker_loop_started.set()  # Indicate the worker loop has started
        while True:
            found_job = False
            for guid_dir, pdf_path in worker.find_jobs():
                found_job = True
                # Extract book_id from guid_dir
                book_id = Path(guid_dir).name
                # Log service-start event for this book/job
                write_service_event("service-start", book_id, "pdf2markdown", storage_root=str(STORAGE_ROOT))
                try:
                    worker.process_pdf(guid_dir, pdf_path)
                    # Log service-stop event on success
                    write_service_event("service-stop", book_id, "pdf2markdown", storage_root=str(STORAGE_ROOT), result="success")
                except Exception as e:
                    # Log service-stop event on error
                    write_service_event("service-stop", book_id, "pdf2markdown", storage_root=str(STORAGE_ROOT), result="error", error=str(e))
                    logger.error_with_error(f"Error processing {guid_dir}: {e}", e)
            if not found_job:
                logger.debug("No jobs found. Sleeping...")
            time.sleep(10)
    except Exception as e:
        logger.error_with_error(f"Fatal error in main: {e}", e)
        raise

def run_flask():
    app.run(host="0.0.0.0", port=3000)

if __name__ == "__main__":
    # Start the worker in a thread
    worker_thread = threading.Thread(target=run_worker, daemon=True)
    worker_thread.start()
    # Start Flask server in main thread (so container stops if Flask dies)
    run_flask()