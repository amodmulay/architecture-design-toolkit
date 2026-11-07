#!/usr/bin/env python3
"""Manage a local, provenance-aware SVG icon catalogue. Python 3.10+, stdlib only."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
import zipfile
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
ICON_ROOT = ROOT / "icon-library"
MANIFEST = ICON_ROOT / "manifest.json"
MAX_DOWNLOAD_BYTES = 8 * 1024 * 1024
USER_AGENT = "architecture-design-toolkit-iconctl/0.1"


def slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    if not value:
        raise ValueError("Asset id/name must contain letters or numbers")
    return value


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_manifest() -> dict:
    if not MANIFEST.exists():
        return {"schema_version": "1.0", "assets": []}
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(data.get("assets"), list):
        raise ValueError("Manifest must contain an assets array")
    return data


def write_manifest(data: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    temp = MANIFEST.with_suffix(".json.tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(MANIFEST)


def normalize_svg(raw: bytes) -> bytes:
    """Validate SVG and add a viewBox/dimensions only when safely inferable."""
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError(f"Invalid SVG/XML: {exc}") from exc
    if root.tag.split("}")[-1].lower() != "svg":
        raise ValueError("Document root is not an SVG element")

    view_box = root.get("viewBox") or root.get("viewbox")
    if not view_box:
        width = root.get("width", "")
        height = root.get("height", "")
        w = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(?:px)?\s*", width)
        h = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(?:px)?\s*", height)
        if w and h and float(w.group(1)) > 0 and float(h.group(1)) > 0:
            root.set("viewBox", f"0 0 {w.group(1)} {h.group(1)}")
    if not root.get("width"):
        root.set("width", "64")
    if not root.get("height"):
        root.set("height", "64")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def read_url(url: str) -> bytes:
    if not url.startswith(("https://", "http://")):
        raise ValueError("Only HTTP(S) URLs are supported")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content_type = response.headers.get("Content-Type", "")
            data = response.read(MAX_DOWNLOAD_BYTES + 1)
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Download failed: {exc}") from exc
    if len(data) > MAX_DOWNLOAD_BYTES:
        raise ValueError(f"Download exceeds {MAX_DOWNLOAD_BYTES} bytes")
    if "text/html" in content_type.lower() or data.lstrip().lower().startswith(b"<!doctype html"):
        raise ValueError("URL returned HTML, not an SVG asset")
    return data


def store_asset(*, asset_id: str, name: str, provider: str, raw: bytes,
                source_url: str, license_name: str, license_url: str = "",
                attribution: str = "", notes: str = "", license_status: str = "review-required") -> dict:
    asset_id = slug(asset_id)
    provider_slug = slug(provider)
    normalized = normalize_svg(raw)
    relative = Path(provider_slug) / f"{asset_id}.svg"
    destination = ICON_ROOT / relative
    digest = sha256(normalized)

    manifest = read_manifest()
    existing = next((a for a in manifest["assets"] if a.get("id") == asset_id
                     and a.get("provider") == provider), None)
    if existing and existing.get("sha256") == digest and destination.exists():
        return {"status": "unchanged", "id": asset_id, "path": str(Path("icon-library") / relative)}

    # Identical bytes are recorded as a duplicate reference, not copied again.
    duplicate = next((a for a in manifest["assets"] if a.get("sha256") == digest), None)
    if duplicate:
        asset_path = duplicate["path"]
        status = "duplicate"
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(normalized)
        asset_path = str(Path("icon-library") / relative)
        status = "added"

    record = {
        "id": asset_id,
        "name": name,
        "provider": provider,
        "path": asset_path,
        "format": "svg",
        "source_url": source_url,
        "license": license_name or "UNSPECIFIED",
        "license_url": license_url,
        "license_status": license_status,
        "attribution": attribution,
        "retrieved_on": date.today().isoformat(),
        "sha256": digest,
        "trademark_notice": "Brand names and logos may remain trademarks of their respective owners.",
        "notes": notes,
    }
    if existing:
        manifest["assets"].remove(existing)
    manifest["assets"].append(record)
    manifest["assets"].sort(key=lambda a: (a.get("provider", "").lower(), a.get("id", "")))
    write_manifest(manifest)
    return {"status": status, "id": asset_id, "path": asset_path, "sha256": digest}


def command_fetch(args: argparse.Namespace) -> None:
    raw = read_url(args.url)
    result = store_asset(
        asset_id=args.id or args.name, name=args.name, provider=args.provider, raw=raw,
        source_url=args.source_url or args.url, license_name=args.license,
        license_url=args.license_url, attribution=args.attribution, notes=args.notes,
        license_status=args.license_status,
    )
    print(json.dumps(result, indent=2))


def command_zip(args: argparse.Namespace) -> None:
    archive = Path(args.archive)
    if not archive.is_file():
        raise FileNotFoundError(archive)
    results = []
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            if info.is_dir() or not info.filename.lower().endswith(".svg"):
                continue
            # Ignore absolute paths and traversal entries in untrusted archives.
            member = Path(info.filename)
            if member.is_absolute() or ".." in member.parts:
                continue
            raw = zf.read(info)
            name = member.stem.replace("_", " ").replace("-", " ").strip()
            results.append(store_asset(
                asset_id=member.stem, name=name, provider=args.provider, raw=raw,
                source_url=args.source_url, license_name=args.license,
                license_url=args.license_url, attribution=args.attribution,
                notes=f"Imported from {archive.name}", license_status=args.license_status,
            ))
    print(json.dumps({"processed": len(results), "results": results}, indent=2))


def command_simple_icons(args: argparse.Namespace) -> None:
    """Fetch selected Simple Icons SVGs from a pinned npm release, never the moving latest tag."""
    slugs = [slug(s) for s in args.slugs]
    results = []
    for icon_slug in slugs:
        url = f"https://cdn.jsdelivr.net/npm/simple-icons@{args.version}/icons/{icon_slug}.svg"
        try:
            raw = read_url(url)
            results.append(store_asset(
                asset_id=icon_slug, name=icon_slug.replace("-", " ").title(),
                provider="simple-icons", raw=raw, source_url=url,
                license_name="CC0-1.0 (project-level; per-icon review required)",
                license_url="https://github.com/simple-icons/simple-icons/blob/develop/DISCLAIMER.md",
                attribution="Simple Icons contributors",
                notes=("Simple Icons project is CC0, but per-icon license metadata may differ; "
                       "review the icon entry and trademark guidance before redistribution."),
                license_status="review-required",
            ))
        except Exception as exc:
            results.append({"id": icon_slug, "status": "error", "error": str(exc)})
    print(json.dumps({"version": args.version, "processed": len(results), "results": results}, indent=2))
    if any(r.get("status") == "error" for r in results):
        raise SystemExit(1)


def command_normalize(_: argparse.Namespace) -> None:
    manifest = read_manifest()
    changed = 0
    errors = []
    for asset in manifest["assets"]:
        path = ROOT / asset["path"]
        try:
            normalized = normalize_svg(path.read_bytes())
            path.write_bytes(normalized)
            asset["sha256"] = sha256(normalized)
            changed += 1
        except Exception as exc:
            errors.append({"id": asset.get("id"), "error": str(exc)})
    write_manifest(manifest)
    print(json.dumps({"normalized": changed, "errors": errors}, indent=2))
    if errors:
        raise SystemExit(1)


def command_audit(_: argparse.Namespace) -> None:
    manifest = read_manifest()
    errors, warnings = [], []
    seen_ids = set()
    for asset in manifest["assets"]:
        key = (asset.get("provider"), asset.get("id"))
        if key in seen_ids:
            errors.append(f"Duplicate catalogue key: {key}")
        seen_ids.add(key)
        for field in ("id", "name", "provider", "path", "source_url", "license", "sha256"):
            if not asset.get(field):
                errors.append(f"{key}: missing {field}")
        if asset.get("license") in ("UNSPECIFIED", "UNKNOWN", "") or asset.get("license_status", "review-required") != "reviewed":
            warnings.append(f"{key}: license/terms review required")
        path = ROOT / asset.get("path", "")
        if not path.is_file():
            errors.append(f"{key}: missing file {asset.get('path')}")
            continue
        try:
            normalized = normalize_svg(path.read_bytes())
            if sha256(normalized) != asset.get("sha256"):
                errors.append(f"{key}: SHA-256 mismatch (file changed outside iconctl)")
        except Exception as exc:
            errors.append(f"{key}: invalid SVG ({exc})")
    print(json.dumps({"assets": len(manifest["assets"]), "errors": errors, "warnings": warnings}, indent=2))
    if errors:
        raise SystemExit(1)


def command_list(args: argparse.Namespace) -> None:
    assets = read_manifest()["assets"]
    query = (args.query or "").lower()
    selected = [a for a in assets if not query or query in " ".join(
        str(a.get(k, "")) for k in ("id", "name", "provider", "notes")
    ).lower()]
    print(json.dumps(selected, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the architecture icon catalogue")
    sub = parser.add_subparsers(dest="command", required=True)

    fetch = sub.add_parser("fetch", help="Download one SVG from a direct HTTP(S) URL")
    fetch.add_argument("--url", required=True)
    fetch.add_argument("--id")
    fetch.add_argument("--name", required=True)
    fetch.add_argument("--provider", required=True)
    fetch.add_argument("--license", default="UNSPECIFIED")
    fetch.add_argument("--license-url", default="")
    fetch.add_argument("--license-status", choices=("review-required", "reviewed"), default="review-required")
    fetch.add_argument("--source-url", default="")
    fetch.add_argument("--attribution", default="")
    fetch.add_argument("--notes", default="")
    fetch.set_defaults(func=command_fetch)

    z = sub.add_parser("import-zip", help="Import SVGs from a vendor ZIP archive")
    z.add_argument("--archive", required=True)
    z.add_argument("--provider", required=True)
    z.add_argument("--source-url", required=True, help="Official page or download URL")
    z.add_argument("--license", default="UNSPECIFIED")
    z.add_argument("--license-url", default="")
    z.add_argument("--license-status", choices=("review-required", "reviewed"), default="review-required")
    z.add_argument("--attribution", default="")
    z.set_defaults(func=command_zip)

    simple = sub.add_parser("simple-icons", help="Fetch selected Simple Icons by slug")
    simple.add_argument("slugs", nargs="+")
    simple.add_argument("--version", default="16.36.0")
    simple.set_defaults(func=command_simple_icons)

    norm = sub.add_parser("normalize", help="Normalize all catalogued SVGs and refresh hashes")
    norm.set_defaults(func=command_normalize)

    audit = sub.add_parser("audit", help="Check files, SVG validity, hashes, and provenance")
    audit.set_defaults(func=command_audit)

    listing = sub.add_parser("list", help="List assets; optional substring search")
    listing.add_argument("query", nargs="?")
    listing.set_defaults(func=command_list)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        args.func(args)
    except (ValueError, RuntimeError, FileNotFoundError, zipfile.BadZipFile) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
