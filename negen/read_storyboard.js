// Read ONE product's storyboard (angle, 8 shots with JOB and DIRECT, both VO parts) and its poster media id.
// Run on the storyboard batch's Review page while signed in:
//   https://marketing-tool.nexgenbros.com/generate/<storyboard batch id>/review   then   (<this whole file>)('<pid>')
// Call it once per product; reload the Review page (navigate to it again) before the next product.
// Returns JSON {pid, angle, poster, text}; text has one line per shot and per voice-over part.
async (pid) => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const a = document.querySelector('main a[href="/products/' + pid + '"]');
  if (!a) return 'PRODUCT ' + pid + ' NOT ON THIS PAGE: open /generate/<storyboard batch id>/review first';
  let card = a;
  for (let k = 0; k < 10 && card && !/\d+ shots/.test(card.innerText); k++) card = card.parentElement;
  const open = card && [...card.querySelectorAll('button,[role=button],a')].find(x => x.innerText.trim().startsWith('Product Storyboard'));
  if (!open) return 'NO STORYBOARD BUTTON for ' + pid + ' (storyboard not finished yet?)';
  a.scrollIntoView({ block: 'start' }); open.click();
  let box = null;
  for (let t = 0; t < 20 && !box; t++) {  // the storyboard opens in a panel; wait up to 10 s
    await sleep(500);
    box = [...document.querySelectorAll('*')].filter(e => /Storyboard \d+ of \d+/.test(e.textContent)
      && e.textContent.includes('Voice-over · Part B')).pop();  // the innermost element holding the whole storyboard
  }
  if (!box) return 'STORYBOARD PANEL DID NOT OPEN for ' + pid;
  const raw = box.textContent;
  const angle = ((raw.match(/(?:Pending|Approved|Rejected)(.*?)\d+ shots/) || [])[1] || '').trim();
  const text = raw.replace(/\s+\n/g, '\n').replace(/(A0\d|B0\d|Voice-over · Part [AB])/g, '\n$1').replace(/(Job|Direct)(?=[A-Z])/g, '\n  $1: ').trim();
  const tab = [...document.querySelectorAll('button,[role=tab]')].find(x => x.innerText.trim() === 'Poster' && x.offsetParent);
  let poster = '';
  if (tab) {
    tab.click();
    for (let t = 0; t < 10 && !poster; t++) {
      await sleep(400);
      const img = [...document.querySelectorAll('img')].find(i => i.offsetParent && i.src.includes('/media/') && /poster/i.test(i.alt || ''));
      if (img) poster = img.src.split('/media/')[1].split('/')[0];
    }
  }
  return JSON.stringify({ pid, angle, poster: poster || 'NOT FOUND: click the Poster tab and read the /media/<id>/ image', text });
}
