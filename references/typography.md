# Typography: how the on-screen lines look and when they appear

The CapCut build sets every ad's text in a style picked for its argument, not in one house look for every video
(owner, Nov 16: "they follow too strictly with my very first example. Every video use the same color, font,
positioning... I need them to be flexible depending on the script and the argument"). The styles live in
`capcut/templates/type_styles.json`; `capcut/typeset.py` applies them; `build_project.py` calls it for every timeline.

## The styles

| Style | For | Faces | Colour and emphasis | Placement |
|---|---|---|---|---|
| statement | turn, myth: an argument against a problem | one humanist bold face (PT Sans Bold) | white, the tension word warm yellow | centred, hook high so the problem picture below reads; proof lines low |
| editorial | story, ritual: first person, calm | italic display serif for the feeling, small sans for the rest | warm ivory, one amber word | left-aligned lower third, like a caption |
| counter | list: three reasons | big italic display numerals 1/2/3, reasons in sans | white, amber numerals | left-aligned high, the count is the structure |
| keepsake | gift | small tracked sans label over italic display serif | ivory, one gold word | centred low, like a card |
| contrast | after: the finished room is the hero | small tracked sans label over a display phrase | white, one yellow word | centred top third |

`"type"` on a timeline in `capcut.json` picks another style; `"type": "house"` keeps the original house edit (the
look of the first approved video). A new style is a new entry in `type_styles.json` with a row here.

## Rules every style keeps

- Two typefaces at most in one video, one of them the voice of the brand's facts (sans), one for feeling (display
  serif) when the argument is personal.
- One emphasis per line: colour or the display face on the word that carries the tension, never two accents.
- Hierarchy by size: the hook and the punchline biggest, proof lines smaller, the offer quiet, the CTA distinct.
- A line is a phrase, not a sentence: at most about six words, two lines on screen at most.
- Safe area: no text in the top 15% or the bottom 24% of the frame (Reels and Feed UI), none hard against the right
  edge (icons): x within +-0.86, y within -0.52 and 0.70.
- Placement follows the picture: a style puts text where its formats' shots leave room (the hook high when the
  problem shot fills the bottom, captions low when the person is centred). A line never sits over the product's
  defining part or a face; move it with the style or `"type"`.
- Contrast with a soft shadow, not a heavy black outline (the outline is the house look only).
- The words come from the voice-over: each line echoes words the voice says in its sentence. The build prints
  TEXT-VOICE for a line whose words the voice never says there; rewrite that line.
- Timing: a line comes up 0.1 s before the voice says the first word it carries (not at the start of its sentence),
  and stays at least 0.8 s. The build finds the words with Windows' own speech recogniser on the voice-over
  (`capcut/vo_align.ps1`, nothing to install); on a Mac the word's place among the sentence's letters estimates it.
- The offer on screen is the brand's `offer.on_screen` from `brand/brands.json` ("Free shipping on every order"),
  never a code; the store is "Spry Interior" or "ET Woodcrafts", never "Spry" alone.

## The owner's hand edits, built in (Nov 17, the 13/11 set)

The owner finished V1-V12 by hand in CapCut. Each change they made across the videos is now the build's default:
- **Line 2 is plain text.** The punchline's setup and payoff are two ordinary text clips, not the house edit's
  animated title clip. The owner replaced it by hand in six videos, so it can be edited in place.
- **The hook's subject leads.** It is the biggest word on screen, from the first frame:
  - "KNOW SOMEONE" was raised to 9.4, "3 reasons" and "This corner" to 12.6;
  - the subject is the thing or the person ("This corner"), never a verb phrase ("Used to be");
  - the linking words and the accent come up as their own clip when the voice says them (V3 was built up word by
    word).
- **The hook leaves when the punchline's sentence starts**, and the title comes with its own words, so there is a short
  breath between them (V8).
- **Line 3 is staggered** in the gift and story styles: the first half sits left, the second half below it to the
  right (V1, V2, V8, V9, V10).
- **No full stop on screen**: "sits within reach", "Stand on wood", "On a shelf". A question mark stays.
- **The fit line weighs more**: bigger and italic in the gift style (V8 "FOUR SIZES, FOUR FINISHES"; V1 "Customized
  sizes" in the accent).
- **A scarcity beat after the offer.** When the voice reaches the scarcity words of the offer sentence, the brand's
  scarcity line takes Line 5's place: "Limited / monthly order", with "Limited" in the accent. Its words are in
  `brand/brands.json` `scarcity_on_screen`. The owner added it by hand to V1, V5, V6 and V10.
- **Accents are light, bright yellows**, never a mid gold or amber. Our products are wood, and a gold or amber accent
  over walnut or oak disappears. The owner lifted them by hand (#FFA900, #FFDC49, #FFE68D, #FFD886), and the text
  preview showed the old ones vanishing.
- **Every text has a soft dark shadow** (alpha 0.85, close and soft), in every style, so white and yellow read over
  a bright window or pale wood (owner, Nov 18).
- **Music sits under the voice at about 0.25.** The ETW tracks were at 1.0 and the owner turned each down to
  0.20-0.33.
- **Every punchline gets a transition** (Pale Clarity, the owner's pick; Slide Blur when it is missing), ritual and
  story included. The one exception is the "follow" structure, which cuts on action.
- **No text animations.** In the twelve finished videos the owner used none and removed the title's zoom. Movement
  comes from timing instead: the subject first, then the words as they are spoken, then the next line on its own
  words.

## The owner's text design (Nov 18, console V2 "Every year / I redecorate")

The owner reset the hook by hand to this, and every line follows it:
- **One block, one edge.** The lines of a text sit together, aligned to the same edge (left in the example), never
  scattered across the frame or centred on different axes.
- **Hierarchy that reads in order.** A small setup line (sans, with its one accent word: "Every **year**") leads
  into the big statement under it (display italic: "I redecorate"). Read top to bottom it is one sentence that says
  something; the words are rewritten so it does (`"line1_order": "setup_first"` on the timeline, line1 written as
  [statement, setup words, accent]).
- **Close together.** Letters at normal tracking (letter spacing 0.02 at most), lines tight (line height 1.12 x
  size), no gap between the parts of a block. Wide tracking and floating lines read as separate pieces.
- **In the empty part of the picture, beside the person**, never on a face, a body or the product's defining part:
  on the wall next to her, above the console, not over her head or across the slab.
- **The logo is locked top centre**, in every video; only its light or dark version changes with the background.
- **Fewer, fuller lines (desk V8/V9, Nov 19).** The hook repeats the voice word for word ("MY WORK STARTS / at a
  clear desk now"; "Morning coffee / on clear wood", staggered left and right); the punchline is a full sentence that
  names the product ("This solid wood office desk became / the steady part of my day", one accent word); a line that
  only restates the picture ("Clutter / Out of sight") is dropped. Hooks and offer lines sit low (y -0.3 to -0.5).
- **The CTA sits in a dark box** (white capitals on a filled background), low on the end card (y about -0.45).

## The text preview (plan check)

Every build writes one sheet per timeline in `work/<week>/plan/text/`: **one tile per shot under each text** (a
line that stays up across two or three cuts gets two or three tiles). Judge every tile, not the first or the middle
one: on Nov 18 a hook moved clear of the woman in one shot ran into her face in the next shot of the same line,
because only one frame per line had been looked at. A place set by hand (`"text_y"`) must be clear in every tile of
that line. Look at every tile:
- text over a face, a hand at work or the product's defining part;
- an accent that disappears into the wood behind it;
- a line too small to read at phone size, or crowding the edge;
- two lines fighting for the eye.

Fix it with the timeline's `"type"`, a style's `"y"`, or the line's words, then preview again. This is how the
design is judged before saving.

## Things to avoid

- The same colour, face and position in every ad of a week (Meta reads look-alike ads as one).
- Text that arrives before its words are spoken, or stays over a sentence about something else.
- All-caps paragraphs, centred long sentences, more than one accent colour, outlines plus shadows plus boxes.
- Text over faces, hands at work or the product's outline (the text preview shows it).
- A gold or amber accent over wood; a full stop at the end of a line; the hook's subject smaller than its linking words.
