# Rule changes

Changes to how the fast lane works, newest first: what changed, why, and what it was tested on.

## 2026-10-28 (night) - Run the week as written; catch drift before saving; fewer hand fixes

**Why:** this week took most of a day instead of 3-4 hours. The route was switched three times (storyboard-to-video
by hand, the creative team's copy, then two test groups), every switch redid briefs, batches and edits, and problems
surfaced only when the owner watched: an extra foot on the chair, a cupboard door swinging the wrong way, a wine rack
drawn lit, two voice-overs timed wrong.

**What changed:**
- `CLAUDE.md` "Run the week as written": one route (steps 0-8) for the whole week, no mid-week route switches or
  side tests, problems fixed inside the week's material, a rule change applies from the next batch, a step that fails
  twice is logged and skipped to its fallback, quality is caught at the plan check before saving.
- Shot check (6b) bad list: body drift (an extra or missing limb, crossed legs with both feet on the floor, a limb
  merging into furniture, floating feet, impossible door or hand physics) and product features the page does not have
  (lit shelves).
- New plan check (`capcut/plan_sheet.py`, step 7, before every save): sentence lengths with a CHECK when one is far
  off the voice's pace, the clean stretches of every video, and a sheet per group with every frame each timeline will
  show. Found five drifts on the final 12 that the per-video sheets had missed.
- `build_project.py`: when the sentence match leaves one sentence far off the voice's pace (letters a second), it
  tries the finer pause pass and keeps the more even reading. Right on all 30 voice-overs of the week, including the
  two that needed `"ends"` by hand; the 12 Oct 31 and look-test timings unchanged. `--save` on an existing project
  now says to use `--replace`.
- `fill_batch.js` `unlit`: the full UNLIT note on every row by itself (week.json group `"unlit": "wine rack"`).
- `ad-brief-compiler` + `video-direction.md`: simple poses (stand, walk, sit upright with both feet down), one simple
  action per row, nothing opened on camera, high shelves reached by a whole person.

**Tested on:** the final 12 of the week (`work/2026-10-26 NegenAgent - Oct31/final/`).

## 2026-10-28 (evening) - The script is an argument: 7 sentences, a brand voice, the owner's offer

**Why:** the look test's console had the right look and edit, but the owner found its argument a feature list ("An
oval top on an S-curve base. Keys down, palm on the grain. Six widths.") next to the creative team's Oct 31 copy,
which moved from a stake to a before-state to a turn, then cleared a doubt and closed on an offer. The brief skill's
"sentence n says Line n" slots, with Lines 3-5 shared, filled up with features. The template's default voice also
read flatter than the voice picked per group on Oct 31.

**What changed:**
- `ad-brief-compiler`: the voice-over is 7 sentences, 40-46 words, one job each: hook, tension, turn (punchline),
  reason ("so" / "because"), doubt cleared, offer or scarcity, CTA. No sentence only names a feature. Owner register
  (first person in the tension and the turn). Scene rows follow the sentences: A02 the tension's before-state with no
  product of our kind in frame, A03 the punchline on a hard cut back to our product.
- `brand/brands.json`: `voice` (Spry Dawn, ETW Evan), `offer` (store-wide, set by the owner: Spry free delivery, ETW
  free shipping, code FS) and `scarcity` (no number, no deadline). These are the only offers the briefs may use.
- `fill_batch.js` picks the voice by name and reports it; READY needs it. Its product search waits up to 19 s and
  searches again once.
- `build_project.py`: a 7-sentence script keeps Line 1 up through the tension, starts the punchline (Line 2, the
  whoosh and the Slide Blur) on sentence 3 and accepts cuts named "s1".."s7". 6-sentence scripts time as before
  (all 12 Oct 31 timelines unchanged).
- `batch_status.js` gives batches that share a name their own ids (page order).
- `build_project.py` stops a planned shot at its next bad stretch too (slowing it to fit), so a shot never runs
  through a blend into the next scene, such as the tension walk into the console. `download_export.py` prints
  Vietnamese file names on Windows.

**Tested on:** the curved console, three new batches "Oct28 - Curved Console Define Piece V1-V3" (`work/2026-10-26
NegenAgent - Oct31/arc-test/`).

## 2026-10-28 (later) - The automated route takes the storyboard's look

**Why:** the owner wants the look of the Oct 31 batch (made by hand from the storyboard's own panels: a person living
with the product in a lived-in room, eye-level medium and wide frames, warm low sun) with the repo's automation and
argument. Comparing the shot sheets: the automated route's footage was a hand-led product demo (macros, crane and
top-down moves, hands with no body, sparse rooms). Two causes: the brief rules replaced each panel's staging with a
hand action and energetic camera moves, and the poster reached the image model only as a text summary.

**New rules:**
- ad-brief-compiler: the storyboard sets the look, the brief the argument; scene rows keep each panel's staging.
  Hook = a person using the product in the first 2 s (body in frame). Camera: one real move per row, at least 5 of 8
  rows eye-level medium or wide with the person in the room, at most 2 close details, no crash zooms, whip pans,
  top-down floor shots or extreme macros. ACTOR A is a whole person described once.
- `fill_batch.js` ticks "Also send this image to the image model" on the poster and only says READY when it is on.
- `references/video-direction.md` opens with the lifestyle look.
- The by-hand storyboard route (CLAUDE.md 4b) is a fallback only.

**Checked:** `fill_batch.js` on the real form for the curved console, not started: poster Style + Composition +
Lighting, sent to the image model, VO Keep speed, direction set, READY=true. Then run as one group (curved
console V1-V3, `work/2026-10-26 NegenAgent - Oct31/look-test/`): all three came out in the Oct 31 look (lived-in
sunlit entry, the woman with her keys, guests arriving, the console true in wide shots), AI 8-8.5, match 8.5-9,
about 10 minutes for the three. Still there: blends at scene changes, drift in two close-ups (V2), and V3's picked
video had the script's captions burned into the picture; the shot check now lists burned-in text as bad.

## 2026-10-28 - A problem line gets a picture of the problem; text timed from the script; music and sound per video

**Why:** the owner's review of the Oct 31 batch: a "plain, soulless console" line played over our own console; text,
voice and footage did not match; all 12 videos had one music track, no sound effects and no accent.

**New rules:**
- ad-brief-compiler 8: a problem or contrast line is fine; its scene shows the problem (the before-state or an
  unbranded stand-in) and our product only arrives with the answer, on a hard cut. In the edit plan the problem
  sentence never plays over a shot of our product. (A first version banned the words themselves; the owner
  ruled the argument fine, only the execution wrong, so that ban was removed the same day.)
- ad-brief-compiler 4: an UNLIT note leads every row when the product photos are lit but the page sells no lights.
- CapCut edit plan: `"vo"` on each timeline; the build times the lines from the script's sentences and the voice's
  pauses; cuts are named by sentence (`"s3"`, `"s3+1.4"`); a shot is slowed rather than run into the next generated
  part.
- Music rotates through `music_pool` per brand; sound effects from `capcut/templates/sfx.json` (whoosh into the
  punchline, pops on Lines 3-5, ding on the CTA).
- The storyboard-to-video route is written down (`references/negen-tool.md`, CLAUDE.md 4b).

**Checked:** built the 12 Oct 31 timelines with it: sentence starts right on all 12 (hand-checked against the
voice's pauses), no bad stretch used, no shot slowed under 0.75x, 4 tracks per brand rotating, 5 sound effects each.
Not yet checked by the owner in CapCut.

## 2026-10-24 (batch step) - We write the voice-over; a standing direction goes with every batch

**Why:** most of the hand edit traced back to how batches were set up: Negen's "AI writes it" voice-over said other
words than the on-screen lines and ran to 20 s; Grok blended shots, drew arms with no body, let the product drift and
changed the light; the punchline came over the continuing opening shot.

**New rules (step 3 and 4, `fill_batch.js`, ad-brief-compiler):**
- Voice-over "Write my own" with "Keep speed" (Negen stores it as `fit=pad`): each brief carries a 36-42 word script,
  sentence n saying on-screen Line n, then the CTA. V1-V3 differ only in the first sentence. Negen's estimate: 34
  words = 13.6 s, so the voice ends at about 15-17 s of the 20 s video; the extra footage is spare for replacements.
  The voice also costs less (about $0.007 a video instead of $0.012).
- On-screen line times come from the script at 2.5 words a second; scene rows are written from the sentences, so
  each shot shows what is being said.
- A02 opens the punchline on a hard cut to a contrasting framing (macro, reverse angle or top-down).
- "Direct the video" gets the standing direction in `references/video-direction.md` every time: hard cuts only,
  the product exactly as in its photos, every hand attached to a person the viewer can place, one room, time of day
  and light, no text.
- `fill_batch.js` only says READY when the script, Keep speed and the direction are in place.

**Checked:** filled on a real batch form without starting: `vo=text fit=pad words=34`, `direction ok`, READY=true.
Not yet run as a batch: run one group with these rules first and compare it with an old group in the shot check.

**Kept as it was:** 720p with "product kept closest to the photos" (already the template's setting), 20 s, two
videos per batch, poster as Style + Composition + Lighting.

## 2026-10-24 (later) - Edit plan: on-screen text, voice-over and footage line up; a punchline with impact

**Learned from:** the person's hand edit of Focal Wall V2 in "Triết Agent - 30-10-2026 V2 V3 - rule test", and their
notes: the punchline title came in softly over the opening shot, and the text, the voice and the footage said
different things. Cause: Negen's voice-over writes its own script, so the brief's lines (for example "Not another
box") played over a voice saying "That curve is where it starts".

**New rules:**
- Read each video's voice-over script in Negen and write an edit plan per timeline (`"edit"` in `capcut.json`):
  on-screen lines that echo the voice's words, each shown while it is said, and for each sentence a clean shot of
  what it talks about.
- The punchline (Line 2's animated title) starts with the second sentence on a hard cut to a different shot than
  the opening, with a Slide Blur into it and a 1.15 punch-in zoom (the person's own V2 edit used Slide Blur and a
  1.24 punch-in).
- A long Line 4 shrinks to the house width.
- `build_project.py --replace` rebuilds named timelines inside an existing project and keeps the person's other
  timelines; old ones are backed up in `work/<week>/capcut-backup/`.

**Tested on:** Focal Wall V3, Curved Focal Point V2 and V3, rebuilt inside the rule-test project (the person's
Focal Wall V2 untouched). Not yet reviewed in CapCut.

## 2026-10-24 - Shot check: bad shots are cut and replaced; hands need a body

**Learned from:** the published 30/10 V2/V3 videos (Focal Wall SILDTTRWA085 and Curved Focal Point SINLKISD005),
looked at frame by frame and not changed, plus the hand edits of the Oct 23 test week.
- Focal Wall V2: two hands rise from below the panel to hang it (0-2.5 s) and a hand comes from the bottom edge to
  push it (12.5-14.5 s): arms with no body. The panel also turns tall and into a thick box (9-15 s).
- Focal Wall V3: daylight jumps to evening at about 15-17.5 s.
- The sideboard (a boxy product) keeps its shape; organic products (tree shelf, wall art) drift in close-ups.
- Every video has two shots blended for about 0.5 s at most scene changes.
- The person removes these shots by hand and fills them with footage from the other videos of the same product.

**New rules:**
- Download keeps both videos of a batch; the second is spare footage in `videos/spare/`.
- New step 6b, shot check: `capcut/shot_sheet.py` makes a sheet per video (a frame every 0.5 s); Claude marks every
  bad stretch (arm with no body, product drift, hallucination, blend) in `shots.json`.
- The CapCut build replaces a bad stretch of 1 s or more with clean, unused footage (the video's spare first, at the
  same moment when that is clean, then the group's other videos) and cuts out a shorter one. Timelines of one group
  carry the same `"group"` in `capcut.json`.
- Brief rules (ad-brief-compiler): every hand row says where ACTOR A's body is (person in frame or eye-level POV);
  no hands rising from below to wall height, out of a wall, the product or a window; wall-mounted products are hung
  by ACTOR A seen from behind or the side; one time of day and light in all rows; organic products keep at least
  5 of 8 rows medium or wide.

**Tested on:** dry run of the build on the Oct 23 test week (shot check done on its 11 videos and spares): every
bad stretch was replaced from the spare or a sibling, no missing references. Not yet opened in CapCut.

**Also fixed:** Vietnamese file names (the codified names) crashed the scripts' output on Windows; they now print
in UTF-8 and read ffmpeg's output as UTF-8.

## 2026-10-23 - CapCut timelines cut to the voice-over, with brand music

**Tested on:** the "Tool test Oct" week (`work/2026-10-19 Tool test Oct/`), 6 videos: Spry Tree Bookshelf Reading
Nook V1-V3 and ETW Wave Vanity Spa Bathroom V1-V3. From sign-in to a built CapCut project took about 1 hour.

**What was wrong:** the CapCut build kept Negen's full 20 s video with fixed text times (Lines 1-5 from 0 to 17 s,
CTA 17.1-20 s) and no music. The voice-over stops at about 16-17 s, so every video ended on 3-4 s of silence and
needed a lot of hand re-editing. In CapCut the person:
- cut every timeline to 14-16 s and sped the voice-over up about 1.08x,
- re-timed every text line to the new cut (Line 1 about 1.5-2 s, CTA in the last 1.5 s),
- added music: Spry "Neon Meow's Jazz Club [Bonus]" at 24%, ETW "Soulful Groove" at 100%,
- sped footage 1.2-1.3x on some videos and swapped weak shots for shots from the sibling V1/V2/V3 video.

**New rule (CapCut step, `capcut/build_project.py`):**
- Each timeline ends 1.5 s (`CTA_HOLD`) after the last word of the voice-over, never longer than the video.
- Voice-over pauses of 0.4 s or more are cut to 0.25 s; the voice-over plays at 1.08x (`VO_SPEED`).
- Lines 1-5 are fitted to the speech (the house edit's 0-17 s block shrinks to end with the voice); a change of
  line moves onto a pause in the voice-over when one is within 0.8 s. Line 2's animated title keeps its length.
- The brand's music bed (`brand/brands.json` "music") runs under the whole timeline with a short fade out:
  Spry at 24%, ETW at 100%. A track CapCut has not saved on this computer yet is left out with a NOTE.
- Result on the test videos: 16.0-17.3 s (the one video whose voice runs to the end stays at 20 s).

**Still by hand:** footage speed-ups, swapping weak shots, punch-in zooms, and the final check of each timeline.

**Not yet checked in CapCut:** the new build was only dry-run on the test videos. Check the first timeline of the
next week carefully (music level, text timing, the voice at 1.08x).
