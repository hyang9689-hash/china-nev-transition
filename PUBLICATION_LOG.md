# Publication and submission log

This file records the repository submission process so the public release can
be audited alongside the Git history.

## Release identity

- Release candidate: `0.2.0`
- Author: `ANDYLALALA`
- GitHub account: [`hyang9689-hash`](https://github.com/hyang9689-hash)
- Repository: [`hyang9689-hash/china-nev-transition`](https://github.com/hyang9689-hash/china-nev-transition)
- Site: [`hyang9689-hash.github.io/china-nev-transition`](https://hyang9689-hash.github.io/china-nev-transition/)
- Submission branch: `main`
- Data vintage: `2026-07-14`
- Publication date: `2026-07-15`

## Milestone history

| Commit | Milestone |
|---|---|
| `8791d6d` | v0.1.0 first-look release |
| `87a8f20` | Independent pre-2021 double-entry audit |
| `e65be68` | Archived evidence records and SHA-256 manifest |
| `f9e0ded` | Executable data dictionary and stronger schema tests |
| `5587588` | BEV/PHEV/FCEV composition and exports |
| `ba02911` | Fleet-turnover model and held-out validation |
| `99d8dc0` | Locked Python environment and CI parity |
| `55455f9` | Publication metadata cleanup |
| `65e02b2` | Rebuilt v0.2.0 site artifacts |
| `8498060` | Canonical owner changed to `hyang9689-hash` |
| `0237256` | Cross-platform archive checksum fix |

## Submission sequence

1. Verify the GitHub identity and canonical URLs.
2. Remove accidental root-level README render artifacts and replace all
   publication placeholders.
3. Run the locked clean rebuild: analysis, notebook execution, 20 tests,
   Quarto render, and artifact validation.
4. Commit the publication candidate and confirm a clean worktree.
5. Create or connect the GitHub repository and push `main` with tags.
6. Observe the GitHub Actions build and Pages deployment.
7. Verify the public report, notebook, figures, links, and responsive layout.

## Submission evidence

- New public repository created: [`hyang9689-hash/china-nev-transition`](https://github.com/hyang9689-hash/china-nev-transition).
- Local `main` connected to `origin` and the complete history plus `v0.1.0` pushed.
- Initial workflow run [`29381893656`](https://github.com/hyang9689-hash/china-nev-transition/actions/runs/29381893656) exposed a Windows/Linux newline mismatch in three archived-capture checksums.
- Commit `0237256` made snapshot text explicitly LF and registered the canonical committed-blob SHA-256 values; all 20 tests and all 7 integrity checks then passed on Linux.
- Workflow run [`29382104587`](https://github.com/hyang9689-hash/china-nev-transition/actions/runs/29382104587), attempt 1, reached Pages configuration and correctly reported that Pages had not yet been enabled for the new repository.
- GitHub Pages was enabled with `build_type: workflow` and HTTPS enforcement.
- Workflow run `29382104587`, attempt 2, completed successfully: both `build` and `deploy` were green.
- Live site verified on `2026-07-15 09:42 CST`: homepage, executed notebook, sitemap, robots file, and all three key figures returned HTTP 200.
- Live HTML contained the canonical `hyang9689-hash/china-nev-transition` link, contained no `andylalala` reference, included fleet-turnover and powertrain analysis, and rendered no notebook traceback.
- Release tag: `v0.2.0` (created after this evidence record is committed).
