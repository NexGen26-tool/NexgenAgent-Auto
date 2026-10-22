// One line per batch on the Batches page: name, state and step counts. Run on
// https://marketing-tool.nexgenbros.com/generate :  (<this whole file>)('Oct27 - ')   // name prefix to filter
(prefix) => {
  const t = document.querySelector('main').innerText;
  const banner = t.split('\nBatches')[0].trim();
  // a batch row starts with its name, then a line like "You · 21 min ago ·" or "Admin · 2 h ago ·"
  const rows = t.split(/\n(?=[^\n]+\n[^\n·]{1,40} · [^\n]*ago)/).filter(x => !prefix || x.startsWith(prefix)).map(x => {
    const one = x.replace(/\s+/g, ' ');
    const state = (one.match(/\b(Running|Paused|Queued|Failed|Done|Cancelled)\b/) || ['?'])[0];
    const steps = (one.match(/(Brief|Image|AI check|Script|Parts|Merge|VO script|Voice-over|Video) \d+\/\d+/g) || []).join(' > ');
    const why = (x.match(/Paused: [^\n]+/) || [''])[0];
    return x.split('\n')[0].trim() + ' | ' + state + ' | ' + steps + (why ? ' | ' + why : '');
  });
  const names = rows.map(r => r.split(' | ')[0]);
  const links = [...document.querySelectorAll('a[href*="/generate/"]')];
  const ids = names.map(n => [n, (links.find(a => a.textContent.trim().startsWith(n)) || { getAttribute: () => '//?' }).getAttribute('href').split('/')[2]]);
  return [banner, ...rows, 'IDS: ' + JSON.stringify(ids)].join('\n');
}
