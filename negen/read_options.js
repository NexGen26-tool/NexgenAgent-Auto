// read_options.js - reads the tracking sheet's own dropdown lists (owner, Nov 18: "use the options available, don't
// invent"), from the open sheet page, no sign-in (window.spread, as read_sheet.js). Load it like the other routines.
// Input: {tab: "Spry"} (default: the open tab); {row: 300} a row to read the lists from (default: the last row with a SKU).
// Output: {tab, header: [...all column names in order], options: {"Collection": [...], "Persona": [...], ...}}
// Every dropdown cell of sheet-rows.tsv must be one of these values exactly (capcut/sheet_rows.py checks it).
async ({tab, row} = {}) => {
  const sp = window.spread;
  if (!sp || !sp.sheets) return {error: "the sheet has not loaded yet: wait a few seconds and run again"};
  const name = (s) => typeof s.name === "function" ? s.name() : s.name;
  const sh = tab ? sp.sheets.find(s => name(s) === tab) : sp.sheets[sp._activeSheetIndex];
  if (!sh) return {error: "no tab named " + tab, tabs: sp.sheets.map(name)};
  const C = sh.getColumnCount(), R = sh.getRowCount();
  const text = (r, c) => { const t = sh.getText(r, c); return t == null ? "" : String(t).trim(); };
  const header = Array.from({length: C}, (_, c) => text(0, c));
  const sku = header.indexOf("SKU");
  if (sku < 0) return {error: "tab not loaded: click it, wait, run again"};
  if (!row) for (let r = R - 1; r > 0; r--) if (text(r, sku)) { row = r; break; }
  const options = {};
  for (let c = 0; c < C; c++) {
    if (!header[c]) continue;
    let v = null;
    try { v = sh.dataValidationService.getDataValidation(row, c); } catch (e) {}
    if (v && v.type === "list" && Array.isArray(v.formulas)) options[header[c]] = v.formulas.map(String);
  }
  return {tab: name(sh), row, header: header.filter(Boolean), options};
}
