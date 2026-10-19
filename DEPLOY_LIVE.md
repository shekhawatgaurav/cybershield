# CyberShield ko GitHub + Live kaise karein (Hindi / Hinglish)

## STEP 1: ZIP download aur extract

`CyberShield_Final_GitHub_Ready.zip` download karo, right-click -> **Extract All**. Extracted `CyberShield` folder kholo. `app.py`, `demo_app.py`, `README.md`, `requirements.txt` aur subfolders dikhne chahiye.

## STEP 2: GitHub par repository

1. https://github.com par sign up / log in karo.
2. https://github.com/new kholo.
3. **Repository name:** `cybershield`
4. **Description:** `Educational passive web security auditor with a Streamlit portfolio demo.`
5. **Public** choose karo. **Add a README**, **.gitignore**, aur **License** = off/none rakho (ye files ZIP me already hain).
6. **Create repository** dabao.

## STEP 3: Files GitHub par upload

1. Repository me **uploading an existing file** (ya **Add file > Upload files**) kholo.
2. Extracted `CyberShield` folder *ke andar ka saara content* select aur drag-drop karo. Pura ZIP akela upload nahi karna.
3. Make sure `demo_app.py`, `app.py`, `README.md`, `requirements.txt`, `cybershield/`, `docs/`, `tests/`, `.github/workflows/tests.yml` sahi paths par aa gaye.
4. **Commit changes** karo.
5. GitHub repository home pe `README.md` automatically display hona chahiye. **Actions** tab me automated tests check karo.

**Tip:** Agar web uploader hidden `.github` folder ya paths preserve na kare, Git install karke local `CyberShield` folder me terminal kholo:

```bash
git init
git add .
git commit -m "Initial CyberShield release with safe demo"
git branch -M main
git remote add origin https://github.com/shekhawatgaurav/cybershield.git
git push -u origin main
```

Git push karte samay GitHub par sign in karna pad sakta hai.

## STEP 4: Live interactive demo via Streamlit (recommended)

1. https://share.streamlit.io kholo aur GitHub se login/connect karo.
2. **Create app** > **Yup, I have an app** select karo.
3. Details:
   - Repository: `shekhawatgaurav/cybershield`
   - Branch: `main`
   - Main file path: **`demo_app.py`** (important! `app.py` nahi)
   - App URL (optional): `cybershield-portfolio-demo` (availability ke hisaab se)
4. **Deploy** click karo; kuch minutes wait karo.
5. Live URL ko copy karke README me **Live Demo** ke paas link add kar sakte ho.

⚠️ `demo_app.py` ONLY: public app simulated security observations dikhata hai, JSON/HTML reports download karta hai aur koi network scan nahi karta. Full scanner `app.py` ko public internet par expose na karo; it is for local use only. Demo output ko real vulnerabilities mat bolo.

## OPTIONAL STEP 5: Free static report site via GitHub Pages

1. GitHub repo > **Settings** > **Pages**.
2. Source: **Deploy from a branch**.
3. Branch: `main`; folder: **`/docs`**; then **Save**.
4. GitHub Pages will display a URL like `https://shekhawatgaurav.github.io/cybershield/` after publishing.
5. Ye ek static HTML demo report hai, interactive Python dashboard nahi.

## STEP 6: Local machine par real scanner

Windows par `launch_windows.bat` double click karo. `http://localhost:8501` par real scanning (authorized website only) aur offline demo dono milenge.

### Submission tip

Teacher ko 3 links/files do: GitHub repository URL, Streamlit live demo URL, `cybershield-project-report.pdf`. Demo simulations ko clearly explain karo.

**Docs:** https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy and https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
