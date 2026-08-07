"""
Deleted File Finder
--------------------
Deleted files often aren't really gone - the filesystem just marks
the space as free, and the raw bytes stick around until overwritten.
This module works two ways:

1. carve_signatures(): scans a raw binary blob (e.g. a disk image, or
   an "unallocated space" dump) for known file signatures (magic
   bytes) like FF D8 FF (JPEG) or 25 50 44 46 (PDF), and reports every
   offset where one is found - a simplified version of real file
   carving used in tools like Foremost/Scalpel.

2. find_mismatched_signatures(): scans a normal folder of existing
   files and flags any file whose actual magic bytes don't match what
   its extension claims - a common sign of a renamed or disguised
   file that an investigator would want to look at closely.
"""

import os

# (signature name, hex bytes, typical extension)
SIGNATURES = [
    ("JPEG", bytes.fromhex("FFD8FF"), ".jpg"),
    ("PNG", bytes.fromhex("89504E470D0A1A0A"), ".png"),
    ("GIF", b"GIF87a", ".gif"),
    ("GIF", b"GIF89a", ".gif"),
    ("PDF", bytes.fromhex("25504446"), ".pdf"),
    ("ZIP/DOCX/XLSX", bytes.fromhex("504B0304"), ".zip"),
    ("BMP", bytes.fromhex("424D"), ".bmp"),
]


def carve_signatures(blob_path):
    """
    Scan a raw binary file byte-by-byte-region for known file
    signatures and report every offset where a signature begins.
    This simulates scanning unallocated disk space for recoverable
    file fragments.
    """
    if not os.path.isfile(blob_path):
       
        raise FileNotFoundError(f"File not found: {blob_path}")

    with open(blob_path, "rb") as f:
        data = f.read()

    hits = []
    for name, sig, ext in SIGNATURES:
        start = 0
        while True:
            idx = data.find(sig, start)
            if idx == -1:
                break
            hits.append({
                "offset_hex": hex(idx),
                "offset_decimal": idx,
                "signature_type": name,
                "likely_extension": ext,
                "signature_hex": sig.hex().upper(),
            })
            start = idx + 1

    hits.sort(key=lambda h: h["offset_decimal"])
    return {
        "scanned_file": os.path.abspath(blob_path),
        "size_bytes": len(data),
        "signatures_found": hits,
        "total_found": len(hits),
    }



def find_mismatched_signatures(folder_path):
    """
    Check every file in a folder: does its extension match what its
    magic bytes actually say it is? A mismatch (e.g. a .txt file that
    is really a JPEG) is a common sign of a disguised or renamed file.
    """
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Not a valid folder: {folder_path}")

    results = []
    for root, _dirs, files in os.walk(folder_path):
        for name in files:
            full_path = os.path.join(root, name)
            ext = os.path.splitext(name)[1].lower()

            try:
                with open(full_path, "rb") as f:
                    header = f.read(16)
            except OSError:
                continue

            detected = None
            for sig_name, sig, sig_ext in SIGNATURES:
                if header.startswith(sig):
                    detected = (sig_name, sig_ext)
                    break

            if detected and detected[1] != ext:
                results.append({
                    "file": os.path.relpath(full_path, folder_path),
                    "claimed_extension": ext or "(none)",
                    "detected_type": detected[0],
                    "expected_extension": detected[1],
                    "flag": "MISMATCH - possible disguised or renamed file",
                })

    return {
        "folder": os.path.abspath(folder_path),
        "mismatches": results,
        "total_mismatches": len(results),
    }
