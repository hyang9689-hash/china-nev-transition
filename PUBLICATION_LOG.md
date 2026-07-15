# Publication and submission log

This file records the repository submission process so the public release can
be audited alongside the Git history.

## Release identity

- Release candidate: `0.2.0`
- Author: `ANDYLALALA`
- GitHub account: [`andylalala`](https://github.com/andylalala)
- Repository: [`andylalala/china-nev-transition`](https://github.com/andylalala/china-nev-transition)
- Site: [`andylalala.github.io/china-nev-transition`](https://andylalala.github.io/china-nev-transition/)
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

The final commit, remote push, workflow run URL, Pages URL, and verification
timestamp will be added here after each action succeeds.
