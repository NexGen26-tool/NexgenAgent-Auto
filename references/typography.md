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

## Things to avoid

- The same colour, face and position in every ad of a week (Meta reads look-alike ads as one).
- Text that arrives before its words are spoken, or stays over a sentence about something else.
- All-caps paragraphs, centred long sentences, more than one accent colour, outlines plus shadows plus boxes.
- Text over faces, hands at work or the product's outline.
