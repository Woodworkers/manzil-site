# Manzil — Astro + GitHub + Netlify (Drive Image Sync)

**Edit copy in `src/content/home.json`.**  
**Drop/replace images in your Google Drive folder** — a GitHub Action pulls them into `/public/images` and redeploys your site.

## How to use this as your “GitHub-linked website”

1) **Create a new GitHub repo** (e.g., `manzil-site`) and upload these files.
2) **Netlify** → "Add new site" → "Import from Git" → pick your repo.  
   Build command: `npm run build`  |  Publish dir: `dist`
3) **Google Cloud** → create a **Service Account**, enable **Drive API**, create a **JSON key**.
4) **Share your Drive folder** (right-click in Drive → Share) **with the service account email** (the one ending in `iam.gserviceaccount.com`).
5) In GitHub **Settings → Secrets and variables → Actions → New repository secret**:
   - `DRIVE_FOLDER_ID` = `13uaGgs1IFzgmZZGcVCgNcMghrycTB9Tg`  (your folder)
   - `GOOGLE_SERVICE_ACCOUNT_JSON` = **base64** of the key JSON file contents
6) Go to **Actions** tab → run **“Sync Drive Images”** (workflow_dispatch) once.
7) The workflow downloads images to `/public/images`, commits, and Netlify will auto-redeploy.
8) Update `src/content/home.json` image paths to match your filenames (e.g., `/images/hero.jpg`, `/images/tile1.jpg` etc.).

> Mirror mode is ON: any image not in Drive will be removed locally, so this folder is your **single source of truth** for images.

## Editing content
- Headline, subhead, bullets, About text are all in `src/content/home.json`.  
- Colors and spacing are in `public/styles.css` (CSS variables at the top).

## Local dev (optional)
```bash
npm install
npm run dev
```

## Notes
- CTA is a simple `mailto:`; switch to `hello@manzil.in` anytime.
- If you change filenames in Drive, update the paths in `home.json` to match.
