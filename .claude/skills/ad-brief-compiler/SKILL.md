---
name: ad-brief-compiler
description: Convert an approved Negen product storyboard (8 panels A01-B04 + VO), the product page facts and verified offer facts into paste-ready values for Negen's Section 7 Ad brief (Ad job, Hook, Proof, Offer, Call to action, On-screen text, 8 Scene rows) for a Conversion Creative V3 video batch. Use when a team member pastes a storyboard and product facts and wants the Ad brief fields to copy into Negen.
---

# Ad Brief Compiler (v2)

## Purpose

Fill Negen's Section 7 "Ad brief" so a Conversion Creative V3 batch turns the approved storyboard into a 20-second, 9:16 ad.

Do not generate video. Do not invent a new angle. Keep the storyboard's argument, and fix only what is listed under "Corrections you must make".

The person using this skill will copy each field into Negen by hand. Make every field paste-ready, in the exact order and format below.

---

## Inputs to ask for (if missing)

1. The storyboard text from Negen Review: angle line, the 8 panels (A01-A04, B01-B04) with JOB and DIRECT, the continuity note, and the VO.
2. The product page "Details" text (description and variants) from Negen Products.
3. Store / brand (Spryinterior or ET Woodcrafts).

If the product page is missing, ask for it. Never fill product facts from memory.

---

## Corrections you must make to the storyboard

### 1. Hook = a hand action in the first 2 seconds
A01 must show a hand doing something with the product from frame one: placing, sliding, lifting, opening, tracing, pulling out.
If the storyboard's A01 is a slow push-in, an empty room, a light sweep, or a macro with no action, rewrite A01 as a hand action that fits the same angle.

The hand must belong to a body the viewer can place (see 6. Hands need a body). For wall-mounted products the hook
is ACTOR A seen from behind or the side, arms visible up to the shoulders, never two hands rising from below the frame.

Avoid hooks that depend on the order of two framings, such as "empty wall, then the product appears" or "macro first, then reveal the whole piece". The video model often plays these in reverse or blends them with a dissolve.

### 2. Camera variety
Every scene row names ONE clear camera move, written first. Use energetic, physically possible moves:
fast push-in, crash zoom, orbit (45-90 degrees), crane up or down, top-down descending to eye level, low-angle dolly through a foreground object, handheld follow of the hand, parallax slide past a foreground object, whip pan.

- Vary the angle across the 8 rows: at least one overhead or top-down, one low angle, one close macro, one wide.
- Never two rows in a row with the same angle and move.
- "Slow push-in", "slow slide" and "locked-off" at most once each. Locked-off only on B04.

### 3. Wide products stay inside the frame
For long or wide products (TV stands, consoles, kitchen islands, sideboards, long wall panels), every wide shot must say "whole product inside the central 70% of the frame". The 9:16 crop otherwise cuts the ends and the AI check marks the video down.

### 4. Product truth
- Only use features stated on the product page or clearly visible in the product photos.
- If the storyboard mentions something the page does not support (for example "live edge", "drawers", a hidden interior), remove it or ask.
- Do not show the inside of closed storage unless the product photos show it. Prefer "the item goes behind the panel and the panel closes flush".

### 5. Continuity
- One recurring person only, as ACTOR A, shown as the right hand and forearm with the body placed as in 6. Fix one sleeve description and repeat it every time the hand appears (for example "ACTOR A's right hand, cream knit cuff").
- Rows with no person end with "No hand."
- Anything placed stays placed; anything removed stays removed; the final frame shows the accumulated state.
- One time of day and one light for all 8 rows (for example "late-morning sun from the left"); never day to evening.

### 6. Hands need a body
Videos where an arm appears from nowhere get cut in the edit. Every row with a hand says where the body is:
- **Person in frame:** ACTOR A's shoulder, back or side is visible (over-the-shoulder, from behind, side-on), or
- **Eye-level POV:** the camera is ACTOR A's eyes and the arm reaches forward from the bottom edge to something at
  waist or table height in front of them.

Never: hands rising from below the frame to something at or above eye level (wall art, high shelves, mirrors); a
hand or arm coming out of the wall, the product or a window; two hands with no person in a wide shot; a hand in a
top-down shot of a floor. Close-ups of wall-mounted products have no hand ("No hand.").

### 7. Organic and sculptural products
Tree shelves, live-edge panels, wall sculptures and other organic shapes drift most in close-ups (a trunk turns into
a pillar, a wide panel turns tall or into a thick box). For these keep at least 5 of the 8 rows medium or wide, name
the part in frame for every close-up ("the trunk where it meets the bench"), and keep the product's orientation.

---

## Variant set: always 3 briefs per SKU + angle

The team tests in groups of 3: one SKU, one angle, three videos. Return three complete Ad briefs, V1, V2 and V3.

Keep identical across V1-V3: AD JOB, PROOF, OFFER, CALL TO ACTION, the product truth, and on-screen Lines 2-5
(unless the hook change makes a line wrong).

Change in each variant:
- **Hook:** a different hand action or situation in A01, and a different on-screen Line 1. The three hooks must
  be clearly different ideas, not rewordings (for example: a use moment, a before-state problem, a tactile detail).
- **Delivery:** a different way of showing the same argument: camera style (handheld close vs. crane and orbit
  vs. top-down), pacing (fast cuts vs. one long move per row), and use scene. Note the intended VO tone in one
  line (for example: calm, direct, playful).
- **Voice-over:** only the first sentence (the hook) changes; sentences 2 to the end are the same in V1-V3.

Before the three briefs, print a 3-row summary: Variant | Hook idea | Delivery idea, so the person can check
they really differ. Batch names: "<Date> - <Product> <Angle> V1", "... V2", "... V3".

---

## Output: paste in this order

### AD JOB
One sentence: what the viewer should believe by the end. Customer-facing, not "make an ad for...".

### HOOK (first 2 s)
One or two sentences describing the hand action and the camera move in the first 2 seconds.

### PROOF
Claim, then what the viewer actually sees. One or two sentences. Only verified features.

### OFFER
Only if the product page states it (for example "Custom sizing available on request."). Otherwise write: LEAVE BLANK.
Never invent discounts, shipping, warranty, returns or deadlines.

### CALL TO ACTION
Short. Spry: "Shop the <product>" (for example "Shop the shelf"). ET Woodcrafts: "Explore the Collection".

### VO SCRIPT (Write my own)
We write the voice-over; Negen's "AI writes it" writes its own words, which then do not match the on-screen text.
- 36-42 words in 6 short sentences, about 14.5-17 s at 2.5 words a second (the batch uses "Keep speed").
- Sentence 1 says on-screen Line 1 (the hook), sentence 2 Line 2 (the punchline), 3 Line 3, 4 Line 4, 5 Line 5,
  sentence 6 is the call to action. Each sentence uses the line's own words and may add 2-6 words around them.
- Spoken English, no lists of features, no claim the product page does not support.

### ON-SCREEN TEXT
Exactly 5 lines, each the key words of its VO sentence, each with From and To in seconds. Time them from the VO at
about 2.5 words a second from 0 s (Negen's own estimate): a line is on screen while its sentence is spoken (Line 1 about 0-2.5 s). The last
line must end by 17 s, because Negen adds the CTA end card from 17.1 s.

Each line 2-6 words, buyer-facing, no generic luxury words, no claims the product page does not support. Line 5 may carry the verified offer.

### SCENES
8 rows. For each row give: Shot, Camera direction, Job, Seconds.

- Shot: A01, A02, A03, A04, B01, B02, B03, B04.
- Job: choose only from Negen's dropdown: Hook, Why it matters, Detail, Bridge, Proof, In use, Payoff, End frame.
  Default mapping: A01 Hook, A02 Why it matters, A03 Detail, A04 Bridge, B01 Proof, B02 In use, B03 Payoff, B04 End frame.
- Seconds: default 2, 3, 3, 2, 3, 2, 3, 2 (total 20). The total must be exactly 20.
- Camera direction: one or two sentences, under about 200 characters. Start with the camera move. Then what is in frame, the hand action if any, and "No hand." if none.
- A04 ends mid-action; B01 continues the same action from the same state.
- Each row shows what the VO is saying at that moment (the shelves when it says "open shelves"); write the rows
  from the VO sentences, not the other way round.
- A02 carries the punchline (Line 2): it opens on a hard cut to a contrasting framing of the product (a macro
  detail, a reverse angle or a top-down), never a continuation of A01's shot.

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
- Wide product kept inside the central 70%: YES/NO/N/A
- Every row with a hand says where ACTOR A's body is; no hands from below to wall height: YES/NO
- One time of day and light in all rows: YES/NO
- VO is 36-42 words, sentence n says Line n, the last sentence is the CTA: YES/NO
- A02 opens on a hard cut to a different framing (the punchline): YES/NO

---

## Reminders for the Negen batch (repeat these at the end of every answer)

- Skill: Conversion Creative V3. Shots: PART A and PART B. Format 9:16. Length 20 s. Continuous, Cut.
- References: pick the storyboard poster from Pick from media > Generated. Tick Style, Composition and Lighting. Do NOT tick Camera or Everything (they make the camera static).
- Voice-over: "Write my own" with the VO SCRIPT, Advanced > Fit to the video length: "Keep speed".
- Direct the video: the standing direction in references/video-direction.md, as-is.
- Brand: SpryInterior for Spry products, ET Woodcrafts for ETW products.
- Batch name: "<Date> - <Product> <Angle> V1|V2|V3". No personal or tool names.
- Two videos come out per batch. Keep the one with the higher AI score and product match; the PART A video is usually but not always better.
