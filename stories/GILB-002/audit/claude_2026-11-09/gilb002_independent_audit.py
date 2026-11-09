#!/usr/bin/env python3
"""GILB-002 independent audit: rebuild the NCA series from the published PDFs.

Reads numbers from the NCA PDFs by page position. It does not read any GilB
data file until the comparison step, and no GilB value feeds the extraction.

Usage:
  python gilb002_independent_audit.py --pdf-dir DIR --repo REPO --out DIR [--pylib DIR]

Needs PyMuPDF, pandas and openpyxl. Writes only to --out.
"""
import argparse, csv, hashlib, json, re, sys, warnings
from fractions import Fraction
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--pdf-dir', required=True)
ap.add_argument('--repo', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--pylib')
a = ap.parse_args()
if a.pylib:
    sys.path.insert(0, a.pylib)
warnings.simplefilter('ignore')
import fitz  # noqa: E402
import pandas as pd  # noqa: E402

PDF = Path(a.pdf_dir); REPO = Path(a.repo); OUT = Path(a.out); OUT.mkdir(parents=True, exist_ok=True)
STORY = REPO / 'stories/GILB-002'

SOURCES = {
    'Market-Data-2023.pdf': ('https://nca.org.gh/wp-content/uploads/2025/06/Market-Data-2023.pdf', 'context only'),
    'Market-Data-2024.pdf': ('https://nca.org.gh/wp-content/uploads/2025/06/Market-Data-2024.pdf', 'S1'),
    'Data-Subscription-December-2025.pdf': ('https://nca.org.gh/wp-content/uploads/2026/02/Data-Subscription-December-2025.pdf', 'S2'),
    'Monthly-Industry-Data_July_2026-.pdf': ('https://nca.org.gh/wp-content/uploads/2026/10/Monthly-Industry-Data_July_2026-.pdf', 'S3'),
}
MON = re.compile(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(\d\d)$')
NUM = re.compile(r'^-?[\d,]+(\.\d+)?%?$')
MN = {m: i + 1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
OPS = ['MTN', 'Telecel', 'AT']


def ym(tok):
    m = MON.match(tok)
    return f'20{m.group(2)}-{MN[m.group(1)]:02d}'


def page_rows(page):
    ws = sorted(page.get_text('words'), key=lambda w: ((w[1] + w[3]) / 2, w[0]))
    rows, cur, y0 = [], [], None
    for w in ws:
        y = (w[1] + w[3]) / 2
        if y0 is None or abs(y - y0) < 2.2:
            cur.append(w); y0 = y if y0 is None else y0
        else:
            rows.append(sorted(cur, key=lambda v: v[0])); cur, y0 = [w], y
    rows.append(sorted(cur, key=lambda v: v[0]))
    return rows


def classify(label):
    if re.search(r'Airtel|^AT\b', label): return 'AT'
    if 'Telecel' in label: return 'Telecel'
    if re.search(r'Scancom|^MTN', label): return 'MTN'
    if label.startswith('TOTAL MOBILE'): return 'TOTAL'
    if label.startswith('MONTH OVER MONTH GROWTH'): return 'TOTAL_MOM'
    return None


def parse(path):
    """Return {section: {row: {month: value}}} plus verbatim labels."""
    doc = fitz.open(path)
    rows = [r for p in doc for r in page_rows(p)]
    out = {'mno': {}, 'mom': {}, 'share': {}}; labels = {}; section = None; cols = None; seen = set()
    for i, r in enumerate(rows):
        months = [(w, (w[0] + w[2]) / 2) for w in r if MON.match(w[4])]
        if len(months) >= 8:
            lab = ' '.join(w[4] for w in r if not MON.match(w[4]))
            if not lab:
                lab = ' '.join(w[4] for w in rows[i - 1]) if i else ''
            cols = [(ym(w[4]), x) for w, x in months]
            if 'MOBILE NETWORK DATA OPERATOR' in lab: sec = 'mno'
            elif 'GROWTH PER OPERATOR' in lab: sec = 'mom'
            elif 'MARKET SHARE' in lab and ('MOBILE OPERATORS' in lab or 'MNO DATA' in lab): sec = 'share'
            else: sec = None
            # First matching block only: the 2023/2024 PDFs reuse the mobile
            # share heading for the fixed-operator table.
            section = sec if sec and sec not in seen else None
            if section: seen.add(section)
            continue
        if not section: continue
        vals = [w for w in r if NUM.match(w[4])]
        lab = ' '.join(w[4] for w in r if not NUM.match(w[4]))
        key = classify(lab)
        if key is None or not vals: continue
        store = out[section].setdefault(key, {})
        for w in vals:
            x = (w[0] + w[2]) / 2
            mon, cx = min(cols, key=lambda c: abs(c[1] - x))
            assert abs(cx - x) < 30, (path, lab, w[4], x, cx)
            assert mon not in store, (path, section, key, mon)
            t = w[4].replace(',', '')
            store[mon] = float(t[:-1]) if t.endswith('%') else int(t)
        labels[(section, key)] = lab
    return out, labels, doc.metadata.get('creationDate')


def within(calc, printed):
    """True if calc rounds to the printed 2-decimal figure."""
    return abs(calc - printed) <= 0.005 + 1e-9


# ---------- extraction ----------
parsed, meta = {}, {}
for f, (url, tag) in SOURCES.items():
    raw = (PDF / f).read_bytes()
    parsed[f], labels, created = parse(PDF / f)
    meta[f] = {'url': url, 'role': tag, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
               'pdf_created': created,
               'labels': {'/'.join(k): v for k, v in labels.items() if k[0] == 'mno'}}

series, printed_total = {}, {}
dup = []
for f, p in parsed.items():
    for op in OPS:
        for m, v in p['mno'][op].items():
            if (m, op) in series and series[(m, op)][0] != v:
                dup.append(('CONFLICT', m, op, series[(m, op)], v, f))
            elif (m, op) in series:
                dup.append(('MATCH', m, op, v, f))
            else:
                series[(m, op)] = (v, f)
    for m, v in p['mno']['TOTAL'].items():
        printed_total.setdefault(m, v)

scope = [f'{y}-{mm:02d}' for y in (2024, 2025, 2026) for mm in range(1, 13) if f'{y}-{mm:02d}' <= '2026-07']
all_months = [f'2023-{mm:02d}' for mm in range(1, 13)] + scope
assert len(scope) == 31
wide = pd.DataFrame({op: {m: series[(m, op)][0] for m in all_months} for op in OPS}, dtype='int64').sort_index()
wide['TOTAL'] = wide[OPS].sum(axis=1)

checks = {'source_files': meta}
checks['operator_month_values_extracted_in_scope'] = sum((m, o) in series for m in scope for o in OPS)
checks['overlap_month_checks'] = dup

# ---------- internal consistency against the NCA's own printed figures ----------
prev = dict(zip(all_months[1:], all_months[:-1]))
sum_bad = [(m, int(wide.loc[m, 'TOTAL']), printed_total[m]) for m in all_months if wide.loc[m, 'TOTAL'] != printed_total[m]]
checks['total_rows_tested'] = len(all_months); checks['total_mismatches'] = sum_bad
checks['total_in_scope_matches'] = sum(wide.loc[m, 'TOTAL'] == printed_total[m] for m in scope)

share_bad, mom_bad, tot_bad, n_share, n_mom, n_tot = [], [], [], 0, 0, 0
for f, p in parsed.items():
    for op in OPS:
        for m, v in p['share'][op].items():
            calc = wide.loc[m, op] / wide.loc[m, 'TOTAL'] * 100; n_share += 1
            if not within(calc, v): share_bad.append((f, m, op, round(calc, 4), v))
        for m, v in p['mom'][op].items():
            if m not in prev: continue
            calc = (wide.loc[m, op] / wide.loc[prev[m], op] - 1) * 100; n_mom += 1
            if not within(calc, v): mom_bad.append((f, m, op, round(calc, 4), v))
    for m, v in p['mno']['TOTAL_MOM'].items():
        if m not in prev: continue
        calc = (wide.loc[m, 'TOTAL'] / wide.loc[prev[m], 'TOTAL'] - 1) * 100; n_tot += 1
        if not within(calc, v): tot_bad.append((f, m, round(calc, 4), v))
checks.update({'printed_share_tests': n_share, 'printed_share_mismatches': share_bad,
               'printed_op_mom_tests': n_mom, 'printed_op_mom_mismatches': mom_bad,
               'printed_total_mom_tests': n_tot, 'printed_total_mom_mismatches': tot_bad})

# ---------- second extraction engine, if its text is supplied ----------
tdir = OUT.parent / 'nca_text'
if tdir.exists():
    miss = []
    for f in SOURCES:
        tf = tdir / (f[:-4] + '.txt')
        if not tf.exists(): continue
        toks = re.findall(r'[\d,]{5,}', tf.read_text(encoding='utf-8', errors='ignore'))
        toks = {t.replace(',', '') for t in toks}
        for op in OPS + ['TOTAL']:
            for m, v in parsed[f]['mno'][op].items():
                if str(v) not in toks: miss.append((f, m, op, v))
    checks['second_engine_pdftotext_missing_tokens'] = miss

# ---------- comparison with GilB's files (first use of those files) ----------
clean = pd.read_csv(STORY / 'data/clean/GILB002_mobile_internet_operator_monthly_2024_2026-07.csv', encoding='utf-8-sig')
clean['m'] = clean['month'].str[:7]
raw = pd.read_csv(STORY / 'data/raw/GILB002_mno_source_transcription_2024_2026-07.csv', encoding='utf-8-sig')
raw['m'] = raw['month'].str[:7]
led = pd.read_csv(STORY / 'analysis/GILB002_Source_to_Clean_Comparison_93_Rows_v2.csv', encoding='utf-8-sig')
cmp_bad = {'clean': [], 'raw': [], 'ledger': [], 'clean_share': [], 'clean_url': []}
url_for = {y: u for y, u in zip(('2024', '2025', '2026'), [v[0] for k, v in SOURCES.items() if v[1] != 'context only'])}
for _, r in clean.iterrows():
    tv = wide.loc[r['m'], r['operator']]
    if int(r['subscriptions']) != tv: cmp_bad['clean'].append((r['m'], r['operator'], int(r['subscriptions']), int(tv)))
    if abs(r['market_share'] - tv / wide.loc[r['m'], 'TOTAL']) > 1e-12: cmp_bad['clean_share'].append((r['m'], r['operator']))
    if r['source_url'] != url_for[r['m'][:4]]: cmp_bad['clean_url'].append((r['m'], r['operator'], r['source_url']))
for _, r in raw.iterrows():
    for op, c in (('MTN', 'mtn'), ('Telecel', 'telecel'), ('AT', 'at')):
        if int(r[c]) != wide.loc[r['m'], op]: cmp_bad['raw'].append((r['m'], op, int(r[c])))
for _, r in led.iterrows():
    if int(r['nca_source_value']) != wide.loc[r['month'], r['operator']]: cmp_bad['ledger'].append((r['month'], r['operator']))
checks['compare_rows'] = {'clean': len(clean), 'raw_operator_values': len(raw) * 3, 'ledger': len(led)}
checks['compare_mismatches'] = cmp_bad
checks['duplicates_in_clean'] = int(clean.duplicated(['m', 'operator']).sum())
checks['nulls_in_clean_counts'] = int(clean['subscriptions'].isna().sum())

w = wide.loc[scope]
sh = w[OPS].div(w['TOTAL'], axis=0) * 100

# ---------- monthly calculations ----------
rows = []
for m in scope:
    r = {'month': m, 'total': int(wide.loc[m, 'TOTAL'])}
    p = prev.get(m); yy = f'{int(m[:4]) - 1}{m[4:]}'
    r['total_mom_abs'] = int(wide.loc[m, 'TOTAL'] - wide.loc[p, 'TOTAL'])
    r['total_mom_pct'] = (wide.loc[m, 'TOTAL'] / wide.loc[p, 'TOTAL'] - 1) * 100
    r['total_yoy_abs'] = int(wide.loc[m, 'TOTAL'] - wide.loc[yy, 'TOTAL'])
    r['total_yoy_pct'] = (wide.loc[m, 'TOTAL'] / wide.loc[yy, 'TOTAL'] - 1) * 100
    for op in OPS:
        s = wide.loc[m, op] / wide.loc[m, 'TOTAL'] * 100
        sp = wide.loc[p, op] / wide.loc[p, 'TOTAL'] * 100
        sy = wide.loc[yy, op] / wide.loc[yy, 'TOTAL'] * 100
        k = op.lower()
        r.update({f'{k}': int(wide.loc[m, op]), f'{k}_share_pct': s,
                  f'{k}_mom_abs': int(wide.loc[m, op] - wide.loc[p, op]),
                  f'{k}_mom_pct': (wide.loc[m, op] / wide.loc[p, op] - 1) * 100, f'{k}_mom_pp': s - sp,
                  f'{k}_yoy_abs': int(wide.loc[m, op] - wide.loc[yy, op]),
                  f'{k}_yoy_pct': (wide.loc[m, op] / wide.loc[yy, op] - 1) * 100, f'{k}_yoy_pp': s - sy})
    rows.append(r)
monthly = pd.DataFrame(rows); monthly.to_csv(OUT / 'audit_monthly_calculations.csv', index=False, float_format='%.6f')
pd.DataFrame([{'month': m, 'operator': o, 'subscriptions': int(wide.loc[m, o]), 'source_pdf': series[(m, o)][1],
               'in_gilb_scope': m in scope, 'nca_printed_total': printed_total[m]}
              for m in all_months for o in OPS]).to_csv(OUT / 'audit_nca_extracted_series.csv', index=False)


def window(a_, b_):
    A, B = wide.loc[a_], wide.loc[b_]
    net = int(B['TOTAL'] - A['TOTAL'])
    d = {'start': a_, 'end': b_, 'total_start': int(A['TOTAL']), 'total_end': int(B['TOTAL']), 'net_change': net,
         'total_growth_pct': (B['TOTAL'] / A['TOTAL'] - 1) * 100}
    gains = sum(max(int(B[o] - A[o]), 0) for o in OPS)
    for o in OPS:
        k = o.lower(); sa, sb = A[o] / A['TOTAL'] * 100, B[o] / B['TOTAL'] * 100; ch = int(B[o] - A[o])
        d.update({f'{k}_start': int(A[o]), f'{k}_end': int(B[o]), f'{k}_change': ch,
                  f'{k}_growth_pct': (B[o] / A[o] - 1) * 100, f'{k}_share_start': sa, f'{k}_share_end': sb,
                  f'{k}_share_pp': sb - sa, f'{k}_net_contribution_pct': ch / net * 100 if net else None,
                  f'{k}_gross_gain_share_pct': max(ch, 0) / gains * 100 if gains else None})
    return d


named = [('2024-01', '2026-07'), ('2025-12', '2026-07'), ('2025-07', '2026-07'), ('2024-01', '2024-12'),
         ('2024-12', '2025-12'), ('2025-06', '2026-07'), ('2024-05', '2026-07'), ('2024-02', '2026-07'),
         ('2023-12', '2026-07'), ('2023-01', '2026-07')]
win = pd.DataFrame([window(*x) for x in named]); win.to_csv(OUT / 'audit_windows.csv', index=False, float_format='%.6f')

# Every possible start month, ending July 2026
sweep = pd.DataFrame([window(m, '2026-07') for m in all_months[:-1]])
keep = ['start', 'net_change', 'mtn_change', 'mtn_share_start', 'mtn_share_pp', 'telecel_share_pp', 'at_share_pp',
        'at_change', 'at_growth_pct', 'mtn_net_contribution_pct', 'telecel_growth_pct', 'mtn_growth_pct']
sweep[keep].to_csv(OUT / 'audit_start_month_sweep.csv', index=False, float_format='%.4f')

# 3-month averaged endpoints
def avg_share(months, op): return float((wide.loc[months, op].sum() / wide.loc[months, 'TOTAL'].sum()) * 100)
ave = {}
for label, ms in (('Nov23-Jan24', ['2023-11', '2023-12', '2024-01']), ('Jan-Mar24', ['2024-01', '2024-02', '2024-03']),
                  ('May-Jul26', ['2026-05', '2026-06', '2026-07'])):
    ave[label] = {o: avg_share(ms, o) for o in OPS}
checks['three_month_pooled_shares'] = ave


# Turning points: reversals of at least the threshold (zigzag)
def zigzag(s, thr):
    pts = [(s.index[0], float(s.iloc[0]))]; hi = lo = pts[0]; d = 0
    for m, v in s.items():
        v = float(v)
        if d >= 0 and v > hi[1]: hi = (m, v)
        if d <= 0 and v < lo[1]: lo = (m, v)
        if d >= 0 and hi[1] - v >= thr and (d == 1 or hi[1] - lo[1] >= 0):
            if d == 1 or hi[0] != pts[-1][0]: pts.append(hi)
            d = -1; lo = (m, v)
        elif d <= 0 and v - lo[1] >= thr:
            if d == -1 or lo[0] != pts[-1][0]: pts.append(lo)
            d = 1; hi = (m, v)
    last = (s.index[-1], float(s.iloc[-1]))
    if pts[-1][0] != last[0]: pts.append(last)
    return pts


tps = {o: zigzag(sh[o], 0.5) for o in OPS}
checks['share_turning_points_min_reversal_0.5pp'] = {o: [(m, round(v, 2)) for m, v in t] for o, t in tps.items()}
checks['extremes'] = {o: {'min': [sh[o].idxmin(), round(float(sh[o].min()), 4)], 'max': [sh[o].idxmax(), round(float(sh[o].max()), 4)],
                          'count_peak': [w[o].idxmax(), int(w[o].max())], 'count_low': [w[o].idxmin(), int(w[o].min())]} for o in OPS}
checks['mtn_share_jun_jul_2025'] = [float(sh.loc['2025-06', 'MTN']), float(sh.loc['2025-07', 'MTN'])]
dsh = sh.diff().dropna()
checks['monthly_share_move_abs_pp'] = {o: {'median': round(float(dsh[o].abs().median()), 3), 'mean': round(float(dsh[o].abs().mean()), 3),
                                          'max': round(float(dsh[o].abs().max()), 3)} for o in OPS}
checks['mtn_share_months_higher_than_jul26'] = int((sh['MTN'].iloc[:-1] > sh['MTN'].iloc[-1]).sum())
checks['mtn_share_months_lower_than_jul26'] = int((sh['MTN'].iloc[:-1] < sh['MTN'].iloc[-1]).sum())
checks['largest_mom_moves'] = {o: [(m, int(v), round(float(p), 2)) for m, v, p in sorted(
    zip(monthly['month'], monthly[f'{o.lower()}_mom_abs'], monthly[f'{o.lower()}_mom_pct']), key=lambda t: -abs(t[2]))[:5]] for o in OPS}

# ---------- reproduce GilB derived outputs ----------
derived_bad = []
panel = pd.read_csv(STORY / 'analysis/GILB002_monthly_analysis_panel_v1.csv', encoding='utf-8-sig')
for _, r in panel.iterrows():
    m = r['month'][:7]
    if int(r['total_mobile']) != wide.loc[m, 'TOTAL']: derived_bad.append(('panel total', m))
    hhi = sum(float(sh.loc[m, o]) ** 2 for o in OPS)
    if abs(r['hhi'] - hhi) > 1e-6: derived_bad.append(('panel hhi', m, r['hhi'], hhi))
    for o in OPS:
        k = o.lower()
        if int(r[f'{k}_subscriptions']) != wide.loc[m, o]: derived_bad.append(('panel count', m, o))
        if abs(r[f'{k}_share_pct'] - sh.loc[m, o]) > 1e-9: derived_bad.append(('panel share', m, o))
        if m != '2024-01' and int(r[f'{k}_change_mom']) != wide.loc[m, o] - wide.loc[prev[m], o]: derived_bad.append(('panel mom', m, o))
ws = pd.read_csv(STORY / 'analysis/GILB002_window_sensitivity_v1.csv', encoding='utf-8-sig')
for _, r in ws.iterrows():
    d = window(r['window_start'][:7], r['window_end'][:7])
    pairs = [('net_change', 'net_change'), ('total_growth_pct', 'total_growth_pct')]
    for o in OPS:
        k = o.lower(); pairs += [(f'{k}_count_change', f'{k}_change'), (f'{k}_share_change_pp', f'{k}_share_pp'),
                                 (f'{k}_net_growth_contribution_pct', f'{k}_net_contribution_pct')]
    for x, y in pairs:
        if abs(float(r[x]) - float(d[y])) > 1e-6: derived_bad.append(('window', r['window_start'], x, r[x], d[y]))
vm = json.loads((STORY / 'analysis/GILB002_verified_metrics_v2.json').read_text(encoding='utf-8'))
d = window('2024-01', '2026-07')
for x, y in (('total_start', d['total_start']), ('total_end', d['total_end']), ('total_growth_abs', d['net_change']),
             ('total_growth_pct', d['total_growth_pct']), ('mtn_gain', d['mtn_change']), ('mtn_start_share', d['mtn_share_start']),
             ('mtn_end_share', d['mtn_share_end']), ('mtn_share_pp', d['mtn_share_pp']), ('telecel_gain', d['telecel_change']),
             ('telecel_growth_pct', d['telecel_growth_pct']), ('at_change', d['at_change']), ('at_growth_pct', d['at_growth_pct'])):
    if abs(float(vm[x]) - float(y)) > 1e-6: derived_bad.append(('verified_metrics', x, vm[x], y))
checks['derived_file_mismatches'] = derived_bad
checks['derived_files_tested'] = {'panel_rows': len(panel), 'window_rows': len(ws), 'verified_metric_fields': 12}
try:
    import openpyxl
    wb = openpyxl.load_workbook(STORY / 'analysis/GILB002_Analysis_Workbook_v1.xlsx', data_only=False)
    checks['workbook'] = {s.title: {'dims': s.dimensions, 'formulas': sum(1 for r in s.iter_rows() for c in r if isinstance(c.value, str) and c.value.startswith('='))} for s in wb}
except Exception as e:  # noqa: BLE001
    checks['workbook'] = repr(e)
checks['clean_csv_sha256_now'] = hashlib.sha256((STORY / 'data/clean/GILB002_mobile_internet_operator_monthly_2024_2026-07.csv').read_bytes()).hexdigest()

# ---------- challenge tests ----------
J, E = wide.loc['2024-01'], wide.loc['2026-07']
tel_cf = J['Telecel'] * E['MTN'] / J['MTN']
at_flat_total = J['TOTAL'] - J['AT'] + wide.loc['2023-12', 'AT']
up = int((dsh['MTN'] > 0).sum()); down = int((dsh['MTN'] < 0).sum())
last_above = [m for m in scope[:-1] if sh.loc[m, 'MTN'] > sh.loc['2026-07', 'MTN']]
checks['challenge'] = {
    'telecel_end_if_grown_at_mtn_rate': float(tel_cf),
    'mtn_end_share_if_telecel_grown_at_mtn_rate': float(E['MTN'] / (E['MTN'] + tel_cf + E['AT']) * 100),
    'mtn_jan24_share_if_at_held_dec23_count': float(J['MTN'] / at_flat_total * 100),
    'mtn_share_months_up': up, 'mtn_share_months_down': down,
    'months_mtn_share_above_jul26': last_above,
    'recovery_jun25_jul26_pp': {o: float(sh.loc['2026-07', o] - sh.loc['2025-06', o]) for o in OPS},
    'telecel_may24_to_jul25_pp': float(sh.loc['2025-07', 'Telecel'] - sh.loc['2024-05', 'Telecel']),
    'telecel_jun25_one_month_pp': float(dsh.loc['2025-06', 'Telecel']),
    'start_months_tested_ending_jul26': len(scope) - 1,
    'start_months_with_mtn_share_down_in_scope': [m for m in scope[:-1] if sh.loc['2026-07', 'MTN'] < sh.loc[m, 'MTN']],
    'contribution_range_all_starts_in_scope': [float(sweep[sweep.start >= '2024-01'].mtn_net_contribution_pct.min()),
                                               float(sweep[sweep.start >= '2024-01'].mtn_net_contribution_pct.max())],
    'nov25_mtn_implied_by_2026_pdf_dec25_growth': [float(wide.loc['2025-12', 'MTN'] / 1.02485), float(wide.loc['2025-12', 'MTN'] / 1.02475)],
    'nov25_total_implied_by_2026_pdf_dec25_growth': [float(wide.loc['2025-12', 'TOTAL'] / 1.01785), float(wide.loc['2025-12', 'TOTAL'] / 1.01775)],
    'nov25_published': [int(wide.loc['2025-11', 'MTN']), int(wide.loc['2025-11', 'TOTAL'])],
    'mom_mixed_sign_months_total': int((monthly['total_mom_abs'] < 0).sum()),
}
print('challenge:', json.dumps(checks['challenge'], default=str))
(OUT / 'audit_checks.json').write_text(json.dumps(checks, indent=1, default=str), encoding='utf-8')

# ---------- console summary ----------
def show(k): print(f'{k}:', json.dumps(checks[k], default=str)[:900])
print('in-scope values', checks['operator_month_values_extracted_in_scope'])
for k in ('total_mismatches', 'total_in_scope_matches', 'printed_share_tests', 'printed_share_mismatches', 'printed_op_mom_tests',
          'printed_op_mom_mismatches', 'printed_total_mom_tests', 'printed_total_mom_mismatches', 'second_engine_pdftotext_missing_tokens',
          'compare_rows', 'compare_mismatches', 'duplicates_in_clean', 'nulls_in_clean_counts', 'derived_file_mismatches', 'derived_files_tested',
          'workbook', 'clean_csv_sha256_now', 'extremes', 'mtn_share_jun_jul_2025', 'monthly_share_move_abs_pp', 'mtn_share_months_higher_than_jul26',
          'mtn_share_months_lower_than_jul26', 'share_turning_points_min_reversal_0.5pp', 'three_month_pooled_shares', 'largest_mom_moves'):
    if k in checks: show(k)
print('overlap checks', [x for x in dup if x[0] == 'CONFLICT'], sum(x[0] == 'MATCH' for x in dup))
for f, v in meta.items(): print(f, v['labels'])
pd.set_option('display.width', 260, 'display.max_columns', 60, 'display.float_format', '{:.2f}'.format)
print(win[['start', 'end', 'net_change', 'total_growth_pct', 'mtn_change', 'mtn_growth_pct', 'mtn_share_start', 'mtn_share_end', 'mtn_share_pp', 'mtn_net_contribution_pct', 'mtn_gross_gain_share_pct']].to_string())
print(win[['start', 'end', 'telecel_change', 'telecel_growth_pct', 'telecel_share_start', 'telecel_share_end', 'telecel_share_pp', 'telecel_net_contribution_pct', 'at_change', 'at_growth_pct', 'at_share_start', 'at_share_end', 'at_share_pp', 'at_net_contribution_pct']].to_string())
print(sweep[['start', 'mtn_share_start', 'mtn_share_pp', 'mtn_change', 'mtn_net_contribution_pct', 'at_share_pp', 'at_change']].to_string())
print(sh.round(2).assign(tot=w['TOTAL']).to_string())
