# Camera rule

The camera rule lives in the ad-brief-compiler skill (section 2, "Shot structure"). Each video picks, from its script,
one shot structure in `capcut/templates/structures.json`:
- argued: argued cuts;
- follow: a follow, cut on action;
- tableau: still-life tableaux;
- pov: first-person;
- match: before/after match cuts;
- montage: a detail montage.

An explore group uses at least two. In "argued", each scene row's size and camera move come from the sentence it plays
under:
- the hook a moving medium on ACTOR A with the product, with an event in the first second;
- the tension a wide of the before-state;
- the punchline a hard cut to a new size;
- a reason a CLOSE, TOP-DOWN or LOW on the part the sentence names;
- the fit a wide dolly with ACTOR A for scale;
- the offer an arc around the product;
- the end frame a locked-off wide.

The other structures each have their own 8 rows. Every row starts with "SIZE / MOVE:", and ACTOR A is in at least 4
of the 8 rows. In argued, follow, tableau and montage the size changes at every row; `cut_sheet.py` prints each cut's
size and SAME SIZE where two cuts in a row repeat one.

Every structure fits Negen's Conversion Creative V3 skill: each 10 s part becomes about three shots with real cuts
(never one continuous camera move), and the first 1-2 s show a visible event (never a static beauty shot or a slow
decorative push-in). The Negen skill is shared by the whole team and is not changed for the fast lane.

The poster goes in as Style + Composition + Lighting and is also sent to the image model; never Camera or Everything
(the video copies the poster's still frames and barely moves).

History:
- **Until 2026-10-28:** the rule pushed energetic moves (crash zoom, crane, top-down, macro) against a static camera.
  Those turned the storyboard's lived-in scenes into hand-led product demos.
- **2026-10-28 to 2026-11-17:** most rows were eye-level medium or wide, with at most two close details and no
  top-down. The footage was lived-in but flat, and the shots often did not show what their sentence said.
- **From 2026-11-17 (owner):** shot structures picked per script. "Argued" is the shot map: dynamic and tied to the
  argument. Every structure keeps the people, the hands with a body, and the outline in frame for close-ups; crash
  zooms and whip pans stay out.

See `references/rule-changes.md`.
