# PDF to Markdown Service

## Role
The pdf2markdown service converts the original PDF file into a markdown file and generates book metadata.

## Input
- `originalbook.pdf` from `/storage/{guid}/`.

## Output
- Markdown file and `bookmetadata.json` in `/storage/{guid}/`.

## Logic
- Runs as a console application (not a REST API).
- Loops infinitely, checking `/storage/{guid}/` for new or incomplete jobs.
- Reads the original PDF file.
- Converts the PDF to markdown format.
- Generates `bookmetadata.json` with relevant metadata.
- Writes progress to `/storage/{guid}/pdf2markdown-progress.json`.
- Recursively checks progress and resumes work as needed if interrupted.

## Configuration

- By default, the service uses `./storage` as the storage directory for development.
- To use a different storage directory (e.g., when running in Docker), set the `STORAGE_ROOT` environment variable.
- For example, in Docker you might mount `/temp/storage/` and run:

```bash
STORAGE_ROOT=/temp/storage/ python3 main.py
```

If not set, it will use `./storage` in the current working directory.

## Setup (Conda Environment)

1. Create and activate a conda environment:

Use `shell` on mac instead of `terminal`:

```bash
conda create -n pdf2md python=3.13.4 -y
conda activate pdf2md
```

2. Install required packages:

```bash
pip install -r requirements.txt
# Add any other dependencies your project requires here
```

3. Run the service as a console app:

```bash
python main.py
```

The app will continuously monitor `/storage/` for new jobs and process them automatically.

## Testing
Integration tests are included to ensure correct PDF conversion and resumable processing.

## Future Increments

- [ ] Automatically extract metadata from the PDF book (e.g., title, author, publication date) with minimal user input and write it to bookmetadata.json.

### Acceptance Criteria (AC)
- The system should extract all available metadata from the PDF file automatically.
- User input should be minimized; metadata fields should be filled in without requiring manual entry unless information is missing from the PDF.
- The extracted metadata must be written to `bookmetadata.json` in the corresponding storage directory. 