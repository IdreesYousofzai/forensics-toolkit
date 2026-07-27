"""
HTML Report Generator
-----------------------
Takes the output of any toolkit module (or a whole case's worth of
findings) and compiles it into a professionally formatted, self
contained HTML report - case name, investigator, date, and every
finding laid out in tables. Designed to be handed to someone who was
not in the room while the investigation happened.
"""

import os
import html
from datetime import datetime

CSS = """
body { font-family: 'Segoe UI', Arial, sans-serif; background:#f4f5f7; color:#1f2430; margin:0; padding:0; }
.container { max-width: 960px; margin: 0 auto; padding: 32px 24px 64px; }
header { background:#1f2937; color:#fff; padding:28px 24px; }
header h1 { margin:0 0 6px; font-size:1.6em; }
header .meta { color:#cbd5e1; font-size:0.95em; }
.meta-table { width:100%; border-collapse:collapse; margin:24px 0; }
.meta-table td { padding:6px 10px; border-bottom:1px solid #e2e4e9; font-size:0.95em; }
.meta-table td:first-child { font-weight:600; width:180px; color:#4b5563; }
section { background:#fff; border:1px solid #e2e4e9; border-radius:8px; padding:20px 24px; margin-bottom:22px; }
section h2 { margin-top:0; font-size:1.15em; border-bottom:2px solid #1f2937; padding-bottom:8px; }
table.data { width:100%; border-collapse:collapse; margin-top:12px; font-size:0.88em; }
table.data th { background:#1f2937; color:#fff; text-align:left; padding:8px 10px; }
table.data td { padding:7px 10px; border-bottom:1px solid #eceef1; vertical-align:top; word-break:break-word; }
table.data tr:nth-child(even) { background:#fafbfc; }
.badge-match { color:#0a7a2f; font-weight:600; }
.badge-fail { color:#b3261e; font-weight:600; }
.summary-line { color:#4b5563; font-size:0.92em; margin-bottom:10px; }
footer { text-align:center; color:#9aa0ab; font-size:0.8em; margin-top:30px; }
"""



def _esc(v):
    return html.escape(str(v))



def _dict_table(d):
    rows = "".join(f"<tr><td>{_esc(k)}</td><td>{_esc(v)}</td></tr>" for k, v in d.items())
    return f'<table class="data"><tbody>{rows}</tbody></table>'



def _list_of_dicts_table(items):
    if not items:
        return "<p class='summary-line'>No results.</p>"
    columns = list(items[0].keys())
    header = "".join(f"<th>{_esc(c)}</th>" for c in columns)
    body_rows = ""
    for item in items:
        cells = "".join(f"<td>{_esc(item.get(c, ''))}</td>" for c in columns)
        body_rows += f"<tr>{cells}</tr>"
    return f'<table class="data"><thead><tr>{header}</tr></thead><tbody>{body_rows}</tbody></table>'


def _render_finding_body(finding):
    """Render a single finding's data into HTML depending on its shape."""
    data = finding["data"]
    module = finding["module"]

    if module == "hash_verifier":
        if "verdict" in data:
            verdict_class = "badge-match" if data.get("match") else "badge-fail"
            table = _dict_table({k: v for k, v in data.items() if k != "verdict"})
            return table + f'<p class="{verdict_class}">{_esc(data["verdict"])}</p>'
        return _dict_table(data)

    if module == "timeline_generator":
        return _list_of_dicts_table(data)

    if module == "metadata_extractor":
        if isinstance(data, list):
            blocks = ""
            for item in data:
                blocks += f"<h3 style='margin-bottom:4px'>{_esc(item['general'].get('file',''))}</h3>"
                blocks += _dict_table(item["general"])
                if item.get("type_specific"):
                    blocks += _dict_table(item["type_specific"])
            return blocks
        blocks = _dict_table(data["general"])
        if data.get("type_specific"):
            blocks += _dict_table(data["type_specific"])
        return blocks

    if module == "keyword_searcher":
        summary = f'<p class="summary-line">Files scanned: {data["files_scanned"]} | ' \
                   f'Files skipped: {data["files_skipped"]} | Total matches: {data["total_matches"]}</p>'
        return summary + _list_of_dicts_table(data["matches"])

    if module == "deleted_file_finder":
        if "signatures_found" in data:
            summary = f'<p class="summary-line">Scanned {data["scanned_file"]} ' \
                       f'({data["size_bytes"]} bytes) | Signatures found: {data["total_found"]}</p>'
            return summary + _list_of_dicts_table(data["signatures_found"])
        else:
            summary = f'<p class="summary-line">Folder: {data["folder"]} | ' \
                       f'Mismatches found: {data["total_mismatches"]}</p>'
            return summary + _list_of_dicts_table(data["mismatches"])

    # Fallback for anything unrecognised
    if isinstance(data, list):
        return _list_of_dicts_table(data)
    if isinstance(data, dict):
        return _dict_table(data)
    return f"<p>{_esc(data)}</p>"


def generate_case_report(case_data, output_path):
    """
    Build a full HTML report covering every finding recorded against a
    case, and write it to output_path.
    """
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sections = ""
    if not case_data["findings"]:
        sections = "<section><p>No findings have been recorded for this case yet.</p></section>"
    else:
        for i, finding in enumerate(case_data["findings"], start=1):
            title = f'{i}. {finding["module"].replace("_", " ").title()}'
            sections += f"""
            <section>
                <h2>{_esc(title)}</h2>
                <p class="summary-line">{_esc(finding["summary"])} &mdash; recorded {_esc(finding["timestamp"])}</p>
                {_render_finding_body(finding)}
            </section>"""

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Forensic Report - {_esc(case_data['case_name'])}</title>
<style>{CSS}</style>
</head>
<body>
<header>
    <h1>Digital Forensics Investigation Report</h1>
    <div class="meta">Case: {_esc(case_data['case_name'])} ({_esc(case_data['case_number'])})</div>
</header>
<div class="container">
    <table class="meta-table">
        <tr><td>Case Name</td><td>{_esc(case_data['case_name'])}</td></tr>
        <tr><td>Case Number</td><td>{_esc(case_data['case_number'])}</td></tr>
        <tr><td>Investigator</td><td>{_esc(case_data['investigator'])}</td></tr>
        <tr><td>Case Opened</td><td>{_esc(case_data['created'])}</td></tr>
        <tr><td>Report Generated</td><td>{_esc(generated_at)}</td></tr>
        <tr><td>Total Findings</td><td>{len(case_data['findings'])}</td></tr>
    </table>
    {sections}
    <footer>Generated by the Digital Forensics Investigation Toolkit</footer>
</div>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html_doc)

    return output_path
