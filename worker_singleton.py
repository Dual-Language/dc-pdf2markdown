from pathlib import Path
import os
from service import PDF2MarkdownWorker

DEFAULT_STORAGE_ROOT = Path("../storage")
STORAGE_ROOT = Path(os.environ.get("STORAGE_ROOT", str(DEFAULT_STORAGE_ROOT))).resolve()

worker_instance = PDF2MarkdownWorker(STORAGE_ROOT)
