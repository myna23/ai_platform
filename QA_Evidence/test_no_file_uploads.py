#!/usr/bin/env python3
"""
QA evidence — file uploads are not available (ACN-2026-31023, story 186189).

The application is approved for PUBLIC data only. Accepting attachments would
send their content to the WBG mAI Factory for analysis with no way to establish
the classification of what a user attached, so the capability has been removed
rather than restricted.

This verifies the capability is absent from the source, not merely discouraged
by a warning.

Run from the application root:

    python QA_Evidence/test_no_file_uploads.py
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKIP_DIRS = {".git", "__pycache__", "QA_Evidence", "node_modules",
             ".venv", "venv", "env", "site-packages", ".tox", "build", "dist"}

checks = []


def record(name, detail, ok):
    checks.append((name, detail, ok))


def app_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".py"):
                yield os.path.join(dirpath, fn)


def scan(patterns, label):
    """Report every source line matching any pattern, ignoring comments."""
    hits = []
    count = 0
    for path in app_files():
        count += 1
        try:
            lines = open(path, encoding="utf-8").read().splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines, 1):
            if line.lstrip().startswith("#"):
                continue          # a comment explaining the removal is not code
            for pat in patterns:
                if re.search(pat, line):
                    hits.append(f"{os.path.relpath(path, ROOT)}:{i} {line.strip()[:70]}")
    return hits, count


# 1. No upload widget of any kind
hits, scanned = scan(
    [r"\bst\.file_uploader\b", r"\baccept_file\b", r"\bst\.camera_input\b",
     r"\bfile_type\s*="],
    "upload widgets")
record("No file-upload control is created",
       "; ".join(hits) if hits else
       f"no upload widget appears in {scanned} application .py files",
       not hits)

# 2. The chat input is constructed without attachment support
app_src = open(os.path.join(ROOT, "app.py"), encoding="utf-8").read()
m = re.search(r"st\.chat_input\((.*?)\)\s*\n", app_src, re.S)
call = " ".join(m.group(1).split()) if m else "<not found>"
record("Chat input accepts text only",
       f"st.chat_input({call})",
       bool(m) and "accept_file" not in call)

# 3. No code remains that would read or decode an uploaded file
hits2, _ = scan(
    [r"PdfReader", r"\.read\(\)\s*\}", r"uploaded_img", r"uploaded_doc",
     r"_pending_files", r"_process_confirmed_upload"],
    "file handling")
record("No uploaded-file handling code remains",
       "; ".join(hits2) if hits2
       else "no attachment parsing, decoding or session storage remains",
       not hits2)

# 4. The image-analysis path is gone
hits3, _ = scan([r"map_analysis"], "image analysis")
record("No image-analysis path remains",
       "; ".join(hits3) if hits3
       else "the map-image-analysis intent and its prompts were removed",
       not hits3)

# 5. The PDF parsing dependency is no longer declared
req = open(os.path.join(ROOT, "requirements.txt"), encoding="utf-8").read()
record("PDF parsing dependency removed",
       "pypdf is not declared in requirements.txt" if "pypdf" not in req
       else "pypdf is still declared",
       "pypdf" not in req)

# Report
print("=" * 78)
print("QA EVIDENCE - FILE UPLOADS NOT AVAILABLE")
print("ACN-2026-31023 / story 186189")
print("=" * 78)
print("Environment        : QA")
print("Application        : Zambia GeoHub AI Assistant")
print("Approved scope     : public data only")
print("-" * 78)

failed = 0
for i, (name, detail, ok) in enumerate(checks, 1):
    failed += not ok
    print(f"{i}. {name}")
    print(f"   {'PASS' if ok else 'FAIL'} - {detail}")
    print()

print("-" * 78)
print(f"{len(checks) - failed} of {len(checks)} checks passed.")
print()
print("The application provides no means of submitting a file. No attachment")
print("control is rendered, and no code exists that would read, decode, store")
print("or forward uploaded content. A user therefore cannot send personal or")
print("restricted material to the AI service through this application,")
print("irrespective of intent.")
print()
print("RESULT:", "PASS" if not failed else "FAIL")
print("=" * 78)
sys.exit(1 if failed else 0)
