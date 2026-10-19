# 🛡️ CyberShield — Automated Web Security Auditor

**Topic 2: Automated Web Scanner** · Python 3.10+ · Streamlit · Passive web security configuration checks

**Repository:** [github.com/shekhawatgaurav/cybershield](https://github.com/shekhawatgaurav/cybershield)  
**Live demo:** Add your Streamlit app link after deployment  
**Project type:** Cybersecurity portfolio / academic demonstration

CyberShield helps website owners and authorized security testers review *observed HTTP response configuration* without crawling, login attempts, exploits, or fuzzing. It checks HTTPS usage, common defensive response headers, a limited CORS reflection behavior, and flags on response cookies. Results are displayed in a dashboard and can be exported to JSON and a shareable, self-contained HTML report.

> **Important:** This is a student/portfolio demonstration and a *configuration audit*, not a complete vulnerability scanner, OWASP Top 10 assessment, penetration test or certification. Scores are illustrative. **Audit only websites you own or are explicitly authorized to test.** Do not publish the dashboard as an internet-facing URL scanner.

## 🌍 Public live portfolio demo (safe)

**Use `demo_app.py` when deploying to Streamlit Community Cloud**, not the locally intended `app.py`. The public demo uses simulated sample findings only and does not accept URLs or scan websites. It still provides interactive finding filters and downloadable JSON/HTML sample reports.

- Open [Streamlit Community Cloud](https://share.streamlit.io) and create an app from this GitHub repository.
- Choose branch `main` and **Main file path `demo_app.py`**.
- For step-by-step Hinglish instructions see [`DEPLOY_LIVE.md`](DEPLOY_LIVE.md).
- Optional static preview: enable GitHub Pages from the `main` branch `/docs` folder.

**Never deploy `app.py` as a publicly accessible scanner**; it has not been hardened against server-side request forgery in hostile, multi-user environments. Real authorized scans are for local operation only.

## ✨ Key features

- Streamlit dashboard: score, grade, audit checks, recommendations and one-click exports.
- Passive HTTP checks: HTTPS, HSTS, CSP presence, anti-framing, MIME sniffing and referrer policy.
- Simple CORS behavior probe: one additional harmless GET using `Origin: https://cybershield-audit.invalid`.
- Cookie attribute review: `Secure`, `HttpOnly`, `SameSite`. Stores **cookie names only**, not cookie values.
- Redirect safeguards: validate each redirect destination, stop cross-site redirects and limit to three hops.
- Rejects private, reserved and localhost IP addresses; TLS certificate validation is enabled.
- Offline demo (no real site queried), offline unit tests and GitHub Actions CI.
- JSON + HTML exports with HTML escaping of all untrusted text.

## 📁 Submission structure

```text
CyberShield/
├── app.py                        # LOCAL-ONLY scanner dashboard
├── demo_app.py                   # SAFE PUBLIC Streamlit demo (offline only)
├── DEPLOY_LIVE.md               # Hinglish GitHub + live deployment guide
├── cybershield-project-report.pdf  # Submission report
├── README.md                     # Project documentation
├── requirements.txt              # Dashboard dependency
├── launch_windows.bat            # Double-click Windows launcher
├── cybershield/
│   ├── __init__.py
│   ├── scanner.py                # Audit engine and CORS check
│   ├── cli.py                    # Command line interface
│   └── reports.py                # Offline HTML/JSON reports
├── docs/                          # GitHub Pages static HTML demo
│   └── index.html
├── examples/
│   ├── demo-audit.json
│   └── demo-audit.html
├── tests/test_scanner.py          # Offline tests
├── .github/workflows/tests.yml   # Continuous integration
├── .gitignore
└── LICENSE
```

## 🚀 Run on Windows (easiest)

1. Install [Python](https://www.python.org/downloads/) 3.10 or newer (tick **Add Python to PATH** if offered).
2. Extract the ZIP to a folder.
3. Double-click **`launch_windows.bat`**. The first run installs Streamlit and may take a few minutes.
4. Browser dashboard opens automatically (usually `http://localhost:8501`). Click **Explore offline demo** to see simulated sample findings.
5. For a real audit, enter your website URL and tick the permission confirmation checkbox.

Or launch manually from a terminal in the project folder:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell prevents environment activation, you can use `.venv\Scripts\python.exe -m streamlit run app.py` without activating the environment.

## ⌨️ No-install CLI (Python standard library only)

```bash
# Offline demo
python -m cybershield.cli --demo

# Save a simulated HTML report
python -m cybershield.cli --demo --format html --output demo-report.html

# Only scan a site you own or are explicitly permitted to assess
python -m cybershield.cli --url https://your-own-site.example --authorized

# Real JSON results for your authorized site
python -m cybershield.cli --url https://your-own-site.example --authorized --format json --output my-audit.json
```

The CLI uses Python's standard library. Only the dashboard needs the Streamlit dependency.

## ✅ Run the tests

```bash
python -m unittest discover -s tests -v
```

The test suite uses mocked DNS and synthetic responses. It does not access real websites.

## 🧠 How it works

```text
Permission confirmed
       ↓
Validate URL + public DNS addresses
       ↓
Request response headers (GET; no response body saved)
       ↓
Follow up to 3 validated redirects
       ↓
(Optional) one Origin reflection probe
       ↓
Analyze response configuration + cookie flags
       ↓
Heuristic 0–100 score + warnings + remediation
       ↓
Dashboard / JSON / HTML report
```

| Check | What it tests | Important limitation |
| --- | --- | --- |
| HTTPS | Final URL is HTTPS | Does not audit all TLS cipher suites or certificate lifecycle |
| HSTS | Positive `max-age`; duration | HSTS is meaningful only on HTTPS responses |
| CSP | Enforced CSP header present | Does **not** validate CSP directives for bypasses |
| Framing | `X-Frame-Options` or CSP `frame-ancestors` | Only observes one page's headers |
| Content type | `X-Content-Type-Options: nosniff` | Does not verify MIME type correctness |
| Referrer | Presence of `Referrer-Policy` | Policy value should be reviewed manually |
| CORS | Synthetic Origin reflection and credentials | One response is not proof of an exploitable issue or complete API audit |
| Cookies | `Secure`, `HttpOnly`, `SameSite` attributes | Cookie-specific exceptions may be intentional; no login responses tested |

**CORS nuance:** A server sending `Access-Control-Allow-Origin: *` with `Access-Control-Allow-Credentials: true` is misconfigured, but browsers reject credentialed sharing in that combination. CyberShield deliberately does **not** label it a credential-exfiltration exploit. For testing arbitrary-origin reflection with credentials, findings require the response to echo the supplied origin and explicitly enable credentials.

## 📐 Heuristic scoring

Start at 100, subtract 17 points for each `HIGH` warning, 10 for `MEDIUM`, 5 for `LOW`, and stop at 0. `INFO` observations are not penalized. Grades: A (90+), B (75+), C (60+), D (40+), F (<40). A high score is **not** a guarantee of security; checks are a narrow, page-level sample.

## 🔐 Security safeguards and privacy

- Only use an authorized public target URL; the tool blocks non-global IPs at validation time.
- Each redirect is validated and unrelated hostnames are blocked; request timeout defaults to 8 seconds.
- The app intentionally **does not** read response bodies or store cookie values, credentials, auth headers, or API keys.
- DNS-based destination checks alone are **not hardened SSRF prevention** (e.g. DNS rebinding). Keep this educational dashboard on your local computer.
- A valid HTTPS connection uses the platform's trusted CA certificates; verification is not bypassed.
- The CORS observation is deliberately limited. No exploit payloads, brute force, form submissions, or automated crawling are included.

## 💻 Academic submission / demo (about 2 minutes)

1. Show the four visible files `app.py`, `cybershield-project-report.pdf`, `README.md`, and `requirements.txt` in the folder.
2. Run `python -m unittest discover -s tests -v` to prove the test suite passes.
3. Start `launch_windows.bat` or run `streamlit run app.py`.
4. Click **Explore offline demo** and clearly explain the vulnerabilities are *simulated*.
5. Expand the CORS warning, show its explanation/remediation, then download the HTML report.
6. Open your GitHub repository to demonstrate documentation and GitHub Actions.

## 🐙 Upload to GitHub

1. Sign in at [GitHub](https://github.com/new) and create a **public** repository named `cybershield`.
2. Leave **Add a README**, **.gitignore** and **License** unchecked (already included).
3. Click **Add file → Upload files** on the empty repo (or follow the empty-repo upload prompt).
4. Drag **the contents inside your extracted CyberShield folder**, including the `cybershield`, `tests`, `examples`, `.github` directories and dotfiles. Do not upload the outer ZIP as your only file.
5. Write a message such as `Initial commit: CyberShield passive web auditor` and commit.
6. Open **Actions** to see the automated test workflow on subsequent pushes.

If your browser does not upload hidden `.github` or `.gitignore`, use Git instead:

```bash
git init
git add .
git commit -m "Initial commit: CyberShield passive web auditor"
git branch -M main
git remote add origin https://github.com/shekhawatgaurav/cybershield.git
git push -u origin main
```

**Suggested GitHub About description:** `CyberShield: Python + Streamlit passive web security auditor for HTTP headers, HTTPS, CORS origin behavior and cookie flags; includes reports and unit tests.`

**Suggested GitHub topics:** `cybersecurity`, `python`, `web-security`, `streamlit`, `http-headers`, `cors`, `security-audit`, `owasp`.


## Project presentation notes

For a class demonstration, explain the scanner's scope, run the offline unit tests yourself, then demonstrate the sample dashboard. The hosted Streamlit app is intentionally a **simulated portfolio demo**; the actual scanner can be run locally on a website you own or have authorization to test. Replace the live-demo placeholder above after publishing.

## 📚 References

- OWASP, [HTTP Security Response Headers Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html)
- MDN, [Cross-Origin Resource Sharing (CORS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
- MDN, [Why credentialed CORS cannot use `*`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS/Errors/CORSNotSupportingCredentials)
- GitHub Docs, [Adding a file to a repository](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)

## 📄 License

MIT. © 2026 CyberShield contributors. This project report and offline demo do not contain results from a real unauthorized website scan.
