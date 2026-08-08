"""
Digital Forensics Investigation Toolkit
=========================================
A unified CLI that combines seven forensic modules into one toolkit:

  1. Hash Verifier            - prove file integrity via MD5/SHA256
  2. File Timeline Generator  - chronological file activity
  3. Metadata Extractor       - general + type-specific file metadata
  4. String/Keyword Searcher  - search evidence for keywords
  5. Deleted File Finder      - signature-based file carving
  6. HTML Report Generator    - compile findings into a report
  7. Case Manager             - open/close/reopen investigations

All results from modules 1-5 are recorded against whichever case is
currently open, and module 6 turns those recorded findings into a
polished HTML report. Run `python3 main.py` and follow the menu.
"""

import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules import (
    case_manager,
    hash_verifier,
    timeline_generator,
    metadata_extractor,
    keyword_searcher,
    deleted_file_finder,
    report_generator,
)

CURRENT_CASE = None  # holds a case_number string once a case is open


def clear():
    print("\n" + "=" * 64 + "\n")


def prompt(text):
    return input(f"{text}: ").strip()



def require_case():
    global CURRENT_CASE
    if CURRENT_CASE is None:
        print("⚠  No case is open. Open or create a case first (option 7).")
        return False
    return True


def record(module_name, summary, data):
    """Save a module's output against the currently open case."""
    if CURRENT_CASE:
      
        case_manager.add_finding(CURRENT_CASE, module_name, summary, data)
        print(f"[Saved to case {CURRENT_CASE}]")


# ---------------------------------------------------------------- Menu 1
def menu_hash_verifier():
    clear()
    print("HASH VERIFIER")
    if not require_case():
        return
    path = prompt("Path to file")
    known = prompt("Known hash to compare against (leave blank to just generate hashes)")
    try:
        if known:
            result = hash_verifier.verify_hash(path, known)
            print(f"\nAlgorithm: {result['algorithm']}")
            print(f"Computed:  {result['computed_hash']}")
            print(f"Known:     {result['known_hash']}")
            print(f"Verdict:   {result['verdict']}")
            record("hash_verifier", f"Verified {os.path.basename(path)}", result)
        else:
            result = hash_verifier.generate_hashes(path)
            print(f"\nMD5:    {result['md5']}")
            print(f"SHA256: {result['sha256']}")
            record("hash_verifier", f"Generated hashes for {os.path.basename(path)}", result)
    except Exception as e:
        print(f"Error: {e}")


# ---------------------------------------------------------------- Menu 2

def menu_timeline():
    clear()
    print("FILE TIMELINE GENERATOR")
    if not require_case():
        return
    folder = prompt("Folder to scan")
    try:
        timeline = timeline_generator.generate_timeline(folder)
        print(f"\n{len(timeline)} files found. Chronological order (by modified time):\n")
        for entry in timeline[:20]:
            print(f"  {entry['modified']}  {entry['file']}")
        if len(timeline) > 20:
            print(f"  ... and {len(timeline) - 20} more (full list saved to case)")
        record("timeline_generator", f"Timeline of {len(timeline)} files in {folder}", timeline)
    except Exception as e:
        print(f"Error: {e}")


# ---------------------------------------------------------------- Menu 3

def menu_metadata():
    clear()
    print("METADATA EXTRACTOR")
    if not require_case():
        return
    target = prompt("Path to a single file OR a folder (batch mode)")
    try:
        if os.path.isdir(target):
            results = metadata_extractor.extract_metadata_batch(target)
            print(f"\nExtracted metadata for {len(results)} files.")
            record("metadata_extractor", f"Batch metadata for {len(results)} files in {target}", results)
        else:
            result = metadata_extractor.extract_metadata(target)
            print(f"\nType: {result['type']}")
            for k, v in result["general"].items():
                print(f"  {k}: {v}")
            record("metadata_extractor", f"Metadata for {os.path.basename(target)}", result)
    except Exception as e:
        print(f"Error: {e}")


# ---------------------------------------------------------------- Menu 4

def menu_keyword_search():
    clear()
    print("STRING / KEYWORD SEARCHER")
    if not require_case():
        return
    folder = prompt("Folder to search")
    raw_keywords = prompt("Keywords (comma separated)")
    keywords = [k.strip() for k in raw_keywords.split(",") if k.strip()]
    try:
      
        result = keyword_searcher.search_keywords(folder, keywords)
        print(f"\nScanned {result['files_scanned']} files, skipped {result['files_skipped']} "
              f"(binary/oversized). Total matches: {result['total_matches']}\n")
        for m in result["matches"][:20]:
            print(f"  {m['file']}:{m['line_number']}  [{m['keyword']}]  {m['line_text']}")
        if result["total_matches"] > 20:
            print(f"  ... and {result['total_matches'] - 20} more (full list saved to case)")
        record("keyword_searcher", f"{result['total_matches']} matches for {keywords} in {folder}", result)
    except Exception as e:
        print(f"Error: {e}")


# ---------------------------------------------------------------- Menu 5

def menu_deleted_finder():
    clear()
    print("DELETED FILE FINDER")
    print("  1) Carve file signatures out of a raw binary blob / disk image")
    print("  2) Check a folder for extension/signature mismatches")
    if not require_case():
        return
    choice = prompt("Choose 1 or 2")
    try:
        if choice == "1":
          
            path = prompt("Path to binary blob / disk image file")
            result = deleted_file_finder.carve_signatures(path)
            print(f"\nScanned {result['size_bytes']} bytes. Found {result['total_found']} signature(s):\n")
            for hit in result["signatures_found"]:
                print(f"  offset {hit['offset_hex']:>10}  {hit['signature_type']} ({hit['likely_extension']})")
            record("deleted_file_finder", f"{result['total_found']} signatures carved from {path}", result)
        elif choice == "2":
            folder = prompt("Folder to check")
            result = deleted_file_finder.find_mismatched_signatures(folder)
            print(f"\nFound {result['total_mismatches']} mismatched file(s):\n")
            for m in result["mismatches"]:
                print(f"  {m['file']}  claims {m['claimed_extension']} but is actually {m['detected_type']}")
            record("deleted_file_finder", f"{result['total_mismatches']} mismatches in {folder}", result)
        else:
            print("Invalid choice.")
    except Exception as e:
        print(f"Error: {e}")


# ---------------------------------------------------------------- Menu 6

def menu_report():
    clear()
    print("HTML REPORT GENERATOR")
    if not require_case():
        return
    case_data = case_manager.load_case(CURRENT_CASE)
    reports_dir = case_manager.case_reports_folder(CURRENT_CASE)
    filename = prompt("Report filename (e.g. investigation_report.html)") or "report.html"
    if not filename.endswith(".html"):
        filename += ".html"
    output_path = os.path.join(reports_dir, filename)
    try:
        path = report_generator.generate_case_report(case_data, output_path)
        print(f"\nReport written to: {path}")
    except Exception as e:
        print(f"Error: {e}")


# ---------------------------------------------------------------- Menu 7


def menu_case_manager():
    global CURRENT_CASE
    clear()
    print("CASE MANAGER")
    print(f"  Currently open case: {CURRENT_CASE or '(none)'}")
    print("  1) Create new case")
    print("  2) List all cases")
    print("  3) Open/reopen a case")
    choice = prompt("Choose 1-3")
    try:
        if choice == "1":
            name = prompt("Case name")
            number = prompt("Case number (unique, e.g. 2026-001)")
            investigator = prompt("Investigator name")
            case_manager.create_case(name, number, investigator)
            CURRENT_CASE = number
            print(f"\nCase '{name}' created and opened.")
        elif choice == "2":
            cases = case_manager.list_cases()
            if not cases:
                print("\nNo cases found.")
            for c in cases:
                print(f"  [{c['case_number']}] {c['case_name']} - {c['investigator']} "
                      f"- {c['created']} - {c['findings_count']} finding(s)")
        elif choice == "3":
            number = prompt("Case number to open")
            case_manager.load_case(number)  # raises if not found
            CURRENT_CASE = number
            print(f"\nCase '{number}' opened.")
        else:
            print("Invalid choice.")
    except Exception as e:
        print(f"Error: {e}")


MENU_ACTIONS = {
    "1": menu_hash_verifier,
    "2": menu_timeline,
    "3": menu_metadata,
    "4": menu_keyword_search,
    "5": menu_deleted_finder,
    "6": menu_report,
    "7": menu_case_manager,
}



def main_menu():
    global CURRENT_CASE
    while True:
        clear()
        print("DIGITAL FORENSICS INVESTIGATION TOOLKIT")
        print(f"Open case: {CURRENT_CASE or '(none - open one via option 7)'}")
        print("""
  1) Hash Verifier
  2) File Timeline Generator
  3) Metadata Extractor
  4) String / Keyword Searcher
  5) Deleted File Finder
  6) HTML Report Generator
  7) Case Manager
  0) Exit
""")
        choice = prompt("Select an option")
        if choice == "0":
            print("Goodbye.")
            break
        action = MENU_ACTIONS.get(choice)
        if action:
            try:
                action()
            except Exception:
                print("An unexpected error occurred:")
                traceback.print_exc()
            input("\nPress Enter to continue...")
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main_menu()
