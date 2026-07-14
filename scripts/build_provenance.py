"""Build a deterministic checksum manifest for archived evidence snapshots."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data" / "raw" / "source_snapshots"
MANIFEST = ROOT / "data" / "raw" / "manifest.csv"
REQUIRED_METADATA = {
    "source_id",
    "publisher",
    "title",
    "url",
    "retrieved_date",
    "capture_type",
}


def read_metadata(path: Path) -> dict[str, str]:
    """Read the leading key-value metadata block from a snapshot."""

    metadata: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            break
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"Malformed metadata line in {path}: {line!r}")
        metadata[key.strip()] = value.strip()
    missing = REQUIRED_METADATA - metadata.keys()
    if missing:
        raise ValueError(f"Missing metadata in {path}: {sorted(missing)}")
    if metadata["source_id"] != path.stem:
        raise ValueError(
            f"Snapshot filename {path.stem!r} does not match source_id "
            f"{metadata['source_id']!r}"
        )
    return metadata


def build_manifest() -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for path in sorted(ARCHIVE.glob("*.txt")):
        payload = path.read_bytes()
        metadata = read_metadata(path)
        rows.append(
            {
                "source_id": metadata["source_id"],
                "relative_path": path.relative_to(ROOT).as_posix(),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "capture_type": metadata["capture_type"],
                "retrieved_date": metadata["retrieved_date"],
                "url": metadata["url"],
            }
        )
    return rows


def main() -> None:
    rows = build_manifest()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else []
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} checksums to {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
