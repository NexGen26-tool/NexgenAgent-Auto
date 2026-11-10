// read_sheet.js - reads the tracking sheet "Source Video chạy Ads v2" (brand/brands.json "assign_sheet") in the browser,
// with no sign-in: the sheet is shared for viewing, draws its cells on a canvas and blocks copy, so this reads the
// cells from the page's own sheet model (window.spread), the same text the grid shows.
// Run it on the sheet page once it has loaded. A tab that has not been opened yet may come back empty: click that tab
// once, wait a few seconds, run again.
// Input: {tab: "Spry"} the tab name (default: the open tab); {months: ["Tháng 11/2026", ...]} keeps only those months
//        (all rows when left out); {columns: [...]} the header names to return (default below).
// Output: {tab, header, rows: [[...], ...], total, missing} with one row per sheet row that has a SKU.
async ({tab, months, columns} = {}) => {
  columns = columns || ["Tháng", "Assigned", "Collection", "SKU", "Persona", "Angle", "Hook type",
                        "Trạng thái video", "Trạng thái Ads"];
  const sp = window.spread;
  if (!sp || !sp.sheets) return {error: "the sheet has not loaded yet: wait a few seconds and run again"};
  const name = (s) => typeof s.name === "function" ? s.name() : s.name;
  const sh = tab ? sp.sheets.find(s => name(s) === tab) : sp.sheets[sp._activeSheetIndex];
  if (!sh) return {error: "no tab named " + tab, tabs: sp.sheets.map(name)};
  const R = sh.getRowCount(), C = sh.getColumnCount();
  const text = (r, c) => { const t = sh.getText(r, c); return t == null ? "" : String(t).trim(); };
  const header = Array.from({length: C}, (_, c) => text(0, c));
  const col = columns.map(h => header.indexOf(h));
  const sku = header.indexOf("SKU"), month = header.indexOf("Tháng");
  if (sku < 0) return {error: "tab " + name(sh) + " has no SKU column yet (not loaded?): click the tab, wait, run again",
                       header: header.filter(Boolean)};
  const rows = [];
  for (let r = 1; r < R; r++) {
    if (!text(r, sku)) continue;
    if (months && !months.includes(text(r, month))) continue;
    rows.push(col.map(c => c < 0 ? "" : text(r, c)));
  }
  return {tab: name(sh), header: columns, missing: columns.filter((h, i) => col[i] < 0), rows, total: R - 1};
}
