// Fill one Conversion Creative V3 video batch in Negen and (optionally) start it.
//
// How to use (the assistant does this through the browser's javascript tool):
//   1. Open https://marketing-tool.nexgenbros.com/generate/new?from_batch=<video_template_batch from brand/brands.json>
//      ("Edit & run again" of an approved batch: skill, engines, 20 s, PART A + B, voice-over, brand are already set).
//   2. Run:  (<this whole file>)({ ...B })   where B is:
//      sku     product SKU to search for (e.g. "SILDTTRWA085")
//      pid     Negen product id (the value of the product checkbox)
//      poster  media id of the storyboard poster (Review > storyboard > Poster)
//      brand   Negen brand id prefix, from brand/brands.json (negen_brand_prefix)
//      batch   batch name "<Mon DD> - <Product> <Angle> V1|V2|V3". Never a person's or a tool's name.
//      job, hook, proof, offer, cta   Ad brief fields ("" for offer unless the product page states one)
//      lines   [[text, from, to], ...] 5 on-screen lines, last one ends by 17 s
//      shots   8 camera directions, A01..B04 (jobs and seconds are fixed below)
//      vo      the voice-over script (Write my own, Keep speed): 7 sentences, 40-46 words (ad-brief-compiler)
//      voice   the brand's voice name from brand/brands.json (e.g. "Dawn"); "" keeps the template's voice
//      unlit   the product noun ("wine rack") when the page says no lights but the photos show some; every row
//              then starts with the full UNLIT note (week.json group "unlit")
//      direction  the standing video direction (references/video-direction.md), sent with every batch
//      start   true to press Start when every check passes; false to only fill and report
//   3. Read the returned log. "READY=true" means: one product ticked, the poster is the reference with
//      Style + Composition + Lighting (never Camera) and is also sent to the image model, the brief and lines are filled, the brand matches, and when
//      vo / direction are given: the voice-over is "Write my own" with that script at "Keep speed", the direction set.
async (B) => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  function setv(el, v) {
    if (!el) return 'MISSING';
    const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : el.tagName === 'SELECT' ? HTMLSelectElement.prototype : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, v);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    return 'ok';
  }
  const q = s => document.querySelector(s);
  const L = l => document.querySelector('[aria-label="' + l + '"]');
  const log = [];

  // product: search by SKU, tick exactly this one
  const s = L('Search products'); setv(s, B.sku);
  s.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
  let tgt = null;  // the search can take 15 s on a fresh page
  for (let i = 0; i < 24 && !tgt; i++) {
    await sleep(800); tgt = [...document.querySelectorAll('input[name=products]')].find(b => b.value === B.pid);
    if (i === 10 && !tgt) s.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));  // search again
  }
  if (!tgt) return 'PRODUCT NOT FOUND';
  if (!tgt.checked) tgt.click(); await sleep(600);
  [...document.querySelectorAll('input[name=products]:checked')].forEach(b => { if (b.value !== B.pid) b.click(); }); await sleep(600);
  log.push('products=' + [...document.querySelectorAll('input[name=products]:checked')].map(b => b.value.slice(0, 8)).join(','));

  // reference: replace the template's poster with this storyboard's poster
  const rm = [...document.querySelectorAll('button')].find(b => (b.getAttribute('aria-label') || '') === 'Remove reference 1');
  if (rm) { rm.click(); await sleep(600); }
  [...document.querySelectorAll('button')].find(b => b.innerText.trim() === 'Pick from media').click(); await sleep(900);
  [...document.querySelectorAll('button')].find(b => b.innerText.trim() === 'Generated')?.click(); await sleep(1800);
  let poster = null;
  for (let pg = 0; pg < 15 && !poster; pg++) {
    const items = [...document.querySelectorAll('button[title]')].filter(x => x.querySelector('img') && x.offsetParent)
      .map(x => ({ b: x, id: ((x.querySelector('img').src.split('/media/')[1]) || '').split('/')[0] }));
    poster = items.find(i => i.id === B.poster);
    if (!poster) {
      const nx = [...document.querySelectorAll('button')].find(x => x.innerText.trim() === 'Next' && x.offsetParent && !x.disabled);
      if (!nx) break; nx.click(); await sleep(1500);
    }
  }
  if (!poster) return 'POSTER NOT FOUND';
  poster.b.click(); await sleep(1500);
  for (const lab of ['Style', 'Composition', 'Lighting']) {
    const bs = [...document.querySelectorAll('button,label')].filter(x => x.innerText.trim() === lab && x.offsetParent);
    bs[bs.length - 1]?.click(); await sleep(400);
  }
  // the image model that draws the start pictures also sees the storyboard itself, not only a summary of it
  let refs = JSON.parse(q('input[name=references]').value);
  if (refs[0] && !refs[0].send) {
    const sendBox = [...document.querySelectorAll('label')].find(x => /Also send this image to the image model/.test(x.innerText) && x.offsetParent);
    (sendBox?.querySelector('input') || sendBox)?.click(); await sleep(500);
  }
  for (let i = 0; i < 25; i++) { refs = JSON.parse(q('input[name=references]').value); if (refs[0] && refs[0].analysis) break; await sleep(1500); }
  log.push('ref=' + JSON.stringify(refs.map(r => ({ t: r.target.slice(6, 14), use: r.use, img: !!r.send, an: !!r.analysis }))));

  // ad brief
  log.push(['job', setv(q('[name=ab_job]'), B.job), 'hook', setv(q('[name=ab_hook]'), B.hook), 'proof', setv(q('[name=ab_proof]'), B.proof),
    'offer', setv(q('[name=ab_offer]') || L('Offer'), B.offer), 'cta', setv(q('[name=ab_cta]'), B.cta)].join(' '));
  for (let n = 6; n > B.lines.length; n--) {
    const b = [...document.querySelectorAll('button')].find(x => (x.getAttribute('aria-label') || '') === 'Remove line ' + n);
    if (b) { b.click(); await sleep(300); }
  }
  B.lines.forEach((l, i) => {
    setv(L('Line ' + (i + 1) + ' text'), l[0]);
    setv(L('Line ' + (i + 1) + ' from, seconds'), String(l[1]));
    setv(L('Line ' + (i + 1) + ' to, seconds'), String(l[2]));
  });
  // a product with no lights whose photos show some (the wine rack): every row starts with the full note, or the
  // model copies the photo's light (a shortened note still gave lit shelves in every take, Oct 28)
  if (B.unlit) {
    const note = 'IMPORTANT: the ' + (typeof B.unlit === 'string' ? B.unlit : 'product') + ' is completely UNLIT, no lights or LEDs. ';
    B.shots = B.shots.map(d => d.startsWith('IMPORTANT: ') ? d : note + d);
    log.push('unlit note on ' + B.shots.length + ' rows');
  }
  const ids = ['A01', 'A02', 'A03', 'A04', 'B01', 'B02', 'B03', 'B04'];
  const jobs = ['hook', 'relevance', 'detail', 'bridge', 'proof', 'in_use', 'payoff', 'end_frame'];
  const secs = [2, 3, 3, 2, 3, 2, 3, 2];
  B.shots.forEach((d, i) => {
    const n = i + 1;
    setv(L('Shot ' + n), ids[i]); setv(L('Shot ' + n + ' direction'), d);
    setv(L('Shot ' + n + ' job'), jobs[i]); setv(L('Shot ' + n + ' seconds'), String(secs[i]));
  });
  let voOk = true, dirOk = true;
  // voice-over: our own script (it says the on-screen lines), natural speed; and the standing direction
  if (B.vo) {
    const pick = txt => { const x = [...document.querySelectorAll('label,button')].find(e => e.innerText.trim() === txt && e.offsetParent); if (x) x.click(); return !!x; };
    pick('Write my own'); await sleep(700);
    setv(L('Voice-over text'), B.vo); await sleep(300);
    if (B.voice) {  // the brand's voice (brand/brands.json "voice"), picked by name from the voice list
      const cur = () => (q('button[aria-label^="Voice:"]')?.getAttribute('aria-label') || '');
      if (!cur().startsWith('Voice: ' + B.voice)) {
        q('button[aria-label^="Voice:"]')?.click(); await sleep(900);
        [...document.querySelectorAll('button[aria-pressed]')].find(e => e.innerText.trim().startsWith(B.voice + ' ') || e.innerText.trim().split('\n')[0] === B.voice)?.click(); await sleep(700);
      }
      voOk = voOk && cur().startsWith('Voice: ' + B.voice);
      log.push('voice=' + cur().slice(7, 40));
    }
    const adv = [...document.querySelectorAll('summary,button')].find(e => /^Advanced/.test(e.innerText.trim()) && /Eleven|Adjust speed|Keep speed/.test(e.innerText) && e.offsetParent);
    if (adv && !pick('Keep speed')) { adv.click(); await sleep(500); }
    pick('Keep speed'); await sleep(300);
    voOk = voOk && q('[name=vo_mode]').value === 'text' && (L('Voice-over text') || {}).value === B.vo && q('[name=vo_fit]').value !== 'speed';
    log.push('vo=' + q('[name=vo_mode]').value + ' fit=' + q('[name=vo_fit]').value + ' words=' + B.vo.split(/\s+/).length);
  }
  if (B.direction) { setv(q('textarea[name=direction]'), B.direction); dirOk = q('textarea[name=direction]').value === B.direction; log.push('direction ' + (dirOk ? 'ok' : 'MISSING')); }
  setv(L('Batch name'), B.batch); await sleep(800);

  // checks, then start
  const t = document.querySelector('main').innerText;
  const lines = [1, 2, 3, 4, 5, 6].map(n => L('Line ' + n + ' text')?.value).filter(Boolean);
  log.push('lines=' + lines.length + ' brand=' + q('[name=brand]').value.slice(0, 8) + ' name=' + L('Batch name').value + ' | ' +
    t.slice(t.indexOf('Ad brief\nUsed'), t.indexOf('Ad brief\nUsed') + 40).replace(/\n/g, ' '));
  const ok = [...document.querySelectorAll('input[name=products]:checked')].length === 1 && refs[0] && refs[0].analysis &&
    refs[0].target === 'asset:' + B.poster && !refs[0].use.includes('camera') && refs[0].send && lines.length === B.lines.length &&
    q('[name=brand]').value.startsWith(B.brand) && !/claude/i.test(B.batch) && voOk && dirOk;
  log.push('READY=' + ok);
  if (ok && B.start) {
    setTimeout(() => [...document.querySelectorAll('button[type=submit]')].find(b => /^Start/.test(b.innerText.trim()) && b.offsetParent).click(), 100);
    log.push('STARTED');
  }
  return log.join(' | ');
}
