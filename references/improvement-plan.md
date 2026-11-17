# Fast lane improvement plan (from 2026-11-17)

The goal is to bring the fast lane's videos, step by step, closer to the main lane's, without making them simpler.
The look stays: people living with the product in a real room, alongside the product on its own. The Nov 13 wine
holder set is the reference for that look. Explore and iterate groups, the formats and the type system stay too.

What changes is how a week is checked: problems are caught before the owner watches, and fixes are tested before
they reach a week.

## What the Nov 13 week showed

- The first pass was fast: about 2 hours from the first popup to the saved CapCut project.
- Then the owner's review found what our checks had passed:
  - 9 of 12 videos made again (R2);
  - V3 made three times;
  - V8 voiced three times;
  - V7-V9 with text on top of text;
  - a second actor in V9;
  - a gliding table in V7.
- The fixes took most of two days. The plan check (step 7) had passed every one of these.
- The 12 briefs were written in 9 minutes (10:51-11:00); CLAUDE.md budgets 20. Two of the three argument failures
  (V3 "I trace the grain", V8's gift chain) came from that step.
- Every problem was judged by the same session that made it: the scripts, the shot check and the plan check.
- The build changed during the week, three times. Each change fixed one video and broke something in another: the
  word timing made Line 2 run over Line 3, and the crossfade fix dropped real crossfades.

So the time is not lost making videos. It is lost after the owner sees them. The fix is a stronger check before that
point.

## The changes

### 1. A script review that is not the writer (from the next week)

**Problem:** I wrote the scripts and judged them. The chain flaws passed twice.

**Change:**
- Each brief carries its chain (done, Nov 17: `ad-brief-compiler` chain test; CLAUDE.md step 3 and the go-ahead).
- A separate reviewer reads all 12 scripts before the go-ahead. The reviewer is a subagent given only the scripts,
  the product page facts, the format jobs and the chain test, not my reasoning.
- It returns pass, or the broken join for each script. A broken one is rewritten before the popup.
- The briefs get their full 20 minutes while the storyboards run.

**Reference scripts:** two or three main lane scripts the owner picks go in `references/main-lane/`. They are the
model for how an argument moves.

**Measure:** argument fixes asked by the owner after the save. Nov 13: 3 (V3, V8 twice). Target: 0.

### 2. The product drawn right before the video is paid for (verify, then from the next week)

**Problem:** product and people drift caused most remakes:
- the side table turned into a drum or a column;
- the coffee table slab turned live-edge with bark;
- the cast changed between parts.

The shot check finds this only after the batch is done.

**Change:**
- **Verify on the next week's first batch:** Negen makes the PART A/B start pictures (the Image step, about 1 minute)
  before the video parts (about 80 s each). Check whether a batch can be looked at and stopped there. If it can,
  look at every start picture next to the product photo before the parts run. A wrong shape or a wrong person is
  stopped, its row fixed, and the batch run again: one picture lost instead of four parts.
- **Name the outline:** every product gets one outline line, written once from its photo and used in every row
  that shows it (V3 R2 did this: "ONE smooth rounded hardwood slab with a single long tapered arm", and it held).
  Store it in `brand/` per SKU, so the next week reuses it.
- **Keep the people, frame them like the wine holder set:** the person and the product share the frame, and the
  product is whole in it. Close-ups of a sculptural base without a person are the shots that drifted most, so
  they are kept short.

**Measure:** remakes after the owner's review. Nov 13: 9 of 12. Next target: 3 or fewer.

### 2b. Shots chosen by the argument: dynamic, and each one proving its sentence (owner, Nov 17)

**Problem:** the camera rule (skill section 2, from Oct 28) keeps most rows eye-level medium or wide, allows at most
two close details, and bans top-down shots and macros. It was a reaction to the Oct 28 batch, where energetic moves
turned lived-in scenes into hand-led product demos. The result is safe but flat: the rows look alike, and the shot
under a sentence often shows the room instead of what the sentence argues (the edit then hunts the footage for a
match).

The owner wants dynamic shots and camera moves chosen by the script: wide, close, dolly, push, arc, top-down.

**Change:** each sentence's job picks its shot size and camera move. The scene rows are written from that map, and
the edit cuts on it. The lived-in look stays: ACTOR A is in at least 4 of the 8 rows, and hands keep their body
(section 6).

| Sentence job | Shot size | Move | What it proves |
|---|---|---|---|
| Hook | medium on ACTOR A with the product (a problem hook: wide on the before-state) | push-in or a 30-45 degree arc, moving from the first frame | stops the scroll; who and where |
| Tension / before | wide | slow dolly-out, or locked, so the problem reads | the problem, without our product |
| Turn (punchline) | a different size from the shot before (wide to close, or close to a wide hero) | push-in; the edit adds the 1.15 zoom and a hard cut | the product as the answer |
| Reason | close on the part the sentence names: top-down for a top and what sits on it, close on the joint or grain, low angle for height | slow push or slide | the fact itself, on screen |
| Doubt cleared / fit | wide with ACTOR A for scale | dolly or parallax past a foreground object | it fits the room and the person |
| Offer | medium hero | arc around the product with ACTOR A in the room | the piece worth buying |
| CTA | wide hero (B04) | locked-off | the end frame |

**By format:**
- **list:** each reason gets its own size (top-down, close, medium), with a cut on every sentence.
- **ritual:** one slow push per moment.
- **story:** handheld follow of ACTOR A.
- **gift:** a medium on the person, a close on the piece as the gift, then the person using it.
- **turn, myth, after:** keep the wide before-state under the tension.

**Rules that keep it working:**
- The size changes at every cut. No two rows in a row share a size and a move.
- Top-down only over a surface the sentence names.
- A close-up of a sculptural product stays short (2 s or less) and names the outline line (change 2), because
  close-ups drifted most.
- Crash zooms and whip pans stay out.

**Where it lives (done Nov 17):**
- `ad-brief-compiler` section 2 is rewritten with this map, and the standing direction asks for the row's size and
  move.
- Each row starts with "SIZE / MOVE" (for example "CLOSE / slow push-in").
- The map is the "argued" structure, one of six in `capcut/templates/structures.json` (argued, follow, tableau,
  pov, match, montage); each video picks one from its script, and an explore group uses at least two.
- `cut_sheet.py` prints each cut's size next to its sentence, so a cut that does not change size, or a shot that does
  not show its sentence, is seen at the plan check.

**Measure:**
- the owner's 1-5 score on "the shots follow the script";
- remakes caused by close-up drift (watched, because more close-ups is the risk).

### 3. An independent look at every frame before saving (from the next week)

**Problem:** the plan and cut sheets were looked at by the same session that made the cuts. The second actor,
the gliding table and the wrong woman on V8's punchline were all on those sheets.

**Change:**
- After `plan_sheet.py` and `cut_sheet.py`, a reviewer subagent gets the sheets, the product photo, the cast line of
  each video and the step 6b bad list. It returns every frame it would cut.
- Each finding is fixed in `shots.json` and the sheets are run again before the save.
- **The owner's catch list:** `references/owner-catches.md` collects every problem the owner found after a save,
  with the frame. The reviewer is given it each week. The checklist grows from real misses, not guesses.

**Measure:** problems the owner finds after the save, counted per week.

### 4. Tool changes are tested before a week, never during it (now)

**Problem:** three build changes in the middle of the Nov 13 week, each with a side effect.

**Change:**
- During a week, problems are fixed in the week's material only (CLAUDE.md "one route"). A change to a script is
  written down in `log.md` as needed and made after the week.
- Between weeks, the change is made on a branch and tested on the last finished week. Rebuild that week's
  timelines as a dry run, run `plan_sheet.py` and `cut_sheet.py`, and compare with the saved timelines. Text
  times, shots and lengths may change only where the fix meant them to.
- A small script (`capcut/regress.py <week>`) prints that comparison per timeline, so the test is one command.

**Measure:** build bugs found by the owner. Nov 13: 3 (title overlap, Line 3 waiting for its number, footage starved
by false crossfades).

### 5. One consistent set of rules (one pass, owner approves)

**Problem:**
- CLAUDE.md grew from about 1,100 to 5,600 words, and the brief skill from about 1,400 to 6,300.
- Some rules repeat or contradict each other. The skill's gift example was itself wrong for a day.

**Change:**
- One pass that merges repeats, removes contradictions and moves checks that a script can do into code (word count,
  sentence count, offer wording, banned words).
- It removes no rule about the look or the quality bar. It is shown to the owner as a diff before it is used.

**Measure:** fewer words, the same rules, and no rule the owner has to repeat.

### 6. A weekly scorecard against the main lane (from the next week)

At the end of each week, `log.md` gets five numbers:
- hours from the first popup to the saved project;
- remakes after the go-ahead;
- the owner's fixes after the save;
- the owner's score of the week against the main lane, 1-5;
- the one thing that most separates the week from the main lane.

The next week's first change targets that thing. The quality goes up one gap at a time, and the numbers show whether
it does.

## Order

1. Now: change 4 (no mid-week tool changes), already the CLAUDE.md rule; the regression script before the next tool
   change.
2. Done Nov 17: change 2b. The shot map is one of six shot structures picked per script
   (`capcut/templates/structures.json`). It is wired into the skill, the standing direction, `cut_sheet.py`,
   `plan_sheet.py` and the build, and recorded in `references/rule-changes.md`.
3. Next week: changes 1, 3 and 6. They need no new tools, only the reviewer subagents and the scorecard.
4. Next week's first batch: verify change 2 (stop at the start pictures); write the outline lines for that week's SKUs.
5. After the next week: change 5, with the owner's two or three main lane videos as the bar.

## Needed from the owner

- Two or three main lane videos (and their scripts) that are the bar.
- After each week: the 1-5 score and the biggest gap, in one line.
