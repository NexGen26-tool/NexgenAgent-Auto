// One line per batch on the Batches page: name, state and step counts. Run on
// https://marketing-tool.nexgenbros.com/generate :  (<this whole file>)('Oct27 - ')   // name prefix to filter
(prefix) => {
  const t = document.querySelector('main').innerText;
  const banner = t.split('\nBatches')[0].trim();
  // a batch row starts with its name, then a line like "You · 21 min ago ·", "Admin · 2 h ago ·" or "You · just now ·"
  const rows = t.split(/\n(?=[^\n]+\n[^\n·]{1,40} · [^\n]*(?:ago|just now))/).filter(x => !prefix || x.startsWith(prefix)).map(x => {
    const one = x.replace(/\s+/g, ' ');
    const state = (one.match(/\b(Running|Paused|Queued|Failed|Done|Cancelled)\b/) || ['?'])[0];
    const steps = (one.match(/(Brief|Image|AI check|Script|Parts|Merge|VO script|Voice-over|Video) \d+\/\d+/g) || []).join(' > ');
    const why = (x.match(/Paused: [^\n]+/) || [''])[0];
    return x.split('\n')[0].trim() + ' | ' + state + ' | ' + steps + (why ? ' | ' + why : '');
  });
  // rows and links come in the same (newest first) order, so batches that share a name still get their own id
  const links = [...new Set([...document.querySelectorAll('a[href*="/generate/"]')].filter(a => !prefix || a.textContent.trim().startsWith(prefix))
    .map(a => a.getAttribute('href').split('/')[2]))];
  const ids = rows.map((r, i) => [r.split(' | ')[0], links[i] || '?']);
  return [banner, ...rows, 'IDS: ' + JSON.stringify(ids)].join('\n');
}
