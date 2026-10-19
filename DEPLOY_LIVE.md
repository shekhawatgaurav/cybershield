# Publish CyberShield on GitHub Pages

Use the existing repository: https://github.com/shekhawatgaurav/cybershield

## Required settings

At https://github.com/shekhawatgaurav/cybershield/settings/pages select:

- Source: **Deploy from a branch**
- Branch: **main**
- Folder: **/docs**
- Save.

The entry point is `docs/index.html`. The expected public URL is https://shekhawatgaurav.github.io/cybershield/ . GitHub builds and deploys Pages after changes reach the selected branch. Check the **pages build and deployment** run under Actions and verify the public URL; an expected URL alone is not deployment evidence.

GitHub Pages hosts the HTML/CSS/JavaScript simulation only. It cannot execute the Python scanner. Keep `app.py` local.

## Publish subsequent changes

From this existing checkout, after checking changes and running tests:

```powershell
git status
git fetch origin
git diff origin/main
# Reconcile remote updates before committing/pushing if main has advanced.
git add README.md DEPLOY_LIVE.md VERIFICATION.md app.py demo_app.py cybershield docs examples tests tools .github .streamlit .gitignore project-report-addendum.html cybershield-project-report.pdf
git commit -m "Update CyberShield audit and portfolio demo"
git push origin main
```

Do not force-push. If Git prompts for authentication, use the Git Credential Manager browser sign-in as `shekhawatgaurav`. Do not paste passwords or tokens into project files or chat.

## Check a deployment

1. Confirm the intended commit and files are visible in the repository.
2. Check that the test workflow and Pages deployment finish successfully.
3. Open the public URL and confirm the score starts at 43 with the simulated-data notice.
4. Choose **After sample improvements**; the simulated score becomes 100.
5. Exercise the header filter and JSON download on desktop and mobile.

If the site returns 404, verify Pages is enabled and uses `main` / `/docs`, then inspect the Pages workflow. Allow the initial deployment to finish. If styling is missing, confirm `styles.css`, `app.js` and `demo-data.js` are alongside `index.html`. All references are relative so the `/cybershield/` project prefix works.

The `.nojekyll` file keeps the demo as plain static assets. No separate hosting subscription, backend, custom domain or API key is needed.

[GitHub documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
