// Make a 1-day share link for the finished videos of ONE batch (one ZIP per batch, because the ZIP does not say
// which batch a file came from). Run on https://marketing-tool.nexgenbros.com/exports while signed in:
//   (<this whole file>)('<batch id>')
// Returns the /shared/exports/... link; download it with negen/download_export.sh (the browser blocks downloads).
async (batchId) => {
  const f = [...document.querySelectorAll('form')].find(x => /Export ZIP/.test(x.innerText));
  if (!f) return 'OPEN /exports FIRST';
  const fd = new FormData();
  fd.append('_csrf', f.querySelector('[name=_csrf]').value);
  fd.append('scope', 'batches'); fd.append('batch', batchId);
  fd.append('status', 'succeeded'); fd.append('kinds', 'videos');
  fd.append('background', '1'); fd.append('share', '1'); fd.append('share_days', '1');
  const r = await fetch('/exports', { method: 'POST', body: fd, credentials: 'include' });
  const html = await r.text();
  const m = html.match(/\/shared\/exports\/[A-Za-z0-9_\-]+/);
  if (m) return location.origin + m[0];
  // the link sometimes only shows on the exports page after a reload
  const again = await (await fetch('/exports', { credentials: 'include' })).text();
  const m2 = again.match(/\/shared\/exports\/[A-Za-z0-9_\-]+/);
  return m2 ? location.origin + m2[0] + '  (newest link on the page; check the label matches the batch)' : 'NO LINK: ' + r.status;
}
