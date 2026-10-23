# Naming and the tracking sheet

Every finished video gets the team's codified name and one row of fields for the working sheet.

## The name

`<Name> | <Angle> | <SKU> - <Code> - <DD/MM/YYYY>`

Example: `Triết Agent | Reading Nook | SINLKITB653 - VIDPDTHC1NA - 30/10/2026`

- Name: the person's creator label in the sheet (ask; never guess it).
- Angle: the group's angle, as written, under 20 characters.
- SKU: the product SKU without the variant suffix.
- Date: the date the person gives for the batch (ask).
- File name: the same, with the date written `DD-MM-YYYY`, because `/` cannot be in a file name.
  On Windows `|` cannot be in a file name either: there use ` - ` in place of ` | ` for the file only.

## The code

`VID` + ad style + awareness + hook type + variant order + offer, for example `VIDPDTHC1NA`.

| Field | Value in the sheet | Code |
|---|---|---|
| Format | Video | VID |
| Ad style | Product demo / UGC / B&A | PD / UG / BA |
| Level of awareness | TOF / MOF / BOF | T / M / B |
| Hook type | Call out Hook / Product Hook / Intrigue Hook | HC / HP / HI |
| Variant order | 1, 2, 3 (V1-V3 of the group) | 1 / 2 / 3 |
| Offer | Không có offer / Free shipping / Combo 6 (Free Shipping + Customize) | NA / FS / CO |

How to choose:
- Ad style: Negen videos with a hand and no person on camera are Product demo (PD).
- Awareness: a callout of the viewer's own space or problem (empty wall, bare corner) is TOF; a hook that assumes
  they already shop the category ("Most sideboards are just boxes") is MOF; Solution-aware is MOF.
- Hook type: callout of the viewer's situation or doubt = Call out Hook; the product shown as the answer =
  Product Hook; a curiosity opening ("Where does your eye land?") = Intrigue Hook.
- Offer: Không có offer unless the brief carries a verified offer.
- Persona: the code from the sheet's Persona dropdown (for example TBS-01). Ask the person; suggest one only if they
  ask, and say it is a suggestion.

## The sheet row

One tab-separated line per video in `work/<week>/sheet-rows.tsv`, in the sheet's column order (the row id is left
blank; the sheet numbers it):

`(id) | Tháng MM/YYYY | Tháng MM/YYYY | YYYY-MM-01 | Name | Name | Product | Product | SKU | Persona | Angle |
Offer | Offer | Offer code | Video | VID | Ad style | Ad style | Ad style code | Awareness | Awareness |
Awareness code | Hook type | Hook type | Hook type code | (blank) | Hook text | Variant order | DD-Mon |
Codified name | Chờ duyệt | Done | (blank) | File name`

Also write `work/<week>/log.md`: one table with Product, SKU, Persona, Angle, Offer, Ad style, Awareness, Hook type,
Hook, Code and Name per video.
