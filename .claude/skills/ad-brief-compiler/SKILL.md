---
name: ad-brief-compiler
description: Convert an approved Negen product storyboard (8 panels A01-B04 + VO), the product page facts and verified offer facts into paste-ready values for Negen's Section 7 Ad brief (Ad job, Hook, Proof, Offer, Call to action, On-screen text, 8 Scene rows) for a Conversion Creative V3 video batch. Use when a team member pastes a storyboard and product facts and wants the Ad brief fields to copy into Negen.
---

# Ad Brief Compiler (v2)

## Purpose

Fill Negen's Section 7 "Ad brief" so a Conversion Creative V3 batch turns the approved storyboard into a 20-second, 9:16 ad.

Do not generate video. The storyboard gives the product's look and staging; the argument comes from the group's persona, angle, mode and format ("Variant set" and "Formats"). Fix the storyboard only where "Corrections you must make" says.

**The storyboard sets the look; the brief sets the argument.** The owner's best-looking videos (Oct 31 batch) came
straight from the storyboard's panels: a real person living with the product in a fully furnished, lived-in room,
eye-level medium and wide frames, warm low sunlight, layered depth. Each scene row keeps its panel's staging (room,
person, what they do, framing, light) in the panel's own words where they work, and adds the argument (what the
voice says at that moment) and the corrections below. Never turn a lived-in panel into a hand-only product demo.

The person using this skill will copy each field into Negen by hand. Make every field paste-ready, in the exact order and format below.

---

## Inputs to ask for (if missing)

1. The storyboard text from Negen Review: angle line, the 8 panels (A01-A04, B01-B04) with JOB and DIRECT, the continuity note, and the VO.
2. The product page "Details" text (description and variants) from Negen Products.
3. Store / brand (Spryinterior or ET Woodcrafts).

If the product page is missing, ask for it. Never fill product facts from memory.

---

## Corrections you must make to the storyboard

### 1. Hook = a person using the product in the first 2 seconds
A01 shows ACTOR A doing something with the product from frame one, in the lived-in room: sitting down, setting keys
down, lifting a bottle, sliding a book onto a shelf. Their body is in frame (see 6). If the storyboard's A01 is an
empty room, a light sweep, or a macro with no action, rewrite it as such a moment in the same room and light.

For wall-mounted products the hook is ACTOR A seen from behind or the side, arms visible up to the shoulders, never
two hands rising from below the frame.

Avoid hooks that depend on the order of two framings, such as "empty wall, then the product appears" or "macro first, then reveal the whole piece". The video model often plays these in reverse or blends them with a dissolve.

### 2. Camera: moving, but the room stays readable
Every scene row names ONE clear camera move, written first, that a real camera operator would make in that room:
push-in, handheld follow of ACTOR A, dolly or parallax slide past a foreground object, orbit up to 45 degrees,
short crane to eye level. Keep the storyboard panel's move when it is one of these.

- At least 5 of the 8 rows are eye-level medium or wide shots with ACTOR A and the product in the room; at most 2
  close details (a part of the product named, a hand with its body placed).
- Layered depth in medium and wide rows: something in the foreground, the product, the room behind.
- No crash zooms, whip pans, top-down floor shots or extreme macros: they break the lived-in look.
- Never two rows in a row with the same angle and move. Locked-off only on B04.

### 3. Wide products stay inside the frame
For long or wide products (TV stands, consoles, kitchen islands, sideboards, long wall panels), every wide shot must say "whole product inside the central 70% of the frame". The 9:16 crop otherwise cuts the ends and the AI check marks the video down.

### 4. Product truth
- Only use features stated on the product page or clearly visible in the product photos.
- If the storyboard mentions something the page does not support (for example "live edge", "drawers", a hidden interior), remove it or ask.
- Do not show the inside of closed storage unless the product photos show it. Prefer "the item goes behind the panel and the panel closes flush".
- Product photos are often staged with lights the product does not have (lit wine-rack shelves). If the page does not
  sell lights, start every row where the product is in frame with "IMPORTANT: the <product> is completely UNLIT, no
  lights or LEDs." in full, never shortened. The model copies the photo's light otherwise; a short "The rack is
  UNLIT" still gave lit shelves in every End-of-year take (2026-10-28). Set the group's `"unlit": "<product noun>"` in `week.json`; `fill_batch.js` then
  adds the full note to every row by itself.

### 5. Continuity and casting
- ACTOR A is the video's `"cast"` in `week.json` (picked by `brand/pick_cast.py` from `brand/cast.json`: someone
  from the group's target buyers, either relatable, the buyer today, or aspirational, who they want to become). Write
  "ACTOR A (<cast.who>)" in full, in the same words, in every row they appear. Never write in your own person
  instead, and never let the storyboard's person carry over: the three videos of an explore group show three
  different people on purpose; an iterate group shows one person in all three, so only the hook changes. Guests only when the angle needs them (a party); the host casts already describe them.
- Relatable rows show ACTOR A doing the everyday version (keys down after work, a book on a Sunday). Aspirational
  rows show them at ease in the finished home (hosting, a calm morning). Same room, product and argument either way.
- Rows with no person end with "No person."
- Anything placed stays placed; anything removed stays removed; the final frame shows the accumulated state.
- One time of day and one light for all 8 rows, the storyboard's own (usually warm low sun from one side, soft long
  shadows); never day to evening.

### 6. Hands need a body
Videos where an arm appears from nowhere get cut in the edit. Every row with a hand says where the body is:
- **Person in frame:** ACTOR A's shoulder, back or side is visible (over-the-shoulder, from behind, side-on), or
- **Eye-level POV:** the camera is ACTOR A's eyes and the arm reaches forward from the bottom edge to something at
  waist or table height in front of them.

Never: hands rising from below the frame to something at or above eye level (wall art, high shelves, mirrors); a
hand or arm coming out of the wall, the product or a window; two hands with no person in a wide shot; a hand in a
top-down shot of a floor. Close-ups of wall-mounted products have no hand ("No hand.").

Sculptural products (a carved base, a freeform top, a shaped frame) drift in close-ups: with the outline out of frame
the model invents a new shape (Nov 9 console: a thin floating ribbon, two humps). Every close-up row keeps in frame
where the part meets the top and the floor ("the base's curve from where it leaves the floor up to where it meets the
top"); never the base alone, never a part with both ends cut off.

A size or number line plays over a wide of the whole product with a person beside it for scale; the offer and the CTA
over a clean shot of the whole product, the person whole or out of frame, never cut by the frame edge.

Picture, voice and text say the same thing, sentence by sentence (owner, Nov 7: "Ours wobbled every time someone
leaned in" played over three friends smiling around the folding table). Every scene row shows its sentence as an
action the viewer can see, with the feeling the sentence carries:
- A problem sentence shows the problem happening and the people bothered by it: the folding table tips under an
  elbow, a glass slides, ACTOR A grabs it and steadies the table, nobody smiles. Write the action and the expression
  in the row ("frowning", "catches the glass", "presses the table flat with both hands"); the model smiles otherwise.
- A claim or proof sentence shows the thing it names (grain when it says grain, a glass standing flat when it says
  room for drinks), never a generic wide.
- The on-screen line on top of it says the same idea in fewer words, or names the proof on screen; it never
  contradicts the picture.

On-screen lines are written new every week (owner, Nov 7: the overlays kept repeating the last two weeks). Banned
skeletons, because they have run every week: "Give it a ___", "One ___ changed that", "This one ___", "Solid wood / ___"
as Line 3, "Free delivery, made to order" or "Every piece is one of a kind" as Line 5. Each line takes its words from
this ad's own voice-over and persona: Line 1 the persona's own thought or a number, Line 2 the one claim in 2-4 words,
Line 3 a caption of the proof on screen ("Glass stays put"), Line 4 the doubt answered with a number from the page
("32 to 60 in wide"), Line 5 the offer in this ad's words. The plan check prints REPEAT for any 3-word run used in the
last three weeks.

Mirrors, glass and windows in the room (a mirror above a console, a glass door): a reflection of ACTOR A is wanted
when it can be right, and only then. At most one row per video is a mirror moment: ACTOR A stands in front of the
mirror facing it, and the row says "the reflection matches ACTOR A exactly". Every other row with a mirror in frame
says "the mirror shows only the room", with ACTOR A beside it or walking past. (Nov 9 console week: the model drew the
man inside the mirror while he stood beside it in five of six videos; the shot check cuts every wrong reflection, and
the build fills the gap from clean footage.) ACTOR A is the only person in the row unless the brief names a group; no one else walks
through the foreground.

**Simple poses, simple physics.** The video model draws extra feet and broken limbs in tangled poses and gets hinged
things wrong (Oct 28: a third foot on the chair, a cupboard door swinging the wrong way). In every row:
- People stand, walk, or sit upright with both feet flat on the floor. No crossed legs, feet tucked up, curling up,
  lying down or legs over the chair arm.
- One simple action per row: set down, lift, take off a shelf, rest a hand, hand over. No opening doors, lids or
  drawers on camera: show the cupboard or cabinet already open.
- High shelves are reached by a person whose whole body is in frame, never by an arm entering from an edge.

### 7. Organic and sculptural products
Tree shelves, live-edge panels, wall sculptures and other organic shapes drift most in close-ups (a trunk turns into
a pillar, a wide panel turns tall or into a thick box). For these keep at least 5 of the 8 rows medium or wide, name
the part in frame for every close-up ("the trunk where it meets the bench"), and keep the product's orientation.

### 8. A problem line needs a picture of the problem
A contrast argument is fine ("Most consoles are plain and say nothing"). What fails is the execution: on Oct 31 that
line played over our own console, so the viewer read ours as the plain one.
- The scene row for a problem sentence shows the problem: the before-state (a bare entry, bottles crowding the
  counter), preferably with no furniture of our product's kind at all (a stand-in console risks the model drawing
  ours, or a look-alike). Our product is not in that frame.
- The answer sentence opens on a hard cut to our product (A03, the punchline).
- No named competitor and no stand-in that resembles a real brand's product.
- A hook that raises a doubt ("Too beautiful to sit in?") is answered by the next sentence and the footage.

---

## Variant set: one ad set, three videos, one thing tested

A group is one SKU, one angle and one persona: one Meta ad set, as the media buyer builds them. Return three
complete Ad briefs, V1, V2 and V3. The persona is the group's buyer, from the SKU's family in
`brand/personas.json` (code prefix: CST consoles, CFT coffee tables, TBS tree shelves...; VALIDATED before MAPPED);
a SKU with no family gets one written there first, in the same fields, from the product page and the brand's buyers.
The angle is that persona's.

**Why (owner, Nov 10).** The Nov 9 week ran one skeleton in all 12 videos ("Mine was a blank ___. One ___ changed
that. ___, so ___. Free delivery..."), the same edit, and all four groups sold "focal point". Meta reads look-alike
ads as one and delivers fewer of them, and nothing was declared as the thing being tested, so a result could not
say what won. Each group now has a mode, a declared variable and its own shape.

**Mode: explore or iterate.** Chosen per group in step 1 from what the owner says won before (the repo cannot see
Meta results, so it asks):
- **explore** (a new SKU or angle, or nothing proven yet): V1-V3 are three formats (below) for the same persona and
  angle. The question is which kind of argument works at all. They share only the product truth, the offer line and
  the CTA; every sentence and on-screen line is their own. The result says which format won, not why.
- **iterate** (a proven body: a video the owner names as the winner, its `"control"`): V1-V3 are one body, the
  control's format and argument with the group's one declared variable changed, and three hooks on it. Only the hook
  changes between them: a different first moment in A01, on-screen Line 1, the first sentence and the hook type, three
  clearly different ideas (a use moment, a problem, a tactile detail), not rewordings. Sentences 2 to the end and
  Lines 2-5 are the same in V1-V3. The result says which opening sells that body.

**One declared variable per group.** Every group names the one thing it changes from the last test of the same SKU
and angle (its `"control"`), or "first run". Write it in `week.json` as `"variable"`, for example "format", "speaker:
a designer instead of the owner", "opener: close on the piece with a hand on it". Anything in the ad can be the
variable; these are the usual ones:

| Variable | Examples |
|---|---|
| format | one of the formats below; the still made into a film |
| persona | another buyer of the same angle (another ad set) |
| speaker | the owner, a designer, a guest, a first-person voice from 0 s |
| opener | the first frame: product whole, a hand on a part, the before-state, a person arriving |
| proof device | a before/after on one locked camera, a timelapse, a remove-and-return, a scale beside a person |
| proof timing | how early the proof is seen or heard (by 3 s, by 5 s) |
| length and density | about 15 s with 4-5 cards, or longer with more beats |
| home and style | room type, home style (modern, mid-century, casual US home), time of day |
| voice and sound | the voice's gender or tone, the music bed, no music |
| text | card style, text density, Line 1 as a question or a statement |
| offer and proof | the offer line, a price line, a review line (only what `brand/brands.json` and the page give) |
| execution | the same argument in another production look |

Change only the declared variable against the control; keep the rest of the control as it was, so the result reads.
A first run has no control and declares "first run".

**Across the week.** No two groups sell the same angle or run the same argument skeleton; no format more than twice
in 12 videos (an iterate group counts as one use of its format); a SKU does not repeat its last test's angle and
persona with nothing declared as changed. The plan check prints SAME for look-alikes (CLAUDE.md, step 7).

Before the three briefs, print the group line (SKU, angle, persona, mode, variable, control) and a 3-row summary:
Variant | Format | Hook idea | Delivery, so the person can check them. Batch names: "<Date> - <Product> <Angle> V1",
"... V2", "... V3".

## Formats

Every ad uses one format: the shape of its argument and of its edit. An explore group uses three of them, an
iterate group one (the control's, unless format is its variable). Each has its sentence jobs below (the voice-over
follows them one sentence each, in order), and a row in `capcut/templates/formats.json` that tells the CapCut build
on which sentence each on-screen line starts, the ad style code for the sheet, and the edit's rhythm. Write the
format's key into the video's `"format"` in `week.json` and on its timeline in `capcut.json`, with the group's
`"mode"`.

| Key | Format | Sentences, one job each | Line 2 (punchline) on | Ad style | Best for |
|---|---|---|---|---|---|
| turn | Problem to turn | 1 hook, 2 tension (before-state), 3 turn, 4 reason, 5 doubt cleared, 6 offer or scarcity, 7 CTA | 3 | PD | problem-aware buyers |
| story | Owner story | 1 the moment or doubt in first person ("I almost kept my old table."), 2 what I expected, 3 what happened, 4 the detail that won me over, 5 who I'd tell, 6 offer, 7 CTA | 3 | UG | approval and belonging desires |
| list | Three reasons | 1 the promise ("Three things guests notice first."), 2 reason one, 3 reason two, 4 reason three, 5 offer, 6 CTA | 2 | PD | solution-aware, comparing |
| myth | Objection, then truth | 1 the belief said plainly ("Solid wood in a small hall? Too bulky."), 2 what people settle for (before-state), 3 the truth, 4 the proof, 5 the fit answer, 6 offer, 7 CTA | 3 | PD | a strong barrier in the persona |
| after | After first | 1 the finished room ("This used to be my emptiest wall."), 2 the before (before-state), 3 the change, 4 what made the difference, 5 the fit answer, 6 offer, 7 CTA | 3 | BA | unaware buyers, big visual change |
| ritual | A day with it | 1 a morning moment, 2 an evening moment, 3 what it is in my day, 4 the reason, 5 the doubt cleared, 6 offer, 7 CTA | 3 | UG | comfort and enjoyment desires |
| gift | For someone | 1 who it is for ("For the friend with books on every floor."), 2 why it lands for them, 3 the one they would not buy themselves, 4 the reason, 5 the choice (size, finish), 6 offer, 7 CTA | 3 | PD | Nov-Dec, gift buyers |

- Every format keeps the rules of the VO SCRIPT section below (40-46 words, spoken, an argument, page facts only);
  only the jobs and their order change. "list" has 6 sentences, every other format 7.
- The before-state (corrections, 8) belongs to the formats with one: turn, myth and after put it on sentence 2 and
  in A02. Story, list, ritual and gift have no before-state: their A02 shows the persona's situation with the
  product, and `"before"` in the shot check stays `[]` unless a stretch plays under a problem sentence.
- "after" opens on the finished room with the product, so its edit plan sets `"line1_end": "s2"`.
- The scene rows follow the format's sentences in order (SCENES below): each row shows what its sentence says.
- A new format is added in both places at once: a row here and a row in `capcut/templates/formats.json`.

---

## Output: paste in this order

### AD JOB
One sentence: what the viewer should believe by the end. Customer-facing, not "make an ad for...".

### HOOK (first 2 s)
One or two sentences describing ACTOR A's action with the product, the room, and the camera move in the first 2 seconds.

### PROOF
Claim, then what the viewer actually sees. One or two sentences. Only verified features.

### OFFER
The brand's store-wide offer from `brand/brands.json` (`offer`, set by the owner), plus anything the product page
states (for example "Custom sizing available on request."). With neither, write: LEAVE BLANK. Never invent
discounts, shipping, warranty, returns or deadlines. The scarcity line (`scarcity` in `brands.json`) never carries a
number or a deadline.

### CALL TO ACTION
Short. Spry: "Shop the <product>" (for example "Shop the shelf"). ET Woodcrafts: "Explore the Collection".

### VO SCRIPT (Write my own): an argument, not a feature list
We write the voice-over; Negen's "AI writes it" writes its own words, which then do not match the on-screen text.
The script is the ad's argument. A script whose middle is "An oval top on an S-curve base. Keys down, palm on the
grain. Six widths." lists features and does not sell (look test, 2026-10-28). The owner's converting scripts (the
creative team's Oct 31 copy) move from a tension to a turn to a reason, then clear a doubt. The table below is the
"turn" format; every format (above) has its own jobs, one sentence each, under the same rules:

| # | Job | What it says | Example (curved console) |
|---|---|---|---|
| 1 | Hook | the stake, a call-out or a doubt, in the viewer's world | "Your entry is the first thing guests see." |
| 2 | Tension | the before-state or the doubt made concrete: what is wrong now, in the owner's own words | "Mine was a bare wall they walked straight past." |
| 3 | Turn (punchline) | our product as the answer, short | "Then one curve gave it something to say." |
| 4 | Reason | the one product fact that makes the turn true, said with "so" or "because" | "An oval top over a single S-curve, so guests see a shape." |
| 5 | Doubt cleared | the question a buyer has before buying (fit, size, use, care), answered with a page fact | "Six widths, so it fits the wall you have." |
| 6 | Offer or scarcity | the brand's verified offer and scarcity line (`brand/brands.json`), or a proof line if the brand has none | "Free delivery, made to order in limited runs." |
| 7 | Call to action | the CTA | "Choose your width at Spry." |

- 40-46 words, about 16-18 s at 2.5 words a second (the batch uses "Keep speed"; the CapCut build speeds the voice to
  1.08x and shortens its pauses, about 15-16 s).
- No sentence only names a feature: a feature is the reason for the turn (4) or the answer to a doubt (5).
- Register: an owner talking to a friend. First person in the tension and the turn ("Mine was…", "Then…") reads as
  lived proof; second person in the hook.
- The hook may itself be the problem ("Bottles crowding your counter again?"); then sentence 2 makes it concrete
  ("Every bottle you own, fighting for the same corner.").
- Spoken English, no claim the product page does not support, no offer or scarcity that `brand/brands.json` does not
  list.
- A full stop, "?" or "!" ends a sentence and nothing else does; the CapCut build finds the sentences by them and by
  the voice's pauses, and times each on-screen line to its sentence. Commas are fine. Exactly as many as the format
  has (7, or 6 for "list"): a doubt asked and answered in one slot takes a comma ("Too precious, it's my everyday
  seat."), not a "?".
- In a format with a before-state, that sentence plays over a picture of the problem without our product (see 8):
  its scene row is A02.
- First person ("Mine was...") is the voice of story, ritual and the tension of turn, myth and after; it is not the
  voice of every ad. A list or gift ad speaks to the viewer.

### ON-SCREEN TEXT
Exactly 5 lines, each the key words of its VO sentences, each with From and To in seconds:
Line 1 = the hook (on screen until Line 2 starts), Line 2 = the punchline, Lines 3-5 = the next sentences, on the
sentences the format's row in `capcut/templates/formats.json` names. For "turn": Line 1 through the tension (heard,
not written), Line 2 the turn, Line 3 the reason, Line 4 the doubt cleared, Line 5 the offer or scarcity; for "list":
Line 2-4 the three reasons, Line 5 the offer. Time them from the VO at
about 2.5 words a second from 0 s (Negen's own estimate). The last line must end by 17 s, because Negen adds the CTA
end card from 17.1 s.

Each line 2-6 words, buyer-facing, no generic luxury words, no claims the product page does not support.

### SCENES
8 rows. For each row give: Shot, Camera direction, Job, Seconds.

- Shot: A01, A02, A03, A04, B01, B02, B03, B04.
- Job: choose only from Negen's dropdown: Hook, Why it matters, Detail, Bridge, Proof, In use, Payoff, End frame.
  Default mapping: A01 Hook, A02 Why it matters, A03 Detail, A04 Bridge, B01 Proof, B02 In use, B03 Payoff, B04 End frame.
- Seconds: default 2, 3, 3, 2, 3, 2, 3, 2 (total 20). The total must be exactly 20.
- Camera direction: one or two sentences, under about 200 characters. Start with the camera move. Then what is in frame: the room, ACTOR A and what they do with the product (body placed), or "No person." if none.
- A04 ends mid-action; B01 continues the same action from the same state.
- Each row shows what the VO is saying at that moment (the shelves when it says "open shelves"); write the rows
  from the VO sentences, not the other way round. For 7 sentences: A01 sentence 1, A02 sentence 2, A03 sentence 3
  (the punchline), A04 + B01 sentence 4, B02 sentence 5, B03 sentence 6 (the product whole, in use), B04 end frame;
  for "list": A01 promise, A02 reason one (the punchline), A03 + A04 reason two, B01 + B02 reason three, B03 offer,
  B04 end frame. The Job dropdown follows what each row now does (a reason row is Proof or Detail).
- Camera and pacing follow the format's rhythm (`"pace"` in `capcut/templates/formats.json`): list cuts hard on
  every sentence, ritual takes one slow move per row, story is handheld.
- In a format with a before-state, A02 is the tension: a hard cut to the before-state in another part of the home (a bare hallway wall, bottles
  crowding a counter), and the row says "no <product>, no furniture against this wall" so the model does not draw
  ours or a look-alike. It is never a stand-in that resembles our product.
- A03 carries the punchline (Line 2): a hard cut back to our product in a framing different from A01 (reverse
  angle, wider, or a named part), never a continuation of A01's shot.

Format each row like this so it can be pasted cell by cell:

```
A01 | Hook | 2 | <camera direction>
A02 | Why it matters | 3 | <camera direction>
...
B04 | End frame | 2 | <camera direction>
```

### PASTE CHECK (for the person, not for Negen)
- Seconds add up to 20: YES/NO
- Last on-screen line ends by 17 s: YES/NO
- Offer is verified or blank: YES/NO
- Every row starts with a camera move, only B04 locked-off: YES/NO
- At least 5 rows are eye-level medium or wide with ACTOR A in the lived-in room; at most 2 close details: YES/NO
- Wide product kept inside the central 70%: YES/NO/N/A
- Every row with a hand says where ACTOR A's body is; no hands from below to wall height: YES/NO
- Simple poses only: standing, walking, sitting upright with both feet on the floor; nothing opened on camera: YES/NO
- One time of day and light in all rows: YES/NO
- VO is 40-46 words in the format's sentences (7, or 6 for list), one job each, in the format's order: YES/NO
- The group's mode holds: explore = three formats sharing no sentence or line but the offer and CTA; iterate = one body (the control plus the declared variable) and three different hooks: YES/NO
- No sentence only names a feature (each feature is a reason or an answer): YES/NO
- A02 shows the tension's before-state with no product of our kind in it: YES/NO
- A03 opens on a hard cut back to our product in a different framing (the punchline): YES/NO
- Product with staged lights in its photos but none on the page: the UNLIT note leads every row it is in: YES/NO/N/A

---

## Reminders for the Negen batch (repeat these at the end of every answer)

- Skill: Conversion Creative V3. Shots: PART A and PART B. Format 9:16. Length 20 s. Continuous, Cut.
- References: pick the storyboard poster from Pick from media > Generated. Tick Style, Composition and Lighting, and "Also send this image to the image model" (the start pictures then see the
  storyboard's look, not only a summary of it). Do NOT tick Camera or Everything (they make the camera static).
- Voice-over: "Write my own" with the VO SCRIPT, the video's `"voice"` in `week.json` (pick_cast.py matches it to the person on screen), Advanced >
  Fit to the video length: "Keep speed".
- Direct the video: the standing direction in references/video-direction.md, as-is.
- Brand: SpryInterior for Spry products, ET Woodcrafts for ETW products.
- Batch name: "<Date> - <Product> <Angle> V1|V2|V3". No personal or tool names.
- Two videos come out per batch. Keep the one with the higher AI score and product match; the PART A video is usually but not always better.
