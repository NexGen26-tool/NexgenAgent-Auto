// revoice.js - a new voice-over for one video of a batch, in the voice that matches the person on screen (owner,
// Nov 18: a woman on screen gets a woman's voice). Run on /generate/<batch id>/review. Costs one voice-over (~$0.01).
// Input: {size: <the video's file size in bytes, to find which of the batch's videos>, text: "<script>", voice: "Dawn"}
// Output: "MADE ..." or what went wrong. Then export and download the batch again (export_batch.js, download_export.py).
async ({size, text, voice}) => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const btns = () => [...document.querySelectorAll('button')].filter(b => b.offsetParent);
  const lab = b => (b.getAttribute('aria-label') || b.innerText).trim();
  await sleep(2500);
  const chips = () => [...document.querySelectorAll('main *')].filter(x => x.offsetParent && x.tagName === 'SPAN' && x.children.length === 2 && (x.textContent || '').trim() === 'Video');
  for (let page = 0; page < 3; page++) {
    const n = chips().length;
    for (let i = 0; i < n; i++) {
      chips()[i].click(); await sleep(4500);
      let sz = '';
      for (const s of [...document.querySelectorAll('video')].map(x => x.currentSrc || x.src).filter(Boolean)) sz = (await fetch(s, {method: 'HEAD'})).headers.get('content-length');
      if (String(sz) !== String(size)) { btns().find(b => lab(b) === 'Close')?.click(); await sleep(1500); continue; }
      btns().find(b => /^New voice-over for video v1/.test(lab(b)))?.click(); await sleep(2500);
      const pick = btns().filter(b => /^(Evan|Dawn|Jessica|Sarah|Wren)/.test(b.innerText.trim()) && /▾|▴/.test(b.innerText)).sort((a, b) => a.innerText.length - b.innerText.length)[0];
      if (!pick) return 'NO VOICE PICKER';
      if (!pick.innerText.trim().startsWith(voice + ' ')) {
        pick.click(); await sleep(1200);
        const opt = btns().find(b => b.innerText.trim().startsWith(voice + ' - ') && !/▾|▴/.test(b.innerText));
        if (!opt) return 'NO VOICE ' + voice; opt.click(); await sleep(1200);
      }
      const ta = [...document.querySelectorAll('textarea')].find(t => t.offsetParent && t.getAttribute('aria-label') === 'Voice-over text');
      if (!ta) return 'NO TEXTAREA';
      Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(ta, text);
      ta.dispatchEvent(new Event('input', {bubbles: true})); ta.dispatchEvent(new Event('change', {bubbles: true})); await sleep(1500);
      const t = document.body.innerText;
      const info = [(t.match(/Voice\*[\s\S]{0,40}/) || [''])[0].replace(/\s+/g, ' '), (t.match(/English · [^\n]+/) || [''])[0], (t.match(/Advanced · [^\n]+/) || [''])[0]];
      if (!(info[0].includes(voice) && /Keep speed/.test(info[2]) && ta.value === text)) return 'NOT OK ' + JSON.stringify(info);
      btns().find(b => /^Make voice-over ·/.test(b.innerText.trim())).click(); await sleep(6000);
      return 'MADE ' + JSON.stringify(info);
    }
    const nx = btns().filter(b => lab(b) === 'Next'); if (!nx.length) break; nx[0].click(); await sleep(2500);
  }
  return 'SIZE NOT FOUND';
}
