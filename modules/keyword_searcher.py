"""
String / Keyword Searcher
--------------------------
Given a folder and a list of keywords, searches through every
text-readable file for those keywords and reports every match with
the file path, line number, and the matching line itself. This is the
digital equivalent of searching seized documents for names, dates, or
incriminating phrases.

Binary files are skipped automatically (detected via a decode check)
rather than being force-read, which would produce garbage matches.
"""

import os

# Reasonable cap so one huge file doesn't hang the search
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB



def _is_probably_text(path):
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
        chunk.decode("utf-8")
        return True
    except (UnicodeDecodeError, OSError):
        return False



def search_keywords(folder_path, keywords, case_sensitive=False):
    """
    Search every text file under folder_path for each keyword.
    Returns a list of match dicts: file, line_number, line_text, keyword.
    """
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Not a valid folder: {folder_path}")
    if not keywords:
        raise ValueError("At least one keyword is required.")

    search_terms = keywords if case_sensitive else [k.lower() for k in keywords]
    matches = []
    files_scanned = 0
    files_skipped = 0

    for root, _dirs, files in os.walk(folder_path):
        for name in files:
            full_path = os.path.join(root, name)

            if os.path.getsize(full_path) > MAX_FILE_SIZE_BYTES or not _is_probably_text(full_path):
                files_skipped += 1
                continue

            files_scanned += 1
            try:
                with open(full_path, "r", errors="replace") as f:
                    for line_num, line in enumerate(f, start=1):
                        haystack = line if case_sensitive else line.lower()
                        for i, term in enumerate(search_terms):
                            if term in haystack:
                                matches.append({
                                    "file": os.path.relpath(full_path, folder_path),
                                    "line_number": line_num,
                                    "line_text": line.strip(),
                                    "keyword": keywords[i],
                                })
            except OSError:
                files_skipped += 1
                continue

    return {
        "matches": matches,
        "files_scanned": files_scanned,
        "files_skipped": files_skipped,
        "total_matches": len(matches),
    }
