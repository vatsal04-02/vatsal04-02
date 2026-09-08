# Setup guide — vatsal04-02/vatsal04-02

## What's in this folder
```
README.md                        <- the actual profile page (renders on github.com/vatsal04-02)
SETUP.md                         <- this file
.github/workflows/refresh-stats.yml
scripts/
  gh_graphql.py                  <- stdlib-only GraphQL client
  fetch_data.py                  <- contributions, streaks, languages
  svg_common.py                  <- shared colours, ramp, font embedding
  svg_stats.py                   <- hero total + sparkline
  svg_streak.py                  <- streak card
  svg_langs.py                   <- top languages bar chart
  svg_year.py                    <- year grid, ramp characters
  generate_stats.py              <- orchestrator the workflow runs nightly
  generate_portrait.py           <- run locally, once, to build portrait.svg
  build_font_subsets.sh          <- run locally, once, to embed a font
  requirements-portrait.txt      <- deps for generate_portrait.py ONLY
fonts/                           <- put ramp.woff2 / headings.woff2 / basic-latin.woff2 here
```

Note: `generate_stats.py` and everything it imports uses **only the Python
standard library**. `requirements-portrait.txt` is for the portrait
pipeline, which you run by hand on your machine, never in CI.

---

## Step 1 — push this repo

```bash
cd vatsal04-02        # this folder, already named to match your username
git init
git add .
git commit -m "init: self-generating profile"
git branch -M main
git remote add origin git@github.com:vatsal04-02/vatsal04-02.git
git push -u origin main
```

If you haven't created the GitHub repo yet:
```bash
gh repo create vatsal04-02 --public --source=. --push
```
The repo name must match your username exactly, or GitHub won't treat it
as your profile README.

## Step 2 — generate the portrait (local, one-time)

```bash
cd scripts
pip install -r requirements-portrait.txt
python3 generate_portrait.py /path/to/your/photo.jpg -o ../portrait.svg
```

Photo checklist before you shoot it:
- side light (~45°), not flat frontal light
- tight crop, chin to just above the hair
- 1200px+ resolution
- plain background, and don't wear black against a dark wall
- slight angle, not dead-on

First run downloads rembg's background-removal model (~176MB) — one-time,
then cached in `~/.u2net`.

Open `../portrait.svg` in a browser to check it before committing. If the
face looks washed out, that's the `(v/255)^1.7` darkening curve in
`generate_portrait.py::enhance()` — you can push the exponent higher
(e.g. 2.0) for more contrast on a naturally low-contrast photo.

Commit it:
```bash
git add ../portrait.svg
git commit -m "add portrait"
git push
```

## Step 3 — embed a font (local, one-time, fixes the Windows-width bug)

Without this, JetBrains Mono / your chosen font isn't available and every
SVG falls back to the visitor's system monospace — which on Windows
(Consolas, ~0.55 advance vs the grid's 0.600) renders your portrait about
7% narrower than you designed it.

```bash
# download JetBrains Mono (SIL OFL) first, e.g.:
curl -L -o JetBrainsMono.zip \
  https://github.com/JetBrains/JetBrainsMono/releases/latest/download/JetBrainsMono-2.304.zip
unzip -j JetBrainsMono.zip "fonts/ttf/JetBrainsMono-Regular.ttf" "fonts/ttf/JetBrainsMono-Bold.ttf" -d .

pip install fonttools brotli
cd scripts
chmod +x build_font_subsets.sh
./build_font_subsets.sh ../JetBrainsMono-Regular.ttf ../JetBrainsMono-Bold.ttf
```

This writes `fonts/ramp.woff2`, `fonts/headings.woff2`, `fonts/basic-latin.woff2`.
Copy the font's `LICENSE.txt` (OFL) into `fonts/` too — it's going into a
public repo, so the license needs to travel with it.

Re-run the portrait + stats scripts after this so the fonts get embedded:
```bash
python3 generate_portrait.py /path/to/photo.jpg -o ../portrait.svg
```

Commit `fonts/` and the regenerated SVGs.

## Step 4 — turn on the nightly workflow

Nothing to configure — `.github/workflows/refresh-stats.yml` uses the
built-in `GITHUB_TOKEN`, which GitHub injects automatically. Just make
sure Actions are enabled for the repo (Settings → Actions → General →
"Allow all actions").

Trigger it once by hand to verify before waiting for the 05:17 UTC cron:
```bash
gh workflow run refresh-stats.yml
gh run watch
```

If it fails, check:
- **Settings → Actions → General → Workflow permissions** is set to
  "Read and write permissions" (needed for the job to `git push`).
- The Action log for the exact GraphQL error — `gh_graphql.py` surfaces
  the raw API response on failure.

## Step 5 — validate against GitHub's actual markdown sanitiser

Before trusting any manual edits to `README.md`, check what survives:
```bash
curl -s -X POST https://api.github.com/markdown \
  -H "Authorization: bearer $(gh auth token)" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --rawfile text README.md '{text:$text,mode:"markdown"}")" \
  | less
```
Look for anything you added — a `<style>` block, a `class=`, an inline
`<svg>` — getting silently stripped. If it's gone from this output, it'll
be gone on your profile too.

## Step 6 — the two things the API can't do

- **Pinned repositories** — set manually via the UI (Customize your pins
  on your profile page). No GraphQL mutation exists for this.
- **Bio** — the REST endpoint needs a `user` scope your CLI token won't
  have by default. Set it manually in Settings → Profile.

## Step 7 — force the first render

New profile READMEs are sometimes cached. If `README.md` doesn't show up
on `github.com/vatsal04-02` after pushing, open it in the web UI and make
a trivial edit (add then remove a space) to force a refresh.

## Verifying the animation locally

A full-page headless-Chrome screenshot restarts SMIL and gives you a
blank result — use a tall fixed viewport instead, and wait for the
typing duration `generate_portrait.py` prints at the end
(`rows * 0.09 + 0.4` seconds).

```bash
node -e "
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: 900, height: 1400 });
  await page.goto('file://' + process.cwd() + '/portrait.svg');
  await new Promise(r => setTimeout(r, 6000));
  await page.screenshot({ path: 'check.png' }); // NOT fullPage: true
  await browser.close();
})();
"
```

## Ongoing maintenance

Nothing, day to day — the workflow commits only when the numbers actually
change. The only times you touch this again:
- new photo → re-run `generate_portrait.py`
- want a different font → re-run `build_font_subsets.sh`
- want a different chart layout → edit the relevant `scripts/svg_*.py`,
  the orchestrator and workflow don't need to change
