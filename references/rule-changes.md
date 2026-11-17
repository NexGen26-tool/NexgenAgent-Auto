# Rule changes

Changes to how the fast lane works, newest first: what changed, why, and what it was tested on.

## 2026-11-17 (owner) - Shot structures fit Negen's own skill

**Why:** the owner asked whether Negen's skill needs changing so the shot rules are built in. Read on Nov 17,
Negen's Conversion Creative V3 skill (the one every video batch runs) already asks for what the shot rules want:
- each 10 s part is an edited sequence of about three shot states with at least two real cuts (hard cut,
  cut-on-action, match cut, wide to detail); a part that is one continuous camera move is rejected;
- the first 1-2 s show a visible event, never a static beauty shot, a slow decorative push-in or an unchanged
  product orbit.

Our "SIZE / MOVE:" rows reach it as written. The skill is shared by the team, so it is left as it is. Two of our
structures clashed with it.

**New rule (`capcut/templates/structures.json`, `ad-brief-compiler` section 2):**
- **follow** is now "Follow, cut on action": one lived moment, handheld, every cut continuing the movement before
  it, about three shots a part, never one take.
- **tableau** opens on an event (ACTOR A sets something down or steps into the frame); the calm composed frames come
  after the hook.
- **The hook row of every structure** names what ACTOR A does in the first second (argued, match and montage
  included).
- **Size checks:** follow and tableau now change size at every cut. match does not, because its before and after
  share one framing on purpose.
- **PASTE CHECK:** a new line says A01 names a visible event and no row is one continuous take.

## 2026-11-17 (owner) - Shot structures, picked per script

**Why:** the owner, on the shot map below: "consider this as one of the structure (or format) of the ad creative. We
need different kind of structure and format across the test, depending on the script and the argument of that
specific one."

**New rule:**
- **`capcut/templates/structures.json`:** six shot structures, each with its 8 scene rows, edit pace, punchline zoom,
  transition and the risk to write against:
  - argued: the shot map below, one per format;
  - follow: a handheld follow, cut on action;
  - tableau: still-life tableaux;
  - pov: first-person;
  - match: before/after match cuts;
  - montage: a detail montage.
- **`ad-brief-compiler` section 2:** each video's structure is picked from what its script argues and written as
  `"structure"` in `week.json` and `capcut.json`. An explore group uses at least two; an iterate group keeps the
  control's unless structure is the variable.
- **`formats.json`:** the argued maps moved from here to `structures.json`. The format is the argument; the structure
  is the camera and the edit.
- **CLAUDE.md:** steps 1, 3, the go-ahead table and step 7 carry the structure.
- **The build:** a structure's `"transitions"` overrides the format's (follow and tableau have no Slide Blur).
- **`plan_sheet.py`:** prints SAME when an explore group films all its videos in one structure, and CHECK for an
  unknown structure.
- **`cut_sheet.py`:** prints SAME SIZE only for structures that change size at every cut.

## 2026-11-17 (owner) - Shots chosen by the argument: the shot map

**Why:** the owner wants dynamic shots tied to the script: "dynamic and script + argument aligned scenes and shot
decisions. Wide, close, camera movements like dolly, pushes, arc, top down". The Oct 28 rule had several limits:
- most rows eye-level medium or wide;
- at most two close details;
- no top-down shots.

It kept the lived-in look after the hand-led demos of Oct 28, but the rows looked alike, and the shot under a
sentence often showed the room instead of what the sentence argued.

**New rule:**
- **`ad-brief-compiler` section 2 is now the shot map.** Each sentence's job picks its size and move:
  - hook: a moving MEDIUM on ACTOR A with the product (a problem hook: a WIDE on the before-state);
  - tension: a WIDE dolly-out;
  - punchline: a hard cut to a new size;
  - reason: a CLOSE, TOP-DOWN or LOW on the part named;
  - fit: a WIDE dolly or parallax with ACTOR A;
  - offer: a MEDIUM arc;
  - end frame: a locked-off WIDE.
- **Row format:** every row starts with "SIZE / MOVE:".
- **Limits:**
  - the size changes at every row;
  - ACTOR A is in at least 4 rows;
  - top-down only over a surface the sentence names;
  - close-ups keep the outline in frame;
  - no crash zooms or whip pans.
- **Sculptural products** (section 7): at most 3 close or top-down rows, each naming where the part meets the rest
  (was: at least 5 medium or wide).
- **`capcut/templates/formats.json`:** each format has its map (`"shots"`, rows A01-B04 as [size, move, job]).
- **`references/video-direction.md`:** "mostly eye-level medium and wide shots" is replaced by "each shot takes the
  size and camera move its scene row names and moves from its first frame".
- **`capcut/cut_sheet.py`:** each cut's row shows its scene row and size, and SAME SIZE is printed where two cuts in
  a row repeat a size.
- **`references/storyboard-camera-rule.md`** is updated with the history.

**Watch:** close-ups drift most on sculptural products, so the owner's remake count on close-up drift is tracked
(`references/improvement-plan.md`, change 2b).

## 2026-11-17 (owner, the 13/11 set, Within Reach V2) - Every script passes the chain test before the go-ahead

**Why:** three scripts of one week broke their own argument (V3 "I trace the grain", V8 twice). V8's second script
still glued two ideas with "so" ("She'd never buy a side table for herself. So it's the gift she'll use every single
night": not buying it herself is a reason for the giver to act, not a reason she will use it), spoke about the woman
instead of to the giver who watches, filled a slot with a picture ("Every night, same chair, same book"), and opened
on a problem (no place for her tea) over footage where the table already stands beside her. The owner: do not make
the same coherence mistake in future batches.

**New rule:**
- `ad-brief-compiler` (VO SCRIPT): the chain test on every script. Join each sentence to the next with the word that
  really connects them and read the joins; a false or stretched join, a picture-only or feature-only sentence, or a
  problem said over footage of the product already solving it is rewritten. The joined chain is written under the
  script in `briefs.md` and as `"chain"` in the brief.
- `ad-brief-compiler` (Formats, "gift"): sentence jobs rewritten to speak to the giver: 1 the person they picture,
  2 why that person would never buy it, 3 so you give it (punchline), 4 what it changes for them every day. The
  example that wrongly passed ("...so it's the gift she'll use every single night") is now the failure example.
- CLAUDE.md step 3 and the go-ahead: each brief passes the chain test, and the go-ahead table shows each video's chain
  in one line, so the owner sees the argument before any spend.
- V8 re-voiced: "Know someone who reads in the same chair every night? She'd never buy a side table just for herself.
  So be the one who gives it. Now her tea sits within reach. Four sizes, four finishes. Free shipping, handcrafted in
  small batches. Explore the collection." (62 credits, about $0.010).

## 2026-11-17 (owner) - The built-in browser is the only browser

**Why:** CLAUDE.md allowed "the built-in browser, or Claude in Chrome". With two Chrome browsers connected, the
session stopped to ask which Chrome to use before opening Negen, a stop the route does not have.

**New rule (CLAUDE.md, "Tools you use"):** every page of the week (Negen, the tracking sheet) is driven in the Claude
desktop app's built-in browser (the browser pane) only, never in Claude in Chrome. `/fastlane` already opens Negen
there; the person signs in to Negen in that pane once.

## 2026-11-17 (owner, the 13/11 set, V7-V9) - One line on screen at a time; a gift ad's steps follow; one actor; false fades

**Why:** V7-V9 text "all messed up": Line 2 (the animated title) has a fixed 3.3 s from the house edit, and with each
line now on its own words Line 3 came in while it was still up; the type styles put both in one place, so "1" sat on
"2" and "It first" on "Blocks joined". The payoff kept the house edit's capital mid-sentence ("Your cup has A home").
V8's gift argument broke: no place for tea, then "they'd never buy this for themselves", then "because the grain wraps
every twist". V7's hook showed the table gliding along the sofa. V9 cut to its spare, played by another man. And the
shot sheets had marked slow push-ins on end shots as crossfades, which starved V8 of footage (an end shot frozen at
0.08x).

**What changed:**
- `capcut/build_project.py` trim_title: Line 2's title clip (and its inner draft) ends 0.05 s before Line 3 comes in;
  TEXT-OVERLAP is printed for any two lines on screen together (Line 3's halves excepted).
- `capcut/typeset.py` in_sentence: in the type styles the payoff keeps the sentence's case ("one for herself"); "I",
  acronyms and store names keep their capitals. The house look keeps the capital.
- `ad-brief-compiler` (Formats, "gift"): each step answers the one before: the need, why they won't buy it themselves,
  so why this is the right gift; a product feature is not a reason to give.
- Shot check: a run of FADE labels over near-identical frames (a slow push-in) is not a crossfade: measure the frame
  change (a crossfade is a burst; a push-in a steady trickle) and correct `"fades"` by hand. A global fix in
  `shot_sheet.py` was tried and dropped: it also lost real crossfades.

**Applied to:** V7 (hook now the man setting his phone down, the table still), V8 (re-voiced: "For the reader with no
place to set her tea. Every night, same chair, same book. She'd never buy a side table for herself. So it's the gift
she'll use every single night. ..."), V9 (one man), all three rebuilt with --replace.

## 2026-11-17 (owner, the 13/11 set, V3) - A list's reasons pass the "because" test; the product named by its outline

**Why:** V3's list "Three reasons my mornings slowed down" had "I trace the grain while it cools" as reason 2: a
sensory detail, not a reason the morning slowed. And V3's coffee table matched the photo for 2 s, then turned into a
live-edge slab with a pale rim, bark, knot holes and cracks, then lobed, then long on two blocks: the rows named it
"one freeform hardwood slab top with thick natural edges", category words that let the model draw a generic slab.

**What changed:**
- `ad-brief-compiler` (Formats, "list"): each reason passes "<promise> because <reason>" and is a change in what the
  buyer does, caused by the product, wanted by the persona, with a shot that shows it.
- `ad-brief-compiler` 9: the product's name in the rows copies the photo's outline (silhouette, parts, edge, base, and
  what it is not), never only category words ("live-edge", "natural edge", "organic"); repeated in close-ups.
- `capcut/build_project.py` key_onsets and `capcut/typeset.py`: in a numbered style (list) Line 3's reason comes with its
  number, not with its second half (the "2" stood alone for 1.2 s), and its two halves sit on two lines.

**Applied to:** V3 of the 13/11 set, made again in Negen ("Nov17 - ... V3 R2") with the script "I sit down with my
coffee instead of gulping it / There's room for breakfast, a book, a candle / And that grain beats scrolling my phone"
and rows that name the slab's outline.

## 2026-11-16 (owner, the 13/11 set) - A type system, text on its words, the product planted, real props, the store's name

**Why:** the owner on the 13/11 set: the text overlays "follow too strictly with my very first example. Every video use
the same color, font, positioning"; text "tends to appear way before the scripts say anything related"; a list ad
whose hook (three reasons) got no payoff, the body listing features; a myth hook ("Big bookcases swallow small rooms")
over our own bookcase; blank white books; a bookcase against the wall in one shot and mid-room in the next; a side
table that glided and one whose shape changed between hook and body; three different women in one video; cloned
wine bottles; a wall piece whose shape drifted; "at Spry" (the store is Spry Interior, spryinterior.com); "code FS"
on screen (free shipping applies to every order, no code).

**What changed:**
- Type system (`references/typography.md`, `capcut/templates/type_styles.json`, `capcut/typeset.py`): five styles
  picked by the ad's format (statement for turn/myth, editorial for story/ritual, counter for list, keepsake for gift,
  contrast for after), each with its own face pairing, size hierarchy, colour and one emphasis, placement and soft
  shadow; `"type"` on a timeline overrides it, `"type": "house"` keeps the first look. Rules: two faces at most, one
  accent per line, safe area, words from the voice.
- Text on its words (`capcut/build_project.py` key_onsets, `capcut/vo_align.ps1`): each line comes up 0.1 s before the
  voice says its first key word, found with Windows' own speech recogniser on the voice-over (no install; a letter
  estimate elsewhere). Cause found: lines were placed at the start of their sentence, and the words they carry come
  later in it. TEXT-VOICE is printed for a line whose words the voice never says in its sentence.
- Briefs (`ad-brief-compiler` 1, 8, 9 and Formats; `references/video-direction.md`): a sentence that states a problem
  or a belief against the product never plays over our product, the hook included (A01 shows the problem); the
  product stays planted in one place with one shape in every row; books, bottles and other repeated props are real
  and varied; a list's three reasons each answer its promise in the buyer's experience.
- Edit: Negen starts PART A from the product picture, so a problem hook can never be shot product-free; the edit plan
  plays a problem hook (turn, myth) over the before-state footage (the video's and its spare's A02, or another
  variant's before-state shot with no person), never over the opening shot.
- Brand and offer (`brand/brands.json`, `ad-brief-compiler` OFFER and CTA): `name` is said and written in full
  ("Spry Interior", never "Spry" or spry.com); `offer.on_screen` ("Free shipping on every order") is what the ad shows;
  `offer.sheet_code` (FS) is only for the sheet and the video name, never shown.
- Shot check (bad list): a product that slides, glides or moves between shots, a wall piece that leaves its wall, a
  shape change between shots of one video, cloned props (identical blank books, identical bottles), more than one
  person playing ACTOR A. Written in `capcut/shot_sheet.py`'s check list and in CLAUDE.md 6b.
- CLAUDE.md 7 (on the person's word, Nov 17): the type system and the offer/name rule after the line parts, text on
  its words under `"times"`, and the problem hook over before-state footage (`"problem_from": "s1"`) under `"cuts"`.

**Applied to:** the 13/11 set, V3-V12 (V1, V2 already exported, left alone): V4-V12 made again in Negen ("R2"
batches), V3 re-voiced with a list that pays its promise, every timeline rebuilt with the type system and the new
timing.

## 2026-11-16 (owner) - The product photo heads every shot sheet; persona sync needs a path

**Why:** product drift was caught by the owner's eye in four reviews, after Negen's own product match had scored the
drifted clips 8.5-9; the shot sheet had no product photo on it to judge against.
`brand/sync_personas.py` defaulted to a path on one member's computer and failed everywhere else.

**What changed:**
- `capcut/shot_sheet.py` (step 6b): each sheet is headed by the week's product photo for that video's SKU, from
  `work/<week>/product-photos/` (else `work/product-photos/`), as `cut_sheet.py` already does. No photo: the sheet is
  made as before, and the run says "(no product photo)".
- `brand/sync_personas.py`: no default source; give the registry path as the argument or in `NEXGEN_PERSONAS_SRC`,
  else it stops with the usage line. Bracketed tracking notes in the registry are no longer copied into the pack.
- `brand/personas.json`, `brand/cast.json`: source notes that pointed at files outside this repo are removed; the
  persona content is unchanged.

**Tested on:** a copy of the Nov 9 week (24 videos and spares, 4 product photos): every sheet headed by its SKU's
photo.

## 2026-11-10 (owner) - The products are picked, not asked: the sheet's assignment first, then what sells on Meta

**Why:** the owner: "nên có 1 rule để pick sản phẩm: check xem có được assign trên sheet chưa -> nếu chưa thì tự pick
sản phẩm. Pick dựa trên data đã work của SKU đó, với lại sản phẩm nào đã work, đang bán được" and, on the data:
"lấy từ Meta. Dựa trên những gì view được và tính được thôi. Generic là được rồi."

**What changed:**
- CLAUDE.md step 1a (new): read the team's tracking sheet ("Source Video chạy Ads v2", each brand's `assign_sheet` in
  `brand/brands.json`) and Meta (the Meta Ads connector, each brand's `meta_ad_account`, ads of the last 90 days), then
  `python brand/pick_products.py work/<week>`. The step-0 popup no longer asks which products.
- `negen/read_sheet.js` (new): reads one tab of the sheet from the open page with no sign-in. The sheet is shared for
  viewing but draws its cells on a canvas and blocks copy, so the routine reads the page's own sheet model
  (`window.spread`). A tab loads when it is clicked.
- `brand/pick_products.py` (new): rows of this month assigned to the person with an empty "Trạng thái video" are their
  products; otherwise each store's SKUs ranked by Meta purchases, then purchase value per dollar, from the SKU in the
  codified ad names, skipping SKUs another person holds an open row for this month and SKUs this lane made in the last
  14 days. A SKU whose best ad is this person's own video goes iterate on it, the rest explore.
- The plan popup (step 1) shows the picked products with why each was picked and lets the person swap one.

**Tested on:** the live sheet (Spry 366 and ETW 330 rows for Oct-Nov; "Triết Agent" is this lane's Assigned name) and
a sample of last-90-day Meta ads: Spry picked SILDTCSC009 (56 purchases, 6.6x), SILDTCS012, SINLCS042, SINLSATB179,
skipping four SKUs held by others this month and SINLSACS108 (made by this lane on Nov 9). Not yet in a real week.

## 2026-11-10 (owner) - One ad set, one declared variable: explore with three formats, iterate with three hooks

**Why:** the owner: "the argument and editing has been the same for the past batch... Meta Ads hates same ads, we
need to change angle, format or variables to target different audiences with different angles." The Nov 9 week ran
one skeleton in all 12 videos ("Mine was a blank ___. One ___ changed that. ___, so ___. Free delivery..."), one edit,
and all four groups sold "focal point"; nothing was declared as the thing being tested. The media buyer builds one ad
set per angle and persona, so a group stays one SKU + angle + persona. The owner then: "Be dynamic. Three hooks when
its best to do so, and 3 formats when its best to do so."

**Principle (distilled from the team's creative-testing practice, now this repo's own rule):** every test changes
one declared variable from a control and records it, so a result can say what won; the three ads of a test share one
body when the question is the opening, and differ in format when the question is the argument itself.

**What changed:**
- `ad-brief-compiler` "Variant set": a group is one SKU, angle and persona (one ad set) with a `"mode"`: **explore**
  (nothing proven: three formats, sharing only product truth, offer and CTA) or **iterate** (the owner names a
  winning `"control"`: its body with one changed variable, three hooks). Every group declares its `"variable"` (a
  table of the usual ones: format, persona, speaker, opener, proof device, proof timing, length and density, home and
  style, voice and sound, text, offer and proof, execution; anything else may be one) or "first run". Across the
  week no two groups sell one angle or one skeleton, and no format runs more than twice.
- `ad-brief-compiler` "Formats" (new): seven argument shapes (turn, story, list, myth, after, ritual, gift), each with
  its sentence jobs, punchline sentence, ad style and edit rhythm. The old 7-sentence argument is "turn".
- `capcut/templates/formats.json` (new): per format the sentence each on-screen line starts on, the ad style, the
  before-state, pace, punch zoom and transitions. `build_project.py`, `plan_sheet.py` and `cut_sheet.py` time the
  lines from a timeline's `"format"` (an edit plan's `"lines"` overrides it); without one the old 7/6-sentence
  default stays, so older weeks rebuild as before.
- `plan_sheet.py` prints SAME for look-alikes by mode: between groups and inside an explore group, 4 shared
  voice-over words before the offer or 3 shared words in Lines 1-4, or one format twice in an explore group; inside an
  iterate group, a shared hook sentence or Line 1; any format run more than twice in the week. CHECK for a timeline
  with no known `"format"` or `"mode"`.
- CLAUDE.md step 1: the plan popup asks per product which earlier video won ("Chưa có (explore)" first); `week.json`
  groups carry `"mode"`, `"variable"`, `"control"`, videos `"format"`; `capcut.json` timelines `"format"`, `"mode"`
  and `"group": "<SKU>"`. `references/naming.md`: the ad style follows the format; `log.md` adds mode, variable,
  control and format. `brand/pick_cast.py` reads a video's persona when one is set, else the group's.

**Repo rule (owner, Nov 10):** everything a week needs is in this repo. A principle learned elsewhere is written in
here first (this log, a skill, a script) and only then used, so anyone who installs the repo gets the same quality.

**Next, not done:** study how Negen's own skills (Product Storyboard Reference + VO, Conversion Creative V3) read and
follow our briefs: compare a few weeks of brief fields with what came out, then tune those skills in Negen.

**Tested on:** the build's timing on sample 7- and 6-sentence scripts with and without a format (old default
unchanged, "list" puts the punchline on sentence 2, a format that does not fit its script stops with a message); a
dry run of the Nov 9 week's 12 timelines (same sentence starts and punchlines as before); the look-alike check on the
Nov 9 week (flags the shared skeleton between groups and "turn" four times) and on a clean explore group (passes).
Not yet on a real week.

## 2026-11-07 (owner, this week's V3s) - No jump cuts, no flashes, the before-state only under the problem, true scale

**Why:** the owner on three V3 timelines: console V3 "cut so bad" (12 shots in 15 s, near-identical wides back to
back, a before-state hallway under the proof sentence); coffee table V3's before-state drew a toy-sized woman next to
a huge sofa under "This one piece pulls the room together"; lamp V3 opened with four cuts of the same woman looking
up and down, the "blank wall" sentence over the lit lamp.

**What changed:**
- `capcut/build_project.py`: two shots that look alike at the cut (a jump cut) or a shot under 0.8 s (a flash) merge
  into the shot before (a locked-off shot may hold long); more than 10 shots prints CHOPPY (regenerate or accept).
  The shot check marks each video's clean before-state in `"before"` in shots.json: only those stretches may play
  under the tension sentence, they never play elsewhere, fills never patch them or bring them into other sentences,
  and a tension shot from elsewhere prints NOT A BEFORE-STATE. A cut may crop (`{"zoom", "cx", "cy"}`) to take a
  clean part of a frame (coffee V3: the empty sofa without the toy-sized woman). `"line1_end": "s2"` ends Line 1
  when the before-state starts, so a product hook never stands over the room without the product. `--only` rebuilds
  just the named timelines and leaves hand edits on the others.
- Shot check (CLAUDE.md 6b): scale drift (a person or the product at the wrong size against the room) and people
  drift (the people change between parts of one video) are bad; `"before"` is marked for every video.

## 2026-11-07 (owner, this week's console) - Close-ups keep the outline; size and offer lines over the whole product

**Why:** the owner caught two console V2 frames: "Five widths fit your wall" over a close-up where the carved base had
become a thin floating ribbon, and "Free delivery, made to order" over a base drawn as two humps with the man cut in
half by the frame edge. The shot check passed both: the close-ups were judged without the product photo beside them.

**What changed:** the standing direction and the briefs keep where a part meets the top and the floor in every
close-up; size lines play over a wide of the whole product with a person for scale, offer and CTA over a clean whole
product; the shot check names the drift (thin ribbon, humps, a part that no longer meets top and floor) and a person
cut in half; `cut_sheet.py` puts the product photo at the top of every sheet so each row is judged against it.

## 2026-11-07 (pilot feedback) - Picture, voice and text match; on-screen lines written new

**Why:** the owner on the conversion pilot: the voice-over said "Ours wobbled every time someone leaned in" over
three friends smiling around the folding table, and the on-screen lines kept repeating the last two weeks ("Give it
a ___", "One ___ changed that", "Free delivery, made to order").

**What changed:** the ad-brief-compiler writes every row as the visible action of its sentence, with its feeling
(a problem row: the problem happens, nobody smiles); the standing direction says so for every batch; the shot check
adds "mismatch"; `cut_sheet.py` prints the sentence beside each cut; on-screen lines have banned skeletons and new
jobs (persona thought, claim, proof caption, number, offer), and `plan_sheet.py` prints REPEAT for any 3-word run
used in the last three weeks.

## 2026-11-07 - No impossible reflections, no passers-by; the build fills short shots itself

**Why:** the owner caught a frame in console V1 where a second person's leg walks through the foreground and the
mirror shows the man who stands beside it. The shot check had no rule for either; five of the six console videos had a
person drawn inside the mirror. The owner also wants the lane agent-to-agent with as few hand passes as possible.

**What changed:**
- Prevention: `references/video-direction.md` (every batch) says ACTOR A is the only person and nobody walks through
  the foreground. A reflection is wanted only when it can be right (the owner: show it if it does not drift, else
  not): one mirror-moment row at most, ACTOR A facing the mirror with a matching reflection; every other row with a
  mirror says it shows only the room. The shot check cuts any reflection that is wrong.
- Shot check (CLAUDE.md 6b): two new bad kinds, an impossible reflection and someone else in the shot (a passer-by,
  a stray leg or arm); a hand, arm or sleeve counts as the video's person in `"person"`.
- `capcut/build_project.py`: a shot that runs out of clean footage gets the rest of its sentence filled with clean
  footage of the same scene (`fill_short`: own video and spare first, then the group's other videos outside their
  person, the before-state only from itself, footage not used yet in the timeline); a flash under 0.3 s is dropped; a
  planned shot that would show another variant's person is replaced. This replaces the hand split ("split the
  sentence into two shots"). `plan_sheet.py` and `cut_sheet.py` show the same pieces.

**Tested on:** the Nov 9 week: mirror and leg stretches marked in five console clips, the three console timelines
re-planned by the build, every cut checked frame by frame (`cut_sheet.py`), 12 timelines rebuilt.

## 2026-11-06 - Cuts land after Negen's crossfade has finished

**Why:** the owner saw cuts in the Nov 9 week's edits where the next shot starts while Negen's own fade between two
scenes is still on screen (a see-through person or lamp over the room). Negen's scene changes are crossfades of about
0.8-1.0 s; the shot check marked about 0.5 s of each, and the cut points sat right at the edge of the mark.

**What changed:**
- Shot check (CLAUDE.md, step 6b): a blend is marked from the first frame where the next shot shows through to the
  last frame where the old one does, about 1 s, not 0.5 s. When in doubt, mark 0.35 s more on each side.
- Edit plan: a cut never starts or ends inside a marked blend. A sentence whose clean footage runs short gets a second
  shot from the same scene of the group (same video or its spare first, so the person on screen stays the same).
- The tension sentence (s2) shows the before-state only; it is never filled with footage of the lit or finished product.
- One person per timeline: footage borrowed from another variant of the group shows the product only, never that
  variant's person (the owner saw two different women in wall art V1).
- Check before saving: one frame every 0.1 s at the start and end of every cut, not only the plan sheet's 0.6 s.
- The voice matches the person on screen (the owner: men get the male voice). A Negen voice-over that runs past the
  20 s video loses its CTA sentence (coffee table V2 and V3 with Dawn).

**Automated (applies from the next week):**
- `capcut/shot_sheet.py` finds Negen's crossfades itself (a frame that is the mix of the frames around it), marks them
  orange on the sheet and writes them to `"fades"` in `shots.json`.
- `capcut/build_project.py`: every blend is widened by 0.35 s each side (`FADE_PAD`); a cut that starts inside a fade,
  a bad stretch or another variant's person moves to its end and the build says so; no shot runs on into one. Another
  variant's footage is unusable inside its `"person"` stretches, in the edit plan and in the automatic replacements.
  A cut-off voice-over (its last sentence plays far faster than the rest) is reported. A video downloaded again (a new
  voice-over) replaces its old copy in the CapCut media folder and its voice-over extract; before, the build kept the
  old copies and the new voice never reached CapCut.
- `capcut/plan_sheet.py` flags a cut-off last sentence and checks borrowed footage the same way.
- `capcut/cut_sheet.py` (new): the first and last frames of every cut, 0.1 s apart, rows from another variant marked.
- `brand/pick_cast.py` gives every video its `"voice"` from the person's gender and the brand's `"voices"` in
  `brand/brands.json` (Spry: Dawn for a woman, Evan for a man; ETW: Evan for everyone, its brand voice).

**By hand at the shot check:** `"person"` stretches per video (no script can tell people apart yet).

**Tested on:** the Nov 9 week, 12 timelines, rebuilt with `--replace` (old timelines in `capcut-backup/`). This week's
`shots.json` carries `"fades_padded": true` (its blends were widened by hand) so the build does not widen them twice.

## 2026-10-29 - Who is on screen: a cast matched to the buyers, varied every week

**Why:** the owner wants the people in the videos to look like our customers, or like who they want to become, not
the same model-like woman in cream every time (Oct 31: one look across the console and chair groups).

**What changed:**
- `brand/cast.json`: 30 people in four pools (everyday buyers F/M 40-49, hosts, first-home nesters in their 30s,
  material skeptics M45-54), each relatable or aspirational, in varied looks and colours. Persona codes map to a pool
  (WIN-02 host, WIN-03 nester, CST-07 skeptic...); the rest use everyday. Grounded in the team persona DB and
  purchaser overlay (casting band F40-49, gender about 50/50, US Sunbelt homes; skeptic lanes M45-54).
- `brand/pick_cast.py` (CLAUDE.md step 1): one person per video, three different per group, relatable and
  aspirational alternating, nobody from last week while the pool allows; the same result if run again.
- `ad-brief-compiler` 5: ACTOR A is the video's cast, written in full in every row; the go-ahead table shows who.

**Tested on:** three simulated weeks of this week's 12 groups: no person repeated week to week, the mix alternating.

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
