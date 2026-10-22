// One line per batch on the Batches page: name, state and step counts. Run on
// https://marketing-tool.nexgenbros.com/generate :  (<this whole file>)('Oct27 - ')   // name prefix to filter
(prefix) => {
  const t = document.querySelector('main').innerText;
  const banner = t.split('\nBatches')[0].trim();
  const rows = t.split(/\n(?=[^\n]+\nYou · )/).filter(x => !prefix || x.startsWith(prefix)).map(x => {
    const one = x.replace(/\s+/g, ' ');
    const state = (one.match(/\b(Running|Paused|Queued|Failed|Done|Cancelled)\b/) || ['?'])[0];
    const steps = (one.match(/(Brief|Image|AI check|Script|Parts|Merge|VO script|Voice-over|Video) \d+\/\d+/g) || []).join(' > ');
    const why = (one.match(/Paused: [^›]+?(?= [A-Z][a-z]+ ·|$)/) || [''])[0];
    return one.split(' You · ')[0] + ' | ' + state + ' | ' + steps + (why ? ' | ' + why : '');
  });
  const links = [...document.querySelectorAll('a[href*="/generate/"]')].map(a => [a.textContent.trim().split('You ·')[0].trim(), a.getAttribute('href').split('/')[2]]);
  return [banner, ...rows, 'IDS: ' + JSON.stringify(links.filter(l => !prefix || l[0].startsWith(prefix)))].join('\n');
}
