# Rule changes

Changes to how the fast lane works, newest first: what changed, why, and what it was tested on.

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
