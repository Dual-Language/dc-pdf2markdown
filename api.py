from flask import Blueprint, request, send_file, jsonify
from werkzeug.utils import secure_filename
import tempfile
import os
import zipfile
from pathlib import Path
from service import PDF2MarkdownWorker
from logger import get_logger

api = Blueprint('api', __name__)

@api.route('/convert', methods=['POST'])
def convert_pdf():
    """
    Convert PDF to Markdown and return a zip with markdown, images, and metadata.
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
        200:
            description: Zipped result with markdown, images, and metadata
            schema:
                type: file
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
    # Use the storage directory for temp output
    from main import STORAGE_ROOT
    import uuid
    temp_id = str(uuid.uuid4())
    temp_dir = Path(STORAGE_ROOT) / f"api_job_{temp_id}"
    temp_dir.mkdir(exist_ok=True)
    try:
        pdf_path = temp_dir / filename
        file.save(pdf_path)
        # Prepare output paths
        book_id = pdf_path.stem
        output_dir = temp_dir / book_id
        output_dir.mkdir(exist_ok=True)
        worker = PDF2MarkdownWorker(output_dir)
        # Use the same logic as process_pdf, but for this single file
        image_dir_path = output_dir / "images"
        image_dir_path.mkdir(exist_ok=True)
        converter = worker.converter
        md_path = output_dir / f"{book_id}.md"
        meta_path = output_dir / "bookmetadata.json"
        conversion_metadata = converter.convert_pdf_to_markdown(str(pdf_path), str(md_path), image_dir_path, book_id)
        # Write metadata
        with open(meta_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(conversion_metadata, f, indent=2)
        # Zip everything
        zip_path = temp_dir / f"{book_id}_result.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(md_path, arcname=f"{book_id}.md")
            zipf.write(meta_path, arcname="bookmetadata.json")
            if image_dir_path.exists():
                for img_file in image_dir_path.iterdir():
                    zipf.write(img_file, arcname=f"images/{img_file.name}")
        # Ensure the zip file is closed before sending
        response = send_file(str(zip_path), as_attachment=True, download_name=f"{book_id}_result.zip")
        # After sending, schedule deletion of the temp files
        from flask import after_this_request
        @after_this_request
        def cleanup(response):
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except Exception as cleanup_err:
                logger.warning(f"Could not clean up temp dir {temp_dir}: {cleanup_err}")
            return response
        return response
    except Exception as e:
        logger.error_with_error(f"Error in /convert: {e}", e)
        # Clean up on error
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        return jsonify({'error': str(e)}), 500
