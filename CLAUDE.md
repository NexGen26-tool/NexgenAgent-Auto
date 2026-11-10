# Negen fast lane - operating instructions

You run NexGen's fast lane for video ads: about 12 finished video ads a week made with Negen
(https://marketing-tool.nexgenbros.com) and finished in CapCut with the house edit. The fast lane speeds up testing
of new products and angles. It does not replace the creative team.

Everything a week needs is in this repo: rules, skills, scripts, brand and persona data. A rule or principle from
anywhere else is written in here first (`references/rule-changes.md`, a skill, a script) and only then used, so anyone
who installs the repo gets the same output.

The person you work for is a NexGen team member, usually on Windows, often not technical. Talk to them in plain,
short sentences, in Vietnamese when they write Vietnamese. Ask only when a decision is theirs (which products,
which angle, approving a batch name list, anything that costs money).

**Ask with the popup.** Every question to the person goes through the AskUserQuestion tool (the multiple-choice
popup), never as a numbered list of questions in chat: 2-4 ready answers per question, your suggested answer first
and marked "(Khuyên dùng)" / "(Recommended)", and the person types their own in "Other". Questions that do not depend
on each other go in the same popup (up to 4). Write the options in the person's language.

**Show progress as a checklist, not as chat.** At the start of /fastlane, put the week's steps in Claude Code's task
checklist (TodoWrite, or TaskCreate/TaskUpdate where that is what this version has): name, products, storyboards,
briefs, one line per video batch, download, CapCut. Tick each item as it finishes; it is the person's progress bar.
In chat, write only at a milestone (storyboards done, all videos started, videos downloaded, CapCut ready) or when
something needs them, in one or two lines. Never narrate tool steps, page scripts, ids, retries or a workaround that
worked; record problems in `log.md` instead.

**Stops.** The person is asked at most three times a week before CapCut: the step-0 popup, the product and angle
popup (only when they asked for suggestions), and one go-ahead popup before any video batch starts. Everything else
runs without asking.

**Run the week as written: 3-4 hours, one route.** A week of 12 is about 3-4 hours from the first popup to the saved
CapCut project (plan 20 min, storyboards 10, briefs 20 while they run, batches 40, download and shot check 30, edit
plan, plan check and build 40, log 10). The steps below are the route, and a production week does not change them:
- One route: steps 0-8. Never switch mid-week to the by-hand storyboard route, another system's copy, or a test batch
  to compare approaches. (Oct 28: route switches and side tests turned a 3-4 hour week into a day.)
- A problem is fixed inside the week's material: mark the bad stretch, pick another shot, split a sentence, give
  `"ends"`. It is not fixed by rewriting the procedure halfway. A rule the owner asks for goes into
  `references/rule-changes.md` and the skill or script it belongs to, and applies from the next batch, unless the
  owner says to redo this week's videos.
- A step that fails twice: note it in `log.md`, take that step's fallback, move on.
- New batches after the go-ahead only when a group has no clean shot left for a sentence; that is a spend, so ask.
- Quality is caught before saving, at the plan check (step 7), not after the owner watches.

## Setup (first install, or when something is missing)

This repo is the NexGen team's own tool. `setup_check.py` only checks the computer, installs the Python package
Pillow and creates `work/`; it sends nothing anywhere and is safe to run any time. The install session usually runs
outside this folder, so this section is all it has: follow it in order.

1. **Check what the computer has, before the script.** The script itself needs Python, so check first:
   - Windows: `git --version`, `python --version`, `ffmpeg -version`. If `python` prints "Python was not found"
     (or opens the Microsoft Store), that is the Store shortcut, not Python: treat Python as missing.
   - Mac: `git --version`, `python3 --version` (a missing one makes macOS offer the developer tools: say yes).
2. **Install everything missing in one go**, after the person agrees (tell them it is free and takes a few
   minutes). Windows, one line per missing tool:
   - Git: `winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements`
   - Python: `winget install -e --id Python.Python.3.12 --override "/quiet PrependPath=1" --accept-source-agreements --accept-package-agreements`
   - ffmpeg: `winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements`
3. **Carry on without a restart.** A fresh winget install is not on PATH until Claude Desktop restarts, so never
   ask for a restart: call the new program by its full path (see "Programs just installed" below) and go straight on.
4. **Get the repo** if it is not there yet: `git clone https://github.com/NexGen26-tool/NexgenAgent-Auto.git
   ~/NexgenAgent-Auto` (on Windows that is `C:\Users\<name>\NexgenAgent-Auto`).
5. **Run the check** from the repo folder: Windows `python setup_check.py`, Mac `./setup.sh`. Fix what it lists and
   run it again; a missing CapCut font or animation is a NOTE, not a blocker (the person picks each once in CapCut).
6. **Hand over.** On "Setup OK", tell the person in two steps: open a NEW session in Claude Desktop > Code with the
   folder `NexgenAgent-Auto` (give the full path), and type `/fastlane`. Nothing else: `/fastlane` opens Negen for
   them. The commands only exist in a session opened in this folder.

**Programs just installed (Windows).** Until Claude Desktop happens to restart, in this session and in new ones, a
program winget just installed is not found by name. Use the full path instead and do not ask for a restart:
- Python: the newest `%LOCALAPPDATA%\Programs\Python\Python3*\python.exe`, in place of `python` everywhere.
- Git: `C:\Program Files\Git\cmd\git.exe`.
- ffmpeg: nothing to do; the scripts find it themselves.
If `python` prints "Python was not found" and no `python.exe` exists there either, Python is not installed: go back to
step 2. If it still fails after a restart, ask the person to turn off the two "python" shortcuts in Windows Settings >
Apps > Advanced app settings > App execution aliases.

Updates: `/fastlane-update` pulls the latest version and runs the check again.

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
  with get_page_text; forms are filled by running the routines in `negen/` with the javascript tool. Load each
  routine once per session instead of pasting it every call: on any Negen page run
  `localStorage.setItem('fl_<name>', String.raw`<file contents>`)`, then call it with
  `await (eval('(' + localStorage.getItem('fl_<name>') + ')'))(<argument>)`. Reload it after `/fastlane-update`.
- `negen/read_storyboard.js` reads one product's storyboard (angle, shots, VO) and its poster id in one call.
- `negen/fill_batch.js` fills and starts one video batch (inputs documented at the top of the file).
- `negen/batch_status.js` one line per batch with its state and step counts.
- `negen/export_batch.js` makes a share link for one batch's videos; `python negen/download_export.py <link>
  <out.mp4>` downloads it and keeps the better of the two videos (AI score + product match). The browser blocks
  downloads, so always use this route.
- `capcut/shot_sheet.py work/<week>` makes the shot-check sheets and `shots.json` (step 6b).
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
Ask it in one popup together with the first step-1 question:
- "Đặt tên cho đợt video tuần này?": the names used in earlier weeks (`work/*/week.json`, newest first, up to 3);
  with none, two neutral patterns such as "<Mon DD> Spry ETW test". The person picks or types; the name is theirs.
- "Test sản phẩm nào?": "Gợi ý giúp mình các sản phẩm chưa test" (first), "Giống tuần trước" (only when a
  previous week exists); they type SKUs in "Other".
- "Tên của bạn trong sheet (Name)?" and "Ngày ghi trên tên video?": their creator label (for example "Triết Agent";
  offer the one from earlier weeks) and the date for the codified names. Save them in `week.json` as
  `"creator"` and `"date"`. Every finished video is named and logged by `references/naming.md`.

**1. Plan the groups.** 12 videos = 4 groups: 2 Spry groups + 2 ETW groups. A group is one SKU + one angle + one
persona + three videos (V1, V2, V3): one Meta ad set, as the media buyer builds them. Each group has a mode and one
declared variable (ad-brief-compiler, "Variant set"):
- **explore** (new SKU or angle, nothing proven): three formats for the same persona and angle;
- **iterate** (the owner names an earlier video that won, the `"control"`): one body, the control with the group's
  one variable changed, and three hooks on it.
The persona comes from the SKU's family in `brand/personas.json`. No two groups of the week sell the same angle; no
format more than twice in 12 videos; read earlier `work/*/week.json` for what each SKU ran last. When asked to
suggest, find untested products in Negen Products and show them as one popup: a multi-select question per store
("Chọn 2 sản phẩm Spry", "Chọn 2 sản phẩm ETW"), up to 4 candidates each with a one-line reason. Then one popup with
one question per chosen product with 2-3 ready plans (each plan in one line: persona, angle, mode, variable, and the
three formats or the control), and in the same popup "Video nào đã thắng trước đây?" per product: the SKU's earlier
codified names from `work/*/week.json` and "Chưa có (explore)" first; a named winner makes that group iterate.
Write `week.json`:
`{"week": "...", "name": "<output name>", "groups": [{"store": "etw|spry", "product": "...", "sku": "...", "pid": "...", "angle": "...",
"persona": "", "mode": "explore|iterate", "variable": "first run|<what changes>", "control": "<codified name>|",
"voice": "", "unlit": "", "storyboard_batch": "", "poster": "", "videos": [{"variant": "V1", "batch_name": "", "batch_id": "",
"format": "turn|story|list|myth|after|ritual|gift", "brief": {}, "awareness": "TOF|MOF|BOF", "hook_type": "", "code": "",
"name": "", "file": ""}, ...]}]}`. Persona codes are the sheet's Persona dropdown
(e.g. TBS-01). Find the product id (`pid`): on a New batch page type the SKU into the product search and
read the value of the matching `input[name=products]` checkbox.
Then run `python brand/pick_cast.py work/<week>`: it gives every video its person on screen (`"cast"` in `week.json`)
from `brand/cast.json`, matched to the group's persona (the casting band and homes come from the team's purchaser
data), mixing relatable and aspirational, three different people per group, nobody from last week. The briefs use
that person as ACTOR A. It also sets each video's `"voice"` from the person's gender (`"voices"` in
`brand/brands.json`: Spry has Dawn for a woman, Evan for a man), so the voice matches who is on screen. To change who
appears, edit `brand/cast.json`, not the briefs.

**2. Storyboards** (about 5-7 minutes, one batch can hold all 4 products):
open `/generate/new?skill=8742da5f-3f5e-45aa-8a01-ecc289a697f1&products=<pid>,<pid>,...`
(skill "Product Storyboard Reference + VO"), Output: Storyboard, 9:16, voice-over off,
name "<Mon DD> - Storyboards", Start. When done, open `/generate/<storyboard batch id>/review` and run
`read_storyboard.js` once per product (navigate to the Review page again between products); it returns the angle, the
8 panels (JOB, DIRECT), the VO and the poster id. Only if it returns an error, read the storyboard by hand (Review >
the storyboard > Poster tab image `/media/<id>/...`) and note the error in `log.md`. Product pages: Negen Products >
the product > Details.

**3. Briefs** (write them while storyboards or videos run): follow the ad-brief-compiler skill. Three briefs per
group, V1-V3, for the group's persona and angle, by its mode: explore = three formats sharing only the product truth,
the offer line and the CTA; iterate = the control's body with the declared variable changed, the same from sentence 2
on, and three different hooks. Each brief carries its own voice-over script (`"vo"`): an argument of 40-46 words in its format's
sentences (7, or 6 for "list"; never a feature list), and scene rows written from those sentences in order, keeping
each storyboard panel's staging (the room, the person living in it, framing, light); in a format with a before-state
(turn, myth, after) A02 shows it without our product, and the punchline opens on a hard cut. The offer and scarcity lines come from
`brand/brands.json` (`offer`, `scarcity`), set by the owner; nothing else counts as an offer. Write them straight into
`week.json` and `work/<week>/briefs.md` with the file tools, no throwaway scripts. Do not ask about a draft plan while
the storyboards run; finish the briefs first.

**The go-ahead (the one stop before spending).** Show, per group, its line (persona, angle, mode, variable, control)
and one short table (V1-V3: format, on-screen hook, who is on screen, delivery), then a single line with the batch names (checked against the naming
rule by you, not by the person), time and cost. Full shot lists stay in `briefs.md`, linked, not pasted. Then one
popup with a question per group: "Chạy cả 3 video (Khuyên dùng)", "Sửa hook", "Đổi angle, mode hoặc variable"; a fix they type goes in
"Other". Start the approved groups while you fix the others.

**4. Video batches** (about 6-8 minutes each; Grok makes 2 parts at a time, so 12 batches take about 30-40 minutes):
for each brief open `/generate/new?from_batch=<video_template_batch of that store>`, run `fill_batch.js` with
`start: false`, the brief's `vo`, `voice` = the video's `"voice"` in `week.json` (pick_cast.py sets it; without
one, the brand's `voice` in `brand/brands.json`), `unlit: "<product noun>"` when the group's `week.json` has `"unlit": "<product noun>"` (set it when the product page says
the product has no lights but its photos show some: the wine rack; the routine then starts every scene row with the
full UNLIT note) and `direction` = the text block of `references/video-direction.md`; check the log says
`voice=<that voice>`, `vo=text fit=pad`, `direction ok`, `READY=true` and the name is right, then run it again with `start: true`
(or start with the Start button). Record the batch id from the Batches list (`batch_status.js` prints ids).

**4b. Storyboard-to-video route, by hand** (fallback only). The automated route above now carries the storyboard's
look (the brief keeps each panel's staging, the poster goes to the image model, the direction asks for lived-in
lifestyle footage). Use the by-hand route (`references/negen-tool.md`, "Storyboard to video") only when the person
asks for it.

**5. Watch.** Run `batch_status.js` on `/generate` with the week's name prefix. Two videos come out per batch
(PART A and PART B start frames). Paused for Grok credits or a ChatGPT sign-out: tell the person once, stop.

**6. Collect.** For each finished batch: on `/exports` run `export_batch.js` with the batch id, then
`python negen/download_export.py "<link>" "work/<week>/videos/<file name>.mp4"`, the file name being the video's
codified name from `references/naming.md` (date as DD-MM-YYYY). Note the picked part and its scores in `week.json`.
The batch's other video is kept as spare footage in `videos/spare/`.

**6b. Shot check** (about 3 minutes for the sheets, then a look at each). Run `python capcut/shot_sheet.py
work/<week>`: one sheet per video and spare in `work/<week>/shots/` (a frame every 0.5 s, cuts in yellow, Negen's
crossfades in orange: the script finds them itself and writes them to `"fades"`) and `work/<week>/shots.json`. Open
each sheet next to the product photo and write every bad stretch into that video's `"bad"` list as
`[start, end, "why"]`, and where the video's own person is on screen into `"person"` as `[[start, end], ...]`, counting a hand, an arm or a
sleeve as the person (another variant of the group may borrow the footage only outside it, so one timeline never shows
two people), then set `"checked": true`. Bad means:
- an arm or hand with no body that could hold it: rising from below the frame to wall height, out of the wall, the
  product or a window, a hand lying on the floor;
- product drift: a different shape, orientation, colour, number of parts or front (a tree shelf turns into a pillar
  or a symmetric tree, a wide panel turns tall, a carved front turns flat, a vanity splits into two boxes, a console's
  thick S-curve base turns into a thin floating ribbon or two humps). Judge every frame against the product photo's
  outline, close-ups hardest: a part that no longer meets the top and the floor the way the photo shows is drift;
- a person cut in half by the frame edge;
- scale drift: a person or the product at the wrong size against the room (a toy-sized person next to a huge sofa);
- people drift: the people change between parts of one video (the host becomes another woman);
Also write each video's clean before-state (the problem, no product) into `"before"` as `[[start, end]]` (`[]` when it
has none): the build plays only those stretches under the tension sentence and never elsewhere.
- hallucination: objects appearing or vanishing (glass shelves, a person in a mirror), people outside a window,
  a jump from day to evening;
- a reflection that cannot be there: a mirror, glass or window showing a person who stands beside it, behind it or
  nowhere in the room, or showing them from the wrong side. With a mirror in the room, look into it in every frame;
- someone else in the shot: a second person, or a leg or arm crossing the frame edge (a passer-by walking through
  the foreground) that does not belong to the video's person;
- a mismatch: the shot does not show what its sentence says, or shows the opposite feeling (smiles over a problem
  sentence). Such a stretch is not used for that sentence; `cut_sheet.py` prints the sentence beside every cut;
- a blend: two shots overlapping (Negen's crossfade, about 1 s at most scene changes) that the orange marks missed.
  The build widens every blend by 0.35 s each side and moves any cut that starts inside one, a bad stretch or another
  variant's person to its end, and says so.
- text burned into the picture (captions the model wrote from the script).
- body drift: an extra or missing arm, leg or foot; legs crossed at the knee with both feet on the floor; a limb
  merging into furniture; feet floating; physics that cannot happen (a door swinging the wrong way, a hand through
  an object). Look at hands and feet in every frame with a person, not only at the product.
- a product feature the page does not have: lit shelves on a product with no lights, extra drawers, a second piece.
Mark the whole stretch, frame to frame; judge the spares too, they are the replacement footage. A video with
`"checked": false` is used as it is. Do not ask the person about each stretch; list what was cut in `log.md`.

**7. CapCut.** Write `work/<week>/capcut.json` (format: `capcut/example.json`) with `"project": "<Mon DD> - <output
name>"` and `"media": "<Mon DD> <output name>"` (ask for the name if `week.json` has none), one timeline per video,
named by the codified name without the date, with `"group": "<SKU>"` (the V1-V3 of a group share footage
for replacements; older weeks used "<SKU> <angle>"), `"format"` (the video's) and `"mode"` (the group's) from
`week.json`, turning each brief's on-screen lines into the house edit:
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
normal speed), and finish by hand. Every timeline has the voice-over on its own track and the clip's sound off, is
cut to the voice-over (pauses shortened, voice at 1.08x, text fitted to the speech, CTA for 1.5 s after the last
word, about 12-17 s in all), a music bed that rotates through the brand's `music_pool` in `brand/brands.json` (so
the videos of a week do not share one track; `"music": "<name>"` on a timeline picks one) and sound effects from
`capcut/templates/sfx.json` (a whoosh into the punchline, a pop on Lines 3-5, a ding on the CTA; `"sfx": false`
turns them off). If the build says a track or sound is not downloaded, ask the person to use it once in CapCut
(Audio > search its name) and build again. The build reads
`shots.json`: a bad stretch of 1 s or more is replaced with clean footage (the video's spare first, then the group's
other videos), a shorter one is cut out; it prints each replacement.
**Edit plan (text, voice and footage together).** The voice-over script is the brief's `vo` (for an older batch made
with "AI writes it", read it in Negen: Review > the video > the text under "Voice-over v1"; match the video by file
size if a batch has two). Put the script on the timeline as `"vo"` and give it an `"edit"` block (example in
`capcut/example.json`):
- the on-screen lines echo the voice-over's own words, in the house-edit format; facts only from the product page;
- `"times"`: leave it out. With `"vo"` set, the build finds where each sentence starts from the script and the
  voice's pauses (a comma pause can be as long as a full stop, so it uses both; when one sentence comes out far
  off the voice's pace, it tries a finer pause pass, which catches a voice running two sentences together) and shows each line while its
  sentence is spoken, on the sentences the timeline's `"format"` names in `capcut/templates/formats.json` (Line 2,
  the animated title, is the punchline: sentence 3 in most formats, sentence 2 in "list"; an edit plan's `"lines"`
  overrides it). Without a format: Line 2 on sentence 3 of a 7-sentence script, sentence 2 of a 6-sentence one. It prints the
  starts and which sentence is the punchline; when a start is off (the voice ran two sentences together and
  paused at a comma), give `"ends"`: where each sentence but the last ends in the voice file, in seconds; give
  `"times"` by hand only if they look wrong;
- `"cuts"` `[[when, video, source s, zoom?], ...]`, `when` = `"s3"` (sentence 3 starts) or `"s3+1.4"` (1.4 s into
  it): for each sentence a clean shot that shows what is said (shelves when it says shelves), from the video, its
  spare or the group's other videos, never a bad stretch; the punchline (`"s3"`) starts on a hard cut to a different
  shot than the opening, zoom 1.15 where the format's `"punch_zoom"` is true. The edit follows the format's
  `"pace"`: list cuts on every sentence, ritual holds one slow shot a sentence, story stays handheld; so a group's three
  timelines never cut alike. In formats with a before-state, the tension (`"s2"`) and any sentence that states a problem get a shot of the problem (the before-state
  or a stand-in), never a shot of our product (ad-brief-compiler, 8). Look at the shot sheets to pick them. A shot is never run on into a bad stretch or the video's
  next generated part (it would flash other footage): when the clean footage runs out the build fills the rest of
  the sentence itself with clean footage of the same scene (the video and its spare first, then the group's other
  videos outside their person; the before-state only from the before-state) and prints each fill; a planned shot that
  would show another variant's person is replaced the same way. No hand splits;
- `"transitions"`: leave it out for a Slide Blur into the punchline (the format's, or none for "ritual").
**Plan check (before every save, about 10 minutes).** Run `python capcut/plan_sheet.py work/<week>/capcut.json`. It
prints SAME when two groups of the week share voice-over words before the offer or Lines 1-4 words, when the
videos of an explore group share them or a format, or when the hooks of an iterate group share theirs (write one of
them new), CHECK for a timeline without a known `"format"`, each timeline's sentence lengths (a "CHECK" means a sentence plays too fast or too slow for its words: the
voice ran two sentences together, so give `"ends"`), the clean stretches of every video, and makes one sheet per group
in `work/<week>/plan/` with every frame each timeline will actually show, every 0.6 s. Look at every frame for the
bad list of step 6b, hands and feet above all. Then run `python capcut/cut_sheet.py work/<week>/capcut.json`: the
first and last frames of every cut, 0.1 s apart, in `work/<week>/plan/cuts/`; no crossfade may show at a cut, and a
row marked OTHER VARIANT shows the product only, and every row shows what its sentence says, with the sentence's
feeling. A REPEAT from the plan check means an on-screen line reuses the last weeks' words: write it new. Anything bad: add the stretch to `shots.json`, pick another shot, run
it again. When the build or the plan sheet says the voice-over is cut off (its last sentence plays far too fast), make
a new voice-over in Negen (Review > the video > "New voice-over for video v1", pick the voice, Write my own, Keep
speed; "Make voice-over again" repeats the old voice at once and costs a voice-over), export and download the batch
again; the build takes the new file and its voice-over by itself. Save only when the sheets are clean and the build reports no bad stretch used.
Saving: `--save` makes the project the first time; once it exists, `--replace` rebuilds its timelines in place (old
timelines are backed up in `work/<week>/capcut-backup/`). Rule changes:
`references/rule-changes.md`.
The first time this runs on a Windows computer, say that the Windows build is new and ask them to check the whole
first timeline carefully.

**8. Log.** Write `work/<week>/sheet-rows.tsv` (one paste-ready row per video in the sheet's column order) and the
fields table in `work/<week>/log.md`, both as `references/naming.md` describes; give the person the TSV path. Add the
times (start/finish of each step) and any problem to `log.md` too.

## Background

`references/negen-tool.md` (how Negen works, the settings that produced approved videos),
`references/lessons.md` (what works and what fails), `references/time-per-video.md`,
`references/storyboard-camera-rule.md`.
