"""
File Timeline Generator
------------------------
Scans a folder (recursively) and builds a chronological timeline of
every file's creation, modification, and last-accessed timestamps.
This helps an investigator reconstruct what happened on a system and
in what order - e.g. spotting a burst of file activity right before
an incident.

Note on ctime: on Linux, os.stat().st_ctime is the "metadata change
time" (permissions, renames, etc.), not true creation time - true
creation time isn't tracked by most Linux filesystems. On Windows it
genuinely is creation time. This module labels the field accurately
per platform rather than mislabeling it.
"""

import os
import platform
from datetime import datetime

IS_WINDOWS = platform.system() == "Windows"



def _fmt(ts):
    
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")



def generate_timeline(folder_path):
    """
    Walk a folder recursively and return a list of file records sorted
    by modification time (most relevant single "what happened when"
    signal), each with created/modified/accessed timestamps.
    """
    if not os.path.isdir(folder_path):
        
        raise NotADirectoryError(f"Not a valid folder: {folder_path}")

    records = []
    for root, _dirs, files in os.walk(folder_path):
        for name in files:
            full_path = os.path.join(root, name)
            try:
                st = os.stat(full_path)
            except OSError:
                continue

            records.append({
                "file": os.path.relpath(full_path, folder_path),
                "size_bytes": st.st_size,
                "created": _fmt(st.st_ctime) if IS_WINDOWS else None,
                "metadata_changed": None if IS_WINDOWS else _fmt(st.st_ctime),
                "modified": _fmt(st.st_mtime),
                "accessed": _fmt(st.st_atime),
                "_sort_key": st.st_mtime,
            })

    records.sort(key=lambda r: r["_sort_key"])
    for r in records:
        del r["_sort_key"]

    return records
