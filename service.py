import json
import base64
from pathlib import Path
from typing import Dict, Any
from marker.converters.pdf import PdfConverter
from model_utils import create_model_dict
from logger import get_logger

PROGRESS_FILENAME = "pdf2markdown-progress.json"
METADATA_FILENAME = "bookmetadata.json"

class MarkerPDFConverter:
    """Converts PDF files to Markdown format using Marker, with image extraction and metadata."""
    def __init__(self, extract_images: bool = True, image_dir: str = "images"):
        logger = get_logger()
        logger.info(f"MarkerPDFConverter __init__ starting: extract_images={extract_images}, image_dir={image_dir}")
        self.extract_images = extract_images
        logger.info("MarkerPDFConverter: extract_images set.")
        self.image_dir = Path(image_dir)
        logger.info("MarkerPDFConverter: image_dir Path object created.")
        if self.extract_images:
            self.image_dir.mkdir(exist_ok=True)
            logger.info("MarkerPDFConverter: image_dir created (if not exists).")
        try:
            self.converter = PdfConverter(artifact_dict=create_model_dict())
            logger.info("MarkerPDFConverter: PdfConverter created.")
        except Exception as e:
            logger.info(f"MarkerPDFConverter: PdfConverter creation failed with error: {e}")
            logger.error_with_error(f"Error creating PdfConverter: {e}", e)
            raise
        logger.info("MarkerPDFConverter __init__ completed.")

    def convert_pdf_to_markdown(self, pdf_path: str, output_path: str, image_dir_path: Path, book_id: str | None = None) -> dict:
        pdf_file = Path(pdf_path)
        output_file = Path(output_path)
        logger = get_logger()
        logger.info(f"Starting conversion: {pdf_file.name} -> {output_file.name}", book_id)
        try:
            rendered = self.converter(str(pdf_file))
            text = rendered.markdown
            metadata = rendered.metadata
            images = rendered.images
            image_count = 0
            image_paths = {}
            if self.extract_images and images:
                image_count, image_paths = self._save_images(images, image_dir_path, book_id)
            text = self._update_image_references(text, image_paths, book_id)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            conversion_metadata = {
                'total_pages': len(metadata.get('page_stats', [])),
                'total_images': image_count,
                'output_file': str(output_file),
                'image_directory': str(image_dir_path) if self.extract_images else None,
                'marker_metadata': metadata
            }
            logger.info("Conversion completed successfully!", book_id)
            logger.info(f"Conversion metadata: {conversion_metadata}", book_id)
            return conversion_metadata
        except Exception as e:
            logger.error_with_error(f"Error during conversion: {str(e)}", e, book_id)
            raise

    def _save_images(self, images: Dict[str, Any], image_dir_path: Path, book_id: str | None = None) -> tuple[int, Dict[str, str]]:
        image_count = 0
        image_paths = {}
        image_dir_path.mkdir(exist_ok=True)
        logger = get_logger()
        try:
            for image_id, image_data in images.items():
                try:
                    image_filename = image_id
                    image_path = image_dir_path / image_filename
                    if hasattr(image_data, 'save'):
                        if image_filename.lower().endswith('.png'):
                            image_format = 'PNG'
                        elif image_filename.lower().endswith(('.jpg', '.jpeg')):
                            image_format = 'JPEG'
                        else:
                            image_format = 'PNG'
                        image_data.save(image_path, format=image_format)
                        image_paths[image_id] = f"{image_dir_path.name}/{image_filename}"
                        image_count += 1
                        logger.info(f"Extracted image: {image_filename} ({getattr(image_data, 'size', 'unknown size')})", book_id)
                    elif isinstance(image_data, str):
                        if image_data.startswith('data:'):
                            image_data = image_data.split(',', 1)[1]
                        image_bytes = base64.b64decode(image_data)
                        with open(image_path, 'wb') as f:
                            f.write(image_bytes)
                        image_paths[image_id] = f"{image_dir_path.name}/{image_filename}"
                        image_count += 1
                        logger.info(f"Extracted image: {image_filename} (base64)", book_id)
                    else:
                        logger.warning(f"Unknown image data type for {image_id}: {type(image_data)}", book_id)
                except Exception as e:
                    logger.warning(f"Could not save image {image_id}: {e}", book_id)
        except Exception as e:
            logger.warning(f"Image extraction failed: {e}", book_id)
        if image_count == 0:
            logger.info("No images found or extracted from the document", book_id)
        else:
            logger.info(f"Successfully extracted {image_count} images", book_id)
        return image_count, image_paths

    def _update_image_references(self, markdown_text: str, image_paths: Dict[str, str], book_id: str | None = None) -> str:
        import re
        logger = get_logger()
        image_pattern = r'!\[\]\((_page_\d+_Picture_\d+\.\w+)\)'
        def replace_image_path(match):
            original_path = match.group(1)
            if original_path in image_paths:
                return f'![]({image_paths[original_path]})'
            else:
                local_image_path = f"{self.image_dir.name}/{original_path}"
                return f'![]({local_image_path})'
        updated_text = re.sub(image_pattern, replace_image_path, markdown_text)
        image_refs = re.findall(image_pattern, markdown_text)
        if image_refs:
            logger.info(f"Found {len(image_refs)} image references: {image_refs}", book_id)
            extracted_count = sum(1 for ref in image_refs if ref in image_paths)
            logger.info(f"Successfully extracted {extracted_count}/{len(image_refs)} images", book_id)
        return updated_text

class PDF2MarkdownWorker:
    def __init__(self, storage_root: Path):
        self.storage_root = storage_root
        self.converter = MarkerPDFConverter()
        self.logger = get_logger(storage_root)
        self.logger.info(f"PDF2MarkdownWorker initialized with storage_root: {storage_root}")

    def find_jobs(self):
        self.logger.info("Entering find_jobs()...")
        for guid_dir in self.storage_root.iterdir():
            if guid_dir.is_dir():
                pdf_path = guid_dir / "originalbook.pdf"
                if pdf_path.exists():
                    self.logger.info(f"Found job: {pdf_path}")
                    yield guid_dir, pdf_path
        self.logger.info("Exiting find_jobs()")

    def load_progress(self, guid_dir: Path) -> Dict[str, Any]:
        progress_path = guid_dir / PROGRESS_FILENAME
        self.logger.info(f"Loading progress from {progress_path}")
        if progress_path.exists():
            with open(progress_path, 'r') as f:
                progress = json.load(f)
            self.logger.info(f"Loaded progress: {progress}")
            return progress
        self.logger.info("No progress file found, returning default progress.")
        return {"status": "pending"}

    def save_progress(self, guid_dir: Path, progress: Dict[str, Any]):
        progress_path = guid_dir / PROGRESS_FILENAME
        self.logger.info(f"Saving progress to {progress_path}: {progress}")
        with open(progress_path, 'w') as f:
            json.dump(progress, f, indent=2)
        self.logger.info("Progress saved.")

    def process_pdf(self, guid_dir: Path, pdf_path: Path):
        book_id = guid_dir.name
        self.logger.info(f"Starting process_pdf for {pdf_path}", book_id)
        progress = self.load_progress(guid_dir)
        if progress.get("status") == "completed":
            self.logger.info(f"Skipping {pdf_path}, already completed.", book_id)
            return
        try:
            self.logger.info(f"Processing {pdf_path}", book_id)
            self.save_progress(guid_dir, {"status": "processing", "step": "converting"})
            image_dir_path = guid_dir / "images"
            conversion_metadata = self.converter.convert_pdf_to_markdown(str(pdf_path), str(guid_dir / f"{pdf_path.stem}.md"), image_dir_path, book_id)
            self.save_progress(guid_dir, {"status": "processing", "step": "writing_metadata"})
            
            # Read existing bookmetadata.json if it exists, otherwise create new
            meta_path = guid_dir / "bookmetadata.json"
            existing_metadata = {}
            if meta_path.exists():
                try:
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        existing_metadata = json.load(f)
                    self.logger.info(f"Read existing bookmetadata.json for {guid_dir.name}", book_id)
                except Exception as e:
                    self.logger.warning(f"Could not read existing bookmetadata.json: {e}", book_id)
            
            # Merge conversion metadata with existing metadata
            merged_metadata = {**existing_metadata, **conversion_metadata}
            
            # Write merged metadata back to file
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(merged_metadata, f, indent=2)
            self.logger.info(f"Merged metadata written to {meta_path}", book_id)
            self.save_progress(guid_dir, {"status": "completed"})
            self.logger.info(f"Completed {pdf_path}", book_id)
        except Exception as e:
            self.logger.error_with_error(f"Error processing {pdf_path}: {e}", e, book_id)
            self.save_progress(guid_dir, {"status": "failed", "error": str(e)})
        self.logger.info(f"Exiting process_pdf for {pdf_path}", book_id) 