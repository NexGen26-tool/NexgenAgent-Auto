# Negen, the parts the fast lane uses

Negen: https://marketing-tool.nexgenbros.com. Shared NexGen workspace: everyone's batches show in Batches and Review.

## Sections
- Products: synced from Shopify, two stores (ET Woodcrafts, Spryinterior). The same design often exists in both
  stores under different names and SKUs.
- Skills that matter:
  - Product Storyboard Reference + VO (public, id 8742da5f-3f5e-45aa-8a01-ecc289a697f1): product image in,
    8-panel storyboard poster (A01-A04, B01-B04) plus a 2-part VO script out.
  - Conversion Creative V3 (public): the proven video skill. Two tool-level shots, PART A and PART B, each a
    10 s edited sequence, joined into about 20 s. No text in the footage.
- Batches (`/generate`): where runs are set up and listed. "Edit & run again" (`/generate/new?from_batch=<id>`)
  copies every setting of an old batch.
- Review: approve or reject, see steps, critique, AI score, product match; storyboards are read here.
- Exports: ZIP of finished items, optionally as a share link (used for downloads, see CLAUDE.md step 6).
- Settings > Brands: ET Woodcrafts, Roy Timber, SpryInterior (logo, fonts, colours, CTA lines).
- Bottom left: quota (ChatGPT and Grok counts today) and how many jobs run at once.

## Settings of the approved video batch (copied by the template batches in brand/brands.json)
- Skill Conversion Creative V3. Output Videos, 2 per product, start frame AI picture.
- Shots PART A and PART B. Format Story / Reel 9:16. Auto-review off.
- Image engine GPT 5.6 Sol Image, video engine Grok Imagine Video 1.5. Total 20 s, parts Continuous, between
  parts Cut, 720p, product photos with each clip off.
- Voice-over: AI writes it, English, Sarah (Eleven v3 Conversational).
- Reference: the storyboard poster, use Style + Composition + Lighting only (Camera or Everything make the camera
  static), analysed by the model.
- Brand: ET Woodcrafts or SpryInterior. Ad brief: every field filled, 5 on-screen lines, 8 scene rows.
- The run goes Brief > Image > AI check > Script > Video parts > Merge > VO script > Voice-over.

## Storyboard to video (the route of the Oct 31 batch: the look the owner wants)
The storyboard's own 8 panels animated directly give real, relatable rooms with people living in them and the
product true to its photos. How it ran:
- Storyboard batch per product at **9:16** (1:1 gives a square 720x720 video). Approve it in Review.
- Before making the video, each part has Edit (what happens, camera, action, on screen, into next, video prompt) >
  Save. Put the brief's scene row for that part there; a product note (UNLIT) goes first in the video prompt.
  "Direct the video" does not exist on this route; the field limits of the ad brief do not apply.
- "Make video from storyboard · 8 shots · 20 s": 8 parts (3+3+2+2+3+3+2+2 s), 20.3 s, 720x1280, Grok Imagine Video
  1.5, included in the subscription. This is V1.
- V2 and V3: Edit Part 1 with that variant's hook row > Save > Make again > "Make again (included in subscription)".
  Each makes a new version of the whole video (v2, v3...); click the version chip to select one.
- Voice-over per version: "New voice-over for video vN" > Write my own > voice > Advanced (open the summary) >
  "Keep speed" > Make voice-over (about $0.02). Without Keep speed the voice is stretched to 20 s.
- Download: the share link holds only the current version. Fetch `/media/<id>` of the version's "video + VO" in the
  page and save it (the browser pane blocks downloads).
- Scripted routines for this route are not in `negen/` yet; drive the page.

## Cost
Image and video engines are included in the subscription. Voice-over (ElevenLabs) is about $0.01-0.03 a video.

## The clean deliverable
In Review, "v1 + VO v1" (current version) is the clean video with voice-over and no text or logo. The export ZIP
holds exactly that file for each of the two videos of a batch, plus manifest.csv with ai_score and product_match.
