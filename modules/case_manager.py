"""
Case Manager
------------
Every investigation in this toolkit belongs to a "case". A case has a
name, a case number, an investigator, a creation date, and a folder on
disk where all evidence findings and reports get saved. This module is
responsible for creating cases, listing existing ones, reopening a
previous case, and recording findings against whichever case is
currently open.
"""

import json
import os
from datetime import datetime

CASES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cases")


def _case_folder(case_number):
    
    return os.path.join(CASES_DIR, case_number)


def _case_file(case_number):
    return os.path.join(_case_folder(case_number), "case.json")


def create_case(case_name, case_number, investigator):
    """Create a new case folder and its case.json metadata file."""
    folder = _case_folder(case_number)
    if os.path.exists(folder):
        
        raise FileExistsError(f"Case number '{case_number}' already exists.")

    os.makedirs(folder)
    os.makedirs(os.path.join(folder, "reports"))

    case_data = {
        "case_name": case_name,
        "case_number": case_number,
        "investigator": investigator,
        "created": datetime.now().isoformat(timespec="seconds"),
        "findings": []
    }

    with open(_case_file(case_number), "w") as f:
        json.dump(case_data, f, indent=2)

    return case_data


def list_cases():
    """Return a list of case summaries (name, number, investigator, date)."""
    if not os.path.isdir(CASES_DIR):
        return []

    summaries = []
    for entry in sorted(os.listdir(CASES_DIR)):
        case_file = _case_file(entry)
        if os.path.isfile(case_file):
            with open(case_file) as f:
                data = json.load(f)
            summaries.append({
                "case_number": data["case_number"],
                "case_name": data["case_name"],
                "investigator": data["investigator"],
                "created": data["created"],
                "findings_count": len(data.get("findings", []))
            })
    return summaries


def load_case(case_number):
    """Load and return the full case data for a given case number."""
    case_file = _case_file(case_number)
    if not os.path.isfile(case_file):
        raise FileNotFoundError(f"No case found with number '{case_number}'.")
    with open(case_file) as f:
        return json.load(f)


def add_finding(case_number, module_name, summary, data):
    """
    Record a finding against a case. `summary` is a short human readable
    description shown in listings; `data` is the full structured result
    from whichever module produced it (used later by the report generator).
    """
    case_data = load_case(case_number)
    finding = {
        "module": module_name,
        "summary": summary,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "data": data
    }
    case_data["findings"].append(finding)

    with open(_case_file(case_number), "w") as f:
        json.dump(case_data, f, indent=2)

    return finding


def case_reports_folder(case_number):
    """Return (and ensure exists) the reports folder for a case."""
    folder = os.path.join(_case_folder(case_number), "reports")
    os.makedirs(folder, exist_ok=True)
    return folder
