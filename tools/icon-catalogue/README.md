# Icon Catalogue CLI

A Python 3.10+ standard-library tool for downloading, importing, normalizing, deduplicating, cataloguing, and auditing SVG icons.

## Commands

Run from the repository root:

```bash
python3 tools/icon-catalogue/iconctl.py --help

# Add one SVG from a direct download URL
python3 tools/icon-catalogue/iconctl.py fetch \
  --url "https://example.com/service.svg" \
  --name "Example Service" --provider example \
  --license "See provider terms" \
  --license-url "https://example.com/terms"

# Import all SVGs from a vendor-provided ZIP
python3 tools/icon-catalogue/iconctl.py import-zip \
  --archive /tmp/vendor-icons.zip --provider azure \
  --source-url "https://learn.microsoft.com/azure/architecture/icons/" \
  --license "Microsoft architecture icon terms" \
  --license-url "https://learn.microsoft.com/azure/architecture/icons/"

# Fetch selected brand marks from a pinned Simple Icons release
python3 tools/icon-catalogue/iconctl.py simple-icons amazonaws microsoftazure googlecloud kubernetes docker apachekafka postgresql redis terraform grafana

# Inspect and validate the catalogue
python3 tools/icon-catalogue/iconctl.py list
python3 tools/icon-catalogue/iconctl.py list azure
python3 tools/icon-catalogue/iconctl.py audit
python3 tools/icon-catalogue/iconctl.py normalize
```

## Behaviour and safeguards

- Python standard library only; no runtime package installation.
- Downloads are HTTP(S)-only, time-limited, and capped at 8 MiB per asset.
- Only valid SVG documents are accepted. Normalization adds missing dimensions and derives a viewBox only when numeric dimensions make that safe; it does not redraw artwork.
- Files are stored under `icon-library/<provider>/<asset-id>.svg`.
- SHA-256 hashes detect modifications and identical assets.
- Every record captures source URL, retrieval date, license, license URL, attribution, and trademark notice.
- ZIP import ignores path traversal entries and non-SVG files.
- The CLI does not infer a license. Unknown terms remain `UNSPECIFIED` and appear in audit warnings.
- The Simple Icons command pins a release version. Its CC0 artwork license does not waive trademark rights; consult its disclaimer and any per-icon license metadata.

## Catalogue record

`icon-library/manifest.json` is the source of truth. Paths are repository-relative. A duplicate asset reuses the existing file path but retains its own provider/name/source metadata record.

## Vendor pack workflow

For official provider packs, manually obtain the current ZIP from the vendor's official page, review the terms, then run `import-zip`. This intentionally avoids scraping pages or guessing undocumented download endpoints. Preserve the vendor's terms; do not label assets MIT/CC0 unless the source explicitly says so.

## Exit codes

- `0`: success
- `1`: audit/normalization found invalid assets or Simple Icons fetch had failures
- `2`: invalid arguments, download or input error
