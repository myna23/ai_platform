#!/bin/bash
# Regenerates all code-side QA evidence. Run from project root:
#   bash QA_Evidence/00_generate.sh
#
# Override the interpreter if needed:
#   PYTHON=python3.11 bash QA_Evidence/00_generate.sh
#
# Each test drives the real application modules, so the output reflects
# deployed behaviour rather than a description of it. A test that fails is
# still written out, and this script reports which ones failed.

cd "$(dirname "$0")/.." || exit 1
OUT=QA_Evidence
PY=${PYTHON:-python3}
DATE=$(date +%Y-%m-%d)
COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "not a git checkout")

command -v "$PY" >/dev/null || { echo "ERROR: '$PY' not found. Set PYTHON=..."; exit 1; }

# story | output file | description | script
TESTS=(
"186198|186198_input_validation.txt|Input validation - closed place-name allowlist|test_input_validation.py"
"186199|186199_error_handling.txt|Error handling - no technical detail disclosed to users|test_error_handling.py"
"186189|186189_no_arcgis_credential.txt|No ArcGIS credential configured or used|test_no_arcgis_credential.py"
"186189|186189_no_file_uploads.txt|File uploads are not available|test_no_file_uploads.py"
)

failed=()
for row in "${TESTS[@]}"; do
    IFS='|' read -r story file desc script <<< "$row"
    target="$OUT/$file"

    {
        echo "EVIDENCE: $desc  (story $story)"
        echo "Run on: $DATE   Commit: $COMMIT"
        echo "-----------------------------------------------------------------------"
        echo
    } > "$target"

    if "$PY" "$OUT/$script" >> "$target" 2>&1; then
        echo "  OK    $file"
    else
        echo "  FAIL  $file  <- test did not pass, see the file"
        failed+=("$file")
    fi
done

echo
if [ ${#failed[@]} -eq 0 ]; then
    echo "All evidence regenerated and passing."
else
    echo "${#failed[@]} test(s) failed: ${failed[*]}"
    exit 1
fi
