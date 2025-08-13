from flask import Blueprint, request, send_file, jsonify
from werkzeug.utils import secure_filename
import zipfile
from pathlib import Path
from logger import get_logger

api = Blueprint('api', __name__)

import uuid
import json

@api.route('/convert', methods=['POST'])
def submit_pdf_job():
    """
    Submit a PDF file for conversion. Returns a job_id for status tracking and download.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: The PDF file to upload
    responses:
        202:
            description: Job accepted, returns job_id
            schema:
                type: object
                properties:
                    job_id:
                        type: string
        400:
            description: Bad request
        500:
            description: Internal server error
    """
    logger = get_logger()
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    from main import STORAGE_ROOT
    job_id = str(uuid.uuid4())
    job_dir = Path(STORAGE_ROOT) / job_id
    job_dir.mkdir(exist_ok=True)
    pdf_path = job_dir / filename
    file.save(pdf_path)
    # Optionally, write a job metadata file
    meta = {"status": "pending", "filename": filename}
    with open(job_dir / "job.json", "w", encoding="utf-8") as f:
        json.dump(meta, f)
    logger.info(f"Job {job_id} submitted with file {filename}")
    return jsonify({"job_id": job_id}), 202

# Endpoint to check job status
@api.route('/job_status/<job_id>', methods=['GET'])
def job_status(job_id):
    """
    Check the status of a submitted job.
    ---
    parameters:
      - in: path
        name: job_id
        type: string
        required: true
        description: The job ID to check
    responses:
        200:
            description: Job status
            schema:
                type: object
                properties:
                    job_id:
                        type: string
                    status:
                        type: string
        404:
            description: Job not found
    """
    from main import STORAGE_ROOT
    job_dir = Path(STORAGE_ROOT) / job_id
    progress_path = job_dir / "pdf2markdown-progress.json"
    if not job_dir.exists():
        return jsonify({"error": "Job not found"}), 404
    if progress_path.exists():
        with open(progress_path, "r", encoding="utf-8") as f:
            progress = json.load(f)
        status = progress.get("status", "pending")
    else:
        status = "pending"
    return jsonify({"job_id": job_id, "status": status})

# Endpoint to download result zip
@api.route('/download/<job_id>', methods=['GET'])
def download_result(job_id):
    """
    Download the result zip for a completed job.
    ---
    parameters:
      - in: path
        name: job_id
        type: string
        required: true
        description: The job ID to download
    responses:
        200:
            description: Zipped result with markdown, images, and metadata
            schema:
                type: file
        404:
            description: Job not found or result not ready
    """
    from main import STORAGE_ROOT
    job_dir = Path(STORAGE_ROOT) / job_id
    if not job_dir.exists():
        return jsonify({"error": "Job not found"}), 404
    # Find the .md file and images dir
    md_files = list(job_dir.glob("*.md"))
    if not md_files:
        return jsonify({"error": "Result not ready"}), 404
    book_id = md_files[0].stem
    zip_path = job_dir / f"{book_id}_result.zip"
    # If zip does not exist, create it
    if not zip_path.exists():
        meta_path = job_dir / "bookmetadata.json"
        image_dir_path = job_dir / "images"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(md_files[0], arcname=f"{book_id}.md")
            if meta_path.exists():
                zipf.write(meta_path, arcname="bookmetadata.json")
            if image_dir_path.exists():
                for img_file in image_dir_path.iterdir():
                    zipf.write(img_file, arcname=f"images/{img_file.name}")
    return send_file(str(zip_path), as_attachment=True, download_name=f"{book_id}_result.zip")
