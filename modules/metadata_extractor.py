"""
Metadata Extractor
-------------------
Integrated into the toolkit from the standalone Project 5 file
metadata analyser. Pulls out general filesystem metadata for any
file, plus type-specific metadata where possible:
  - Images: dimensions, format, and EXIF data (camera model, GPS,
    timestamp) if Pillow is installed
  - PDFs: author, title, producer, page count if pypdf is installed
  - Text files: line count, word count, character count

Missing optional libraries degrade gracefully rather than crashing -
the toolkit should still run on a bare Python install, just with
fewer type-specific details.
"""

import os
from datetime import datetime

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

try:
    from pypdf import PdfReader
    HAVE_PYPDF = True
except ImportError:
    HAVE_PYPDF = False

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".gif"}
TEXT_EXTS = {".txt", ".log", ".csv", ".md", ".json", ".xml", ".html", ".py"}


def _general_metadata(path):
    st = os.stat(path)
    return {
        "file": os.path.abspath(path),
        "extension": os.path.splitext(path)[1].lower() or "(none)",
        "size_bytes": st.st_size,
        "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "accessed": datetime.fromtimestamp(st.st_atime).strftime("%Y-%m-%d %H:%M:%S"),
    }

def _image_metadata(path):
    if not HAVE_PIL:
        return {"note": "Pillow not installed - install with: pip install Pillow --break-system-packages"}

    info = {}
    try:
      
        with Image.open(path) as img:
            info["dimensions"] = f"{img.width}x{img.height}"
            info["format"] = img.format
            info["mode"] = img.mode

            exif_data = img.getexif()
            if exif_data:
                exif_readable = {}
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_readable[str(tag)] = str(value)
                if exif_readable:
                    info["exif"] = exif_readable
                else:
                    info["exif"] = "No EXIF tags found"
            else:
                info["exif"] = "No EXIF data present"
    except Exception as e:
        info["error"] = f"Could not read image: {e}"
    return info


def _pdf_metadata(path):
    if not HAVE_PYPDF:
        return {"note": "pypdf not installed - install with: pip install pypdf --break-system-packages"}

    info = {}
    try:
      
        reader = PdfReader(path)
        info["page_count"] = len(reader.pages)
        meta = reader.metadata or {}
        info["title"] = meta.get("/Title", "(none)")
        info["author"] = meta.get("/Author", "(none)")
        info["producer"] = meta.get("/Producer", "(none)")
        info["creation_date"] = meta.get("/CreationDate", "(none)")
    except Exception as e:
        info["error"] = f"Could not read PDF: {e}"
    return info


def _text_metadata(path):
    info = {}
    try:
        with open(path, "r", errors="replace") as f:
            content = f.read()
        info["line_count"] = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
        info["word_count"] = len(content.split())
        info["char_count"] = len(content)
    except Exception as e:
        info["error"] = f"Could not read text file: {e}"
    return info


def extract_metadata(path):
    """
    Extract general + type-specific metadata for a single file.
    Returns a nested dict: {"general": {...}, "type_specific": {...}}
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    result = {"general": _general_metadata(path)}

    if ext in IMAGE_EXTS:
        result["type"] = "image"
        result["type_specific"] = _image_metadata(path)
    elif ext == ".pdf":
        result["type"] = "pdf"
        result["type_specific"] = _pdf_metadata(path)
    elif ext in TEXT_EXTS:
        result["type"] = "text"
        result["type_specific"] = _text_metadata(path)
    else:
        result["type"] = "unknown"
        result["type_specific"] = {"note": "No type-specific extractor for this file type"}

    return result


def extract_metadata_batch(folder_path):
    """Run extract_metadata over every file in a folder (recursively)."""
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Not a valid folder: {folder_path}")

    results = []
    for root, _dirs, files in os.walk(folder_path):
        for name in files:
            full_path = os.path.join(root, name)
            try:
                results.append(extract_metadata(full_path))
            except Exception as e:
                results.append({"general": {"file": full_path}, "type": "error",
                                 "type_specific": {"error": str(e)}})
    return results
