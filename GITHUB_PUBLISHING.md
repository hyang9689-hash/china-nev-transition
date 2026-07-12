# Publish this project to GitHub

Nothing in this repository has been uploaded. Complete these steps when you are
ready to publish it under your own account.

## 1. Replace placeholders

Search for:

```text
Project Author
YOUR-GITHUB-USERNAME
```

Update `README.md`, `index.qmd`, `_quarto.yml`, `CITATION.cff`, and `LICENSE`.
Then rebuild with `quarto render` and commit the result.

## 2. Create an empty GitHub repository

On GitHub, create a repository named `china-nev-transition`. Do not initialize
it with a README, license, or `.gitignore`; those already exist locally.

## 3. Add the remote and push

Run from this folder, replacing the username:

```bash
git remote add origin https://github.com/YOUR-GITHUB-USERNAME/china-nev-transition.git
git push -u origin main
```

Check the remote before pushing:

```bash
git remote -v
git status
git log --oneline --decorate --graph --all
```

## 4. Enable GitHub Pages

In the GitHub repository:

1. Open **Settings → Pages**.
2. Under **Build and deployment**, select **GitHub Actions**.
3. Open **Actions** and confirm the `Test and publish Quarto site` run is green.
4. The deployment job will report the public page URL.

The workflow follows GitHub's custom Pages artifact flow: configure Pages,
upload `docs/`, and deploy through the protected `github-pages` environment.

## 5. Prepare the first release

After checking the live report and notebook:

```bash
git tag -a v0.1.0 -m "First reproducible China NEV transition preview"
git push origin v0.1.0
```

Create a GitHub release from that tag and use the `CHANGELOG.md` entry as the
release notes. Reserve `v1.0.0` for the independently audited final analysis.

## Official reference pages

- [GitHub: using custom workflows with GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Quarto: publishing to GitHub Pages](https://quarto.org/docs/publishing/github-pages.html)
