# Digital Forensics Investigation Toolkit

A CLI toolkit that combines seven forensic modules into one workflow: verify
evidence integrity, reconstruct file timelines, pull metadata, search for
keywords, recover deleted file fragments, and compile everything into a
professional HTML report — all organised by case.

## Requirements

- Python 3.9+
- Optional (for full metadata extraction): `Pillow`, `pypdf`
  ```
  pip install Pillow pypdf --break-system-packages
  ```
  The toolkit still runs without these — it just skips EXIF/PDF-specific
  metadata and tells you what's missing.

## Running it

```
python3 main.py
```

You'll land on the main menu. Start with option **7 (Case Manager)** to
create or open a case — every other module needs an open case, because all
findings get saved against it.

```
DIGITAL FORENSICS INVESTIGATION TOOLKIT
Open case: (none - open one via option 7)

  1) Hash Verifier
  2) File Timeline Generator
  3) Metadata Extractor
  4) String / Keyword Searcher
  5) Deleted File Finder
  6) HTML Report Generator
  7) Case Manager
  0) Exit
```

## Project structure

```
forensics-toolkit/
├── main.py                     # unified CLI menu
├── modules/
│   ├── case_manager.py
│   ├── hash_verifier.py
│   ├── timeline_generator.py
│   ├── metadata_extractor.py
│   ├── keyword_searcher.py
│   ├── deleted_file_finder.py
│   └── report_generator.py
├── cases/                      # created at runtime, one folder per case
│   └── <case_number>/
│       ├── case.json           # all findings for that case
│       └── reports/            # generated HTML reports
├── evidence_sample/             # simulated evidence used for the demo case study
└── docs/
    ├── module_guide.md          # what each module does and how to read its output
    └── case_study_report.md     # write-up of the simulated investigation
```

See `docs/module_guide.md` for a walkthrough of each module and
`docs/case_study_report.md` for a full worked investigation using the toolkit
against the sample evidence in `evidence_sample/`.
