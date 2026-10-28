# What works and what fails (runs of Oct 19-22)

- Hooks: a hand action in the first 2 seconds works. "Change of framing" hooks (empty wall then product, macro then
  reveal) come out reversed or as a dissolve.
- Camera: write one strong move per scene row (orbit, crane, top-down, low dolly through foreground, handheld
  follow, fast push-in, parallax); vary the angles; only B04 locked-off. With the poster used for Camera or
  Everything, the video copies the poster's still frames and the camera barely moves.
- Wide products (TV stands, kitchen islands, long panels) lose points to the 9:16 crop: ask for the whole product
  inside the central 70% in every wide row.
- Product drift is the main quality risk (carving flatter, colour paler). Check product match before keeping.
- The last on-screen line must end by 17 s; Negen's CTA end card starts at 17.1 s.
- The voice-over can run past the video and lose its last words; check the end.
- Two videos per batch: PART A is usually, not always, better. Keep the higher AI score + product match.
- The AI check retries a failed start frame but keeps the retry even when it scores lower.
- Multi-product video batches only work inside one category (one Ad brief per batch). Storyboard batches can mix.
- ChatGPT in 9router signs out and hits limits often; every image step stops until an admin fixes it. Grok runs out
  of credits; video parts stop. Both resume by themselves once fixed. Plan storyboards early in the week.
- Negen has no rename and no delete. A wrong batch name stays; cancel it and run again with the right name.
- Downloads from the browser get blocked; the Exports share link + curl always works.

# CapCut finishing (first build, Oct 23)

- The first build kept Negen's full 20 s and needed a lot of hand work: the voice-over stops at about 16-17 s,
  so the person cut every video to 14-16 s, re-timed every text line and added music (Spry "Neon Meow's Jazz Club
  [Bonus]" at 24%, ETW "Soulful Groove" at 100%). The builder now cuts to the voice-over, plays it at 1.08x
  and adds that music, so videos come out at about 16-17 s.
- Still by hand: the person sped footage 1.2-1.3x on some and swapped weak shots
  for shots from the sibling V1/V2/V3 video of the same product.
- Sculptural products (tree bookshelves) drift most in close-ups and macro shots: the trunk turns into a pillar,
  the bench into a separate table, the tree into a symmetric shelf. Wide room shots stay closest to the product
  photo. Negen's product match still gave 8/10, so watch every close-up before keeping a video. For these products,
  keep most scene rows medium or wide and write which part of the product is in frame.
- Arms from nowhere come from hand-only briefs: "ACTOR A's right hand" with no body. Worst on wall-mounted products
  (two hands rising from below to hang wall art). Briefs now place the body for every hand; the shot check cuts any
  that still appear.
- Grok blends two shots for about 0.5 s at most scene changes inside a part, and can jump from day to evening.
- Boxy products (sideboards) keep their shape; organic ones (tree shelves, live-edge wall art) drift in close-ups.
- Negen's "AI writes it" voice-over does not read the brief's on-screen lines, so text and voice drift apart. Write
  the on-screen lines from the voice-over script and time them to it (edit plan, CLAUDE.md step 7).
- A punchline over the continuing opening shot lands softly; start it on a hard cut with a Slide Blur and a punch-in.
- Negen's voice-over "Write my own" + "Keep speed" (fit=pad) plays our script at natural speed: 34 words = 13.6 s.
  With our own script the on-screen text, the voice and the scenes come from one source.

# Oct 31 batch (storyboard-to-video route, owner review Oct 28)

- The owner liked the look: colours, staging, hierarchy, camera, light; product and room real and relatable.
- Rejected for: hands with wrong physics; a "plain, soulless console" line over our own console (the contrast
  argument was fine; the footage under it showed ours, so ours read as the plain one); text, voice and footage not matching; one music
  track for all 12, no sound effects, no accent in the text.
- Fixes that held without regenerating footage: our own voice-over per version (Keep speed), on-screen lines from
  its sentences, shots picked per sentence around the bad hand stretches, music rotated per brand, SFX.
- Product photos staged with lights make the model light an unlit product (wine rack); an UNLIT note first in the
  part prompt fixed it.
- A storyboard made at 1:1 gives a square video; always 9:16.
- Negen's voices pause 0.3-0.4 s between sentences and about as long at some commas; room sound in the clip hides
  short pauses unless the voice band is filtered first. The build now uses the script's commas and pace to tell
  them apart (right on all 12).
- The 8 generated parts each hold one shot; a planned shot that runs past its part flashes the next one.

# Look test vs arc test (curved console, Oct 28)
- The script carries the conversion, not the footage: same look and edit, but the owner rated the feature-list
  script ("Oval top, S-curve base. Keys down, palm on the grain. Six widths.") below the creative team's arc. A
  converting script moves stake -> before-state -> turn -> reason -> doubt cleared -> offer -> CTA; a feature is
  only ever the reason or the answer to a doubt.
- A before-state row works when it says what is NOT there: "a bare hallway wall... no console, no furniture against
  this wall" gave a clean bare-wall walk in all three videos, with no look-alike console.
- The voice matters to pacing: the template's default voice reads flat with 0.1-0.2 s gaps; pick the brand's voice.
- Late close-ups of the product with props on it (the bowl, 15-18 s) drift most; keep the offer sentence on a
  medium or wide shot.

# Final 12 (Oct 28 afternoon)
- The UNLIT note must be the full sentence at the start of every row; shortened, the wine rack came out lit in every
  End-of-year take. Lit stretches are bad footage (the page says no lighting).
- Before-state rows that name what is NOT there worked for all four products (bare wall, metal side chair, crammed
  cupboard, crowded counter with no rack).
- A doubt asked and answered in one slot needs a comma, not "?", or the build counts an extra sentence.

# What cost the day (Oct 28)
- Switching route mid-week is the expensive mistake: each switch (by-hand storyboard route, another system's copy,
  a look test, an arc test) redid briefs, batches and the edit. Finish the week on the route it started on; test a
  change on the next week.
- Drift shows in hands and feet, not in the product: the per-video shot sheets were judged by the product and missed
  a third foot, floating feet and an arm from an edge. The plan sheet (only the frames the timelines use) caught them.
- Tangled poses (curled up, legs crossed, feet tucked) and opening doors are where the model breaks bodies and
  physics. Brief simple poses and things already open.
