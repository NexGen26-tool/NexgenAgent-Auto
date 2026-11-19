# Fundamentals: the reality tests every shot passes

These are not taste. A real person filming a real home with a phone could never produce a shot that fails one of
them, so a viewer feels the fake at once, even without naming it. The video model we use has no idea of object
permanence, identity or cause and effect: it fails these by default, in every batch. So we test for them on every
shot of every final cut, at full size, before anything is saved. Nobody waits for the owner to find them.

The list below is the tests, not the symptoms. A failure nobody has named before still fails a test. When a shot
looks "a bit off", find the test it breaks.

## How strict: hard fails and small differences (owner's sofa V1 cut, Nov 18)

The owner's own cut of sofa V1 kept shots the reviewer had failed: a slightly different trouser shade, a small notch
in the table top, the same set on differently patterned paving in an end wide. Judge like a viewer watching once on a
phone:
- HARD FAIL (never used): a different person or a second person; the product changing shape, parts, number of pieces
  or position; anything moving by itself; a person cut in half; a crossfade ghost or burned-in text; a room that a
  viewer would see as another room (indoors: other walls, sofa, windows).
- SMALL DIFFERENCE (allowed in a wide or medium shot, noted, not failed): a clothing shade, a prop or cushion count, a
  small detail of the product's edge or top, the paving or lawn pattern of the same kind of garden, light that shifts
  a little. The same kind of place (the hedge garden with lavender, the panelled office) counts as one place.
- ALLOWED (owner's V8 cut, Nov 19): a close-up or an empty product shot from another take or room (a drawer
  close-up, a hand on the top, the empty desk in its best room); a hand with no face in a close-up, even from another
  take. "Another room" is a hard fail only for wides and mediums with the video's person in them.
- SMALL DIFFERENCE (owner's V9 cut, Nov 19): a thin glass-like sheen or plate on the top in a close-up or medium,
  when the shot acts out its sentence (the laptop closing, a drawer pulled, the mug). A glass top that changes the
  product in a wide is still a fail.

## 1. Object permanence: the product is one solid thing

Our product is a real piece of furniture. Between the first and the last frame of a shot, and from shot to shot of
one video, it keeps:
- its **shape and outline** as the product photo shows it (a U leg stays a U leg; a square block never becomes
  curved; a tree trunk never becomes a pillar);
- its **parts**: the same number of drawers, legs, shelves, pieces; nothing appears, splits, merges or vanishes;
- its **size** against the room and the person;
- its **place**: it does not slide, glide, float or end up somewhere else between shots;
- its **material and finish**: no glass top, no lights the page does not sell, the same wood tone.

Compare every shot with the product photo, and the hook with the body. Close-ups hardest.

## 1b. One place: a video stays in one room

The shots of one video happen in one room, with the same sofa, rug, art and props, unless the script itself moves
(a before-state in the old room). A table that jumps between three living rooms in the closing shots reads as fake.
The build's fills borrow footage from the spare and the group's other videos: each of those is its own generated room,
so the build treats every take as its own room: a timeline's wide and medium shots come from its own take only, other takes give close-ups only (Nov 18 gate: gardens a tagger called the same were four different gardens). A fill is only clean when it shows the same room (Nov 18 review: the closing shots of all three coffee-table
videos were three different rooms in a row).

## 1c. Real use: the piece stands and works the way a person uses it

A real home places furniture for the person who uses it, and a viewer reads anything else as staged or fake, even
without naming it. In every shot with a person:
- drawers, doors and lids face the person who uses them: a desk's drawers on the side of the chair she sits in, a
  vanity's doors toward the person at the sink, a sideboard's doors toward the room; she can reach them from where she
  is (Nov 18: desk V1's drawers faced the camera, away from the woman sitting at it);
- the person sits at a desk on the side with the knee space and the drawers, on a sofa facing the room, at a table
  with her legs under it; a console, shelf or TV cabinet stands against its wall with its open side to the room;
- an object is used the way its owner would use it: a laptop opened by her hands, a mug put down on the top, a
  drawer pulled by her hand on its handle.
The product photo shows the product from the front for the catalogue; it does not decide which side the person is
on. The brief places the person on the side the piece is used from, and the camera where it can see both.
- An empty shot with no chair in it may show the catalogue front view (the owner used one in V7, Nov 19). An empty
  shot with a chair behind the desk and the drawers facing away from it fails: the chair says where she sits.
- An arm reaching around the piece to the far side to open a drawer fails, and so does any drawer that opens in a
  shot whose rows did not ask for it (Negen invents an extra drawer under the top whenever a drawer opens).

## 2. Causality: nothing moves without a cause

A drawer, door, lid, cushion or the piece itself moves only when a visible hand moves it, at the speed a hand would.
A drawer that slides out while hands rest on the desk, a table that drifts, a book that appears on a shelf: fail.
The camera may move; the room may not.

## 3. Identity: one person, the same person

A review or first-person video has one narrator and shows one person: the cast's `"who"` in `week.json`. Across all
shots of the video (and the spare footage it borrows), that person keeps face, age, hair, glasses, skin tone and
clothes. A second person, a passer-by, a reflection of someone else, or another actor taking over: fail. Compare
faces at full size against the `"who"` line, not on small tiles.

## 4. Bodies: a person is physically possible

Two arms, two legs, hands with fingers, feet on the floor, a hand attached to a body that could reach there, no
limb through furniture, no head or body cut in half by the frame, the right scale against the room.

## 5. Voice and story match the picture

- The voice matches the person on screen: a woman on screen is voiced by a woman, a man by a man. ("I" in the
  script is the person we see.) The build checks this itself.
- Every word on screen and in the voice-over describes something the picture shows: a look word ("curved",
  "floating", "lit") must be visible in the product photo, not only written on the page.
- A problem sentence plays over the problem, never over our product; a feeling sentence over that feeling.

## 6. Frames are clean

No crossfade blend between two shots, no text burned into the picture, no cloned props (identical blank books,
copied bottles), no hallucinated objects, no jump from day to night inside one scene.

## How it is enforced

1. `python capcut/build_project.py work/<week>/capcut.json` (dry run) writes, for every timeline, the final cut's
   shots (`work/<week>/plan/cut.json`) and one review sheet per timeline in `work/<week>/qc/`: every shot of the
   final cut as its first, middle and last frame at full phone size, the product photo and the cast's `"who"` at the
   top.
2. The reviewer looks at every shot of every sheet against tests 1-6 and writes the verdict into
   `work/<week>/qc.json` per timeline: `{"cut": "<hash printed on the sheet>", "pass": true|false, "fails":
   [[shot, "test N: what"]]}`. A failing shot is fixed in the week's material (mark the stretch bad in `shots.json`,
   pick another shot) and the sheet is made again.
3. `--save` and `--replace` refuse any timeline whose current cut has no passed review (the hash changes when the cut
   changes), and any timeline whose voice does not match its person's gender. There is no flag to skip it.

The reviewer is a fresh look: when Claude built the cut, a separate reviewer agent judges the sheets, given only the
sheets, this file and the product photo, so it does not see what it expects to see.
