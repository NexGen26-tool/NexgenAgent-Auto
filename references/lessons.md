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
