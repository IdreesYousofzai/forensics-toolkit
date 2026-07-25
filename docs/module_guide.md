# Module Guide

How to use each module, what its output means, and what a real forensic
investigator would do with it.

---

## 1. Hash Verifier

**What it does:** Generates MD5 and SHA256 hashes for a file, and optionally
compares them against a known hash.

**How to use it:** Point it at a file. Leave the "known hash" prompt blank
the first time you collect evidence — this generates the baseline hash you
record on the chain-of-custody form. Later, run it again with that hash
filled in to check the file hasn't changed.

**Reading the output:**
- `computed_hash` — the hash of the file right now.
- `match` / `verdict` — whether it still matches the known hash.

**What an investigator does with it:** This is the whole basis of proving
evidence integrity in court. If the hash still matches, you can state under
oath that the file is byte-for-byte identical to what was seized. If it
doesn't match, the evidence has been altered (or you've got the wrong file)
and cannot be relied on without explaining the discrepancy.

---

## 2. File Timeline Generator

**What it does:** Recursively scans a folder and lists every file's
modified, accessed, and (on Linux) metadata-changed / (on Windows) created
timestamps, sorted chronologically by modification time.

**Reading the output:** Each row is one file with its timestamps. Read it
top to bottom as "what happened, in order."

**What an investigator does with it:** Timelines let you spot clusters of
activity — e.g. five files all modified within the same two-minute window
right before an incident is a strong signal of what the suspect was doing
and when. It's also how you notice something *missing*: a gap in otherwise
regular activity can be as telling as an unusual burst.

**Caveat documented in the module itself:** on Linux, `ctime` is metadata
change time, not true file creation time — the toolkit labels this
correctly per platform rather than claiming a false "created" timestamp.

---

## 3. Metadata Extractor

**What it does:** Pulls general metadata (size, extension, modified/accessed
times) for any file, plus type-specific metadata: EXIF data for images
(camera model, GPS, capture time if present), title/author/producer/page
count for PDFs, and line/word/character counts for text files.

**How to use it:** Point it at a single file for a detailed read-out, or a
whole folder for a batch sweep.

**Reading the output:** `general` always has the basics. `type_specific`
has whatever could be extracted for that file type — if a library like
Pillow or pypdf isn't installed, it tells you that instead of guessing.

**What an investigator does with it:** EXIF GPS data can place a photo at
a specific location and time. PDF author/producer fields can tie a document
to a specific machine or piece of software. Even simple things — a text
file with an unusually high word count for its apparent purpose — can be
worth a second look.

---

## 4. String / Keyword Searcher

**What it does:** Searches every readable text file in a folder for a list
of keywords and reports every match with file, line number, and the
matching line.

**How to use it:** Give it a folder and a comma-separated list of keywords
— names, IP addresses, suspected passwords, dates, anything relevant to the
case.

**Reading the output:** Each match shows exactly where a keyword was found,
so you can jump straight to that line in the original file.

**What an investigator does with it:** This is evidence discovery at scale
— instead of reading every log and document by hand, you search for the
specific facts that matter (a suspect's name, a leaked credential, a
timestamp) and get pointed straight to every occurrence.

---

## 5. Deleted File Finder

**What it does two ways:**
1. **Signature carving** — scans a raw binary file (a disk image, or a dump
   of "unallocated space") for known file signatures (magic bytes), such as
   `FF D8 FF` for JPEG or `25 50 44 46` for PDF, and reports every offset
   where one starts.
2. **Mismatch detection** — checks every file in a normal folder to see if
   its actual magic bytes match what its extension claims. A `.txt` file
   that's actually a JPEG under the hood is a classic sign of a disguised
   file.

**Reading the output:** Carving gives you a list of offsets and signature
types — each one is a potential recoverable file fragment. Mismatch
detection flags files where the claimed and detected type disagree.

**What an investigator does with it:** Deleting a file usually just removes
its filesystem entry, not the underlying bytes, so scanning raw disk
regions for known signatures is a genuine (if simplified — this toolkit
demonstrates the signature-matching principle used by tools like
Foremost/Scalpel, not full sector-level reconstruction) way to recover
evidence a suspect thought was gone. A renamed/disguised file is worth
flagging because people rename files specifically to make them less
interesting to a casual search.

---

## 6. HTML Report Generator

**What it does:** Compiles every finding recorded against the currently
open case into a single, self-contained, professionally formatted HTML
report — case name, case number, investigator, date opened, and every
finding as its own section with a data table.

**How to use it:** Run it any time — it always reflects everything recorded
so far. Give it a filename; it's saved into that case's `reports/` folder.

**What an investigator does with it:** This is the document that leaves the
toolkit and gets read by someone who wasn't there — a supervisor, a lawyer,
a court. It needs to be self-explanatory, which is why every finding
includes a plain-English summary line alongside the raw data.

---

## 7. Case Manager

**What it does:** Creates a case (name, number, investigator, date), lists
existing cases, and lets you reopen a previous one. All findings from every
other module are recorded against whichever case is currently open.

**How to use it:** Create a case before doing anything else in a session.
If you're continuing earlier work, reopen that case number instead of
creating a new one — findings accumulate, they don't reset.

**What an investigator does with it:** Real investigations span days or
weeks and produce evidence from many different tools. Keeping everything
filed under one case number, with a persistent record of who investigated
what and when, is what makes the whole thing auditable later.
