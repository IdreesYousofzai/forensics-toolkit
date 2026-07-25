# Case Study Report: Draymond Street Warehouse Data Breach

**Case number:** 2026-014
**Investigator:** Idrees Yousofzai
**Date opened:** simulated investigation, run against sample evidence in `evidence_sample/`

## Background

A witness reported a suspicious van parked outside a warehouse late at night. Around the same time, the company's IT team flagged a burst of failed login attempts on the admin panel, followed by a successful login and an export of the customer database. I was asked to run the toolkit against the collected evidence — a witness statement, a server access log, an internal IT memo, a CCTV frame, a draft incident report, and a suspect disk image — and work out what actually happened.

The evidence lives in `evidence_sample/`:

- `witness_statement.txt` — the witness's account, including a partial number plate and a password overheard on a phone call
- `server_access.log` — raw Apache-style access log from the admin panel
- `internal_memo.txt` — the IT team's own write-up of the flagged activity
- `cctv_frame_2340.jpg` — a still from CCTV around the time of the incident
- `incident_report_draft.pdf` — a draft report with the same details the witness gave
- `disk_image_unallocated.bin` — a simulated dump of unallocated disk space, built by embedding fragments of the JPEG and the full PDF inside random noise, to stand in for a real forensic disk image
- `hidden_notes.txt` — a copy of the CCTV JPEG saved with a `.txt` extension, standing in for a file someone tried to disguise

## Methodology

I opened a case in the toolkit (case number 2026-014) and ran all seven modules against the evidence in sequence, recording every result against that case so the final report would pull them together automatically.

### Hash Verifier

I generated MD5/SHA256 hashes for `server_access.log` at the point of collection, then re-ran the verifier a second time against the known SHA256 to simulate a later integrity check. Both hashes matched — the file hadn't been altered between collection and analysis, so it can be relied on as evidence.

### File Timeline Generator

The timeline covered all seven evidence files sorted by modification time. Because this is a simulated case built in one session, the timestamps cluster close together rather than spreading across the real 14 October timeline described in the witness statement — worth noting as a limitation of using freshly created sample files rather than an actual seized system.

### Metadata Extractor

Ran in batch mode across the whole evidence folder. The PDF metadata extraction correctly pulled the author field ("J. Marsh") and page count from `incident_report_draft.pdf`. The JPEG had no EXIF data — the sample image was generated programmatically rather than taken on a camera, so there's no GPS or device information to pull. On a real CCTV export this is exactly the kind of field that would matter: camera model and embedded timestamp can corroborate or contradict a witness's account of when something happened.

### String / Keyword Searcher

I searched for three terms tied to the case: the suspected password (`falcon2024`), the internal IP address from the log (`192.168.1.14`), and the partial plate (`LK19`). The search returned 10 matches across the text evidence — `falcon2024` appears in both the witness statement and the internal memo, and the IP address ties the memo directly to specific lines in the raw access log. That's the kind of corroboration an investigator is looking for: two independent sources (a human witness and a machine log) pointing at the same fact.

### Deleted File Finder

Run both ways. Signature carving against `disk_image_unallocated.bin` found three recoverable signatures: a truncated JPEG fragment, a complete PDF, and a PNG signature fragment I'd deliberately planted in the noise. The PDF carved out fully intact, which mirrors a real scenario where a "deleted" document is still completely recoverable because the underlying data was never overwritten.

The mismatch scan flagged exactly one file: `hidden_notes.txt`, whose magic bytes identify it as a JPEG despite the `.txt` extension. This is the disguised-file scenario the module is built to catch.

### HTML Report Generator

With all findings recorded, I generated `full_investigation_report.html` from the case data. It lays out the case metadata up top, then every finding as its own section with a data table, so someone reading it cold can follow the investigation from hash verification through to the disguised file discovery without needing to have run the toolkit themselves.

### Case Manager

Everything above only worked because it was all filed under one case number. Reopening case 2026-014 at any point pulls the full history of what's been done, which is the whole point — a real investigation isn't run in one sitting.

## Findings

1. The access log shows two failed login attempts followed by a successful one at 23:32, then a customer data export at 23:33, from internal IP 192.168.1.14 — consistent with the IT memo.
2. The password `falcon2024`, overheard by the witness and named in the memo, appears in both independent sources, which strengthens the credibility of the witness account.
3. `hidden_notes.txt` is a JPEG disguised as a text file, flagged automatically by the extension/signature mismatch check.
4. The unallocated space scan recovered a complete PDF and a partial JPEG, demonstrating that deleted evidence can survive in raw disk regions even after a file's directory entry is gone.
5. The server log's hash remained consistent across two checks, so it holds up as reliable evidence.

## Conclusions

Taken together, the log timestamps, the shared password reference across two independent sources, and the disguised file point to the same conclusion: the admin account was compromised around 23:31–23:33 on the night in question, the customer table was exported shortly after, and at least one piece of evidence (`hidden_notes.txt`) had been deliberately renamed to avoid a casual search turning it up. None of these findings depend on a single module — it's the combination of log analysis, keyword search, and signature checking that builds a case that would hold up to scrutiny.

## Limitations of this simulation

This is a constructed exercise, not a real investigation. The disk image is a hand-built blob rather than an actual forensic image, the timestamps don't span a realistic multi-day window, and the CCTV frame has no genuine camera metadata. The toolkit's logic and output format are the same as they'd be in a real case; only the input data is simulated.
