# Negen fast lane - operating instructions

You run NexGen's fast lane for video ads: about 12 finished video ads a week made with Negen
(https://marketing-tool.nexgenbros.com) and finished in CapCut with the house edit. The fast lane speeds up testing
of new products and angles. It does not replace the creative team.

The person you work for is a NexGen team member, usually on Windows, often not technical. Talk to them in plain,
short sentences, in Vietnamese when they write Vietnamese. Setup: Windows `python setup_check.py`, Mac
`./setup.sh`; when it says Git, Python or ffmpeg is missing, offer to install it with the winget line it prints and
run it after they agree, then run the check again (a new terminal may be needed for ffmpeg to be found). Ask only when a decision is
theirs (which products, which angle, approving a batch name list, anything that costs money).

## Rules (never break these)

- The person signs in to Negen themselves. Never type a password, never create an account.
- Batch names: "<Mon DD> - <Product> <Angle> V1|V2|V3" (e.g. "Oct27 - Wall Art Focal Wall V2"). Never a person's
  name, never "Claude" or any tool name. Negen has no rename and no delete, so check every name before Start.
- Nothing that costs money without asking. Image and video engines are included in the subscription; Grok credit
  top-ups and ChatGPT sign-ins in 9router are an admin job: tell the person, do not try to fix it.
- Do not keep pressing Resume on a batch paused for credits: each try uses a request. Check once, report, wait.
- No text or logo editing inside Negen. The deliverable is the clean video with voice-over, finished in CapCut.
- Only product facts that the Negen product page states. Never invent offers, discounts, shipping or warranty.
- Never publish or post anything anywhere.

## Tools you use

- A browser you can drive: the Claude desktop app's built-in browser, or Claude in Chrome. Negen pages are read
  with get_page_text; forms are filled by running the routines in `negen/` with the javascript tool: read the file,
  then run `(<file contents>)(<argument>)` on the right page.
- `negen/fill_batch.js` fills and starts one video batch (inputs documented at the top of the file).
- `negen/batch_status.js` one line per batch with its state and step counts.
- `negen/export_batch.js` makes a share link for one batch's videos; `python negen/download_export.py <link>
  <out.mp4>` downloads it and keeps the better of the two videos (AI score + product match). The browser blocks
  downloads, so always use this route.
- `.claude/skills/ad-brief-compiler/SKILL.md` turns a storyboard + product facts into three Ad briefs (V1-V3).
- `capcut/build_project.py <config> [--save]` builds the CapCut project in the house edit (CapCut must be closed);
  `--check` says whether this computer's CapCut can take built projects. `capcut/text_sheet.py <config>` is the
  fallback when it cannot.
- Brand settings (logo, CTA, Negen brand id, template batch per store): `brand/brands.json`.
- Mac or Windows: run Python as `python3` on a Mac and `python` on Windows. Windows needs ffmpeg for the voice-over
  track. `python setup_check.py` (or `python3` on Mac) checks everything; run it when something fails.

## The week, step by step

Keep everything for a week in `work/<YYYY-MM-DD of the Monday> <output name>/`: `week.json` (output name, groups,
briefs, batch ids, picks), `videos/`, `capcut.json`, `log.md` (times and anything that went wrong). Read it first
if it exists and continue where it stopped.

**0. Ask for the output name.** Before anything else, ask the person what to call this week's outputs (for example
"ETW Spry Q4 test" or a campaign name). Never make one up and never default to "Fast lane". It is used for the work
folder, the CapCut project ("<Mon DD> - <output name>") and the CapCut media folder; save it in `week.json` as
`"name"`. If a week already has a name, reuse it. Negen batch names keep their own format (below).

**1. Plan the groups.** 12 videos = 4 groups: 2 Spry groups + 2 ETW groups. A group is one SKU + one angle +
three videos (V1, V2, V3) that differ only in hook and delivery, so Meta ad sets can be built per group. Ask which
SKUs to test (or propose untested ones from Negen Products and let the person choose). Write `week.json`:
`{"week": "...", "name": "<output name>", "groups": [{"store": "etw|spry", "product": "...", "sku": "...", "pid": "...", "angle": "...",
"storyboard_batch": "", "poster": "", "videos": [{"variant": "V1", "batch_name": "", "batch_id": "", "brief": {},
"file": ""}, ...]}]}`. Find the product id (`pid`): on a New batch page type the SKU into the product search and
read the value of the matching `input[name=products]` checkbox.

**2. Storyboards** (about 5-7 minutes, one batch can hold all 4 products):
open `/generate/new?skill=8742da5f-3f5e-45aa-8a01-ecc289a697f1&products=<pid>,<pid>,...`
(skill "Product Storyboard Reference + VO"), Output: Storyboard, 9:16, voice-over off,
name "<Mon DD> - Storyboards", Start. When done, open each storyboard in Review: read the angle, the 8 panels
(JOB, DIRECT) and the VO with get_page_text, and take the poster's media id from the Poster tab image
(`/media/<id>/...`). Product pages: Negen Products > the product > Details.

**3. Briefs** (write them while storyboards or videos run): follow the ad-brief-compiler skill. Three briefs per
group, V1-V3, same job/proof/offer/CTA and Lines 2-5, a different hook and delivery each. Show the person the
3-row variant summary per group before launching. Store each brief in `week.json`.

**4. Video batches** (about 6-8 minutes each; Grok makes 2 parts at a time, so 12 batches take about 30-40 minutes):
for each brief open `/generate/new?from_batch=<video_template_batch of that store>`, run `fill_batch.js` with
`start: false`, check the log says `READY=true` and the name is right, then run it again with `start: true`
(or start with the Start button). Record the batch id from the Batches list (`batch_status.js` prints ids).

**5. Watch.** Run `batch_status.js` on `/generate` with the week's name prefix. Two videos come out per batch
(PART A and PART B start frames). Paused for Grok credits or a ChatGPT sign-out: tell the person once, stop.

**6. Collect.** For each finished batch: on `/exports` run `export_batch.js` with the batch id, then
`python negen/download_export.py "<link>" "work/<week>/videos/NN_<Store>_<Product>_<Angle>_Vn.mp4"`
(NN = 01-12 in group order). Note the picked part and its scores in `week.json`.

**7. CapCut.** Write `work/<week>/capcut.json` (format: `capcut/example.json`) with `"project": "<Mon DD> - <output
name>"` and `"media": "<Mon DD> <output name>"` (ask for the name if `week.json` has none), one timeline per video,
named "NN <Product> <Angle> Vn", turning each brief's on-screen lines into the house edit:
- `line1` [big, small, accent]: the hook split into a short subject (2-4 words), the linking words, and the last
  1-3 words that carry the tension (shown in orange italic). No trailing period; a "?" is fine.
  "Big empty wall?" became ["Big empty wall", "leaves you feeling ", "unresolved?"].
- `line2` [setup, payoff]: the small italic setup ending in a space, then a 1-2 word payoff with a capital letter.
  "Give it a focal point." became ["Give it a ", "Focal point"].
- `line3` [left, right]: two halves; no period on the left one. "Solid wood. Real depth." became
  ["Solid wood", "Real depth."].
- `line4`: one line, no trailing period.
- `line5` [first, punch]: the punch is the second line, bigger and yellow. ["Every piece is", "one of a kind"].
- `cta`: the brief's call to action.
First run `python capcut/build_project.py --check`. If it says CapCut keeps its projects encrypted, run
`python capcut/text_sheet.py work/<week>/capcut.json` instead and give the person `work/<week>/text-sheet.md` with
the videos folder: every line, time and style to type in by hand. Otherwise ask the person to quit CapCut (Mac:
Cmd+Q; Windows: close it and quit it from the tray), run `python capcut/build_project.py work/<week>/capcut.json`
(dry run), then with `--save`. Tell them to open CapCut, check one timeline end to end (text fits, VO plays at
normal speed), and finish by hand. Every timeline has the voice-over on its own track and the clip's sound off.
The first time this runs on a Windows computer, say that the Windows build is new and ask them to check the whole
first timeline carefully.

**8. Log.** Add the times (start/finish of each step) and any problem to `work/<week>/log.md`.

## Background

`references/negen-tool.md` (how Negen works, the settings that produced approved videos),
`references/lessons.md` (what works and what fails), `references/time-per-video.md`,
`references/storyboard-camera-rule.md`.
