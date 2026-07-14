# Raw evidence archive

This directory contains small, redistribution-safe evidence snapshots rather
than copies of complete third-party pages. Each snapshot records the canonical
URL, retrieval date, the fields independently transcribed from that page, and
the statistical scope needed to interpret the values.

The approach preserves the audit evidence without republishing an entire
copyrighted page. It is also resilient to pages whose charts are rendered as
images or whose servers reject automated downloads.

## Integrity manifest

Run the following command from the repository root after adding or changing a
snapshot:

```powershell
python scripts/build_provenance.py
```

The command rebuilds `data/raw/manifest.csv` with one SHA-256 checksum and byte
count per snapshot. A checksum change therefore makes any later correction or
accidental edit visible in Git history.

Snapshots are evidence records, not new licenses for the underlying source.
Use the original URL and publisher terms before redistributing source material.
