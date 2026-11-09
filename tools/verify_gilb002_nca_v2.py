import csv, json, hashlib, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = ROOT / 'stories/GILB-002/data/clean/GILB002_mobile_internet_operator_monthly_2024_2026-07.csv'
with p.open(encoding='utf-8-sig') as f: data=list(csv.DictReader(f))
lookup={(r['month'][:7],r['operator']):int(r['subscriptions']) for r in data}
# Independently copied from the NCA primary report tables viewed 2026-11-08.
nca={
'2024':{
 'AT':[1210156,1458524,1629526,1664891,1691720,1637270,1609444,1600596,1603100,1623822,1623999,1609235],
 'Telecel':[3063868,3130447,3120886,3124768,3119688,3181152,3301104,3467123,3645955,3776295,3863804,3892046],
 'MTN':[18973091,18760199,19601366,19779359,20020650,19890327,20095630,20203321,20311829,20418251,20282122,20626311],
 'TOTAL':[23247115,23349170,24351778,24569018,24832058,24708749,25006178,25271040,25560884,25818368,25769925,26127592]},
'2025':{
 'AT':[1602482,1609022,1614387,1621255,1626394,1627592,1607209,1586005,1557850,1533007,1474831,1301794],
 'Telecel':[3922328,3976378,3983835,4031038,4049242,4434780,4514459,4234617,4517633,4366697,4407203,4528907],
 'MTN':[20694172,20480694,21118921,21112593,21076408,21184896,21400505,21665206,21958090,22339796,22344100,22867689],
 'TOTAL':[26218982,26066094,26717143,26764886,26752044,27247268,27522173,27485828,28033573,28239500,28226134,28698390]},
'2026':{
 'AT':[1368441,1337762,1291576,1256771,1239992,1221060,1194237],
 'Telecel':[4577900,4602125,4617656,4637221,4770900,4850533,4959805],
 'MTN':[22339808,23103208,23818235,24057865,24284686,24444118,24646152],
 'TOTAL':[28286149,29043095,29727467,29951857,30295578,30515711,30800194]}
}
rows=[]; mismatch=[]; totals=[]
for y, r in nca.items():
 for i in range(len(r['MTN'])):
  m=f'{y}-{i+1:02d}'
  vals=[r[o][i] for o in ('MTN','Telecel','AT')]
  assert sum(vals)==r['TOTAL'][i],(m,vals,r['TOTAL'][i])
  for o in ('MTN','Telecel','AT'):
   ours=lookup.get((m,o)); ref=r[o][i]
   status='PASS' if ours==ref else 'MISMATCH'
   rows.append({'month':m,'operator':o,'nca_source_value':ref,'gilb_clean_value':ours,'difference':None if ours is None else ours-ref,'status':status,'nca_document':{'2024':'Market-Data-2024.pdf','2025':'Data-Subscription-December-2025.pdf','2026':'Monthly-Industry-Data_July_2026-.pdf'}[y]})
   if status!='PASS': mismatch.append((m,o,ours,ref))
  totals.append((m,r['TOTAL'][i]))
print('RECORDS',len(data),'SOURCE VALUES',len(rows),'MISMATCH',len(mismatch),mismatch[:30]);
if len(data)!=93 or len(rows)!=93 or mismatch: raise SystemExit('FAIL: primary-source mismatch')
print('TOTAL mismatches',[(m,sum(lookup[(m,o)] for o in ('MTN','Telecel','AT'))-t) for m,t in totals if sum(lookup[(m,o)] for o in ('MTN','Telecel','AT'))!=t]);
print('DATES',len(set(x['month'] for x in rows)), 'SHA256',hashlib.sha256(p.read_bytes()).hexdigest())
for op in ['MTN','Telecel','AT']:
 a=lookup[('2024-01',op)];b=lookup[('2026-07',op)];print(op,a,b,'net',b-a,'percent',100*(b/a-1),'sharepp',100*(b/30800194-a/23247115))
print('MTN jun 2025 share',lookup[('2025-06','MTN')]/sum(lookup[('2025-06',o)] for o in ('MTN','Telecel','AT')))
print('MTN min share',min(((m,lookup[(m,'MTN')]/total) for m,total in totals),key=lambda a:a[1]))
print('AT peak',max(((m,lookup[(m,'AT')]) for m,total in totals),key=lambda x:x[1]))
with (ROOT / 'stories/GILB-002/analysis/GILB002_Source_to_Clean_Comparison_93_Rows_v2.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with (ROOT / 'stories/GILB-002/analysis/GILB002_source_audit_metrics_v2.json').open('w') as f:json.dump({'source_value_checks':len(rows),'mismatches':mismatch,'totals':len(totals),'original_csv_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dates':list(sorted(set(x['month'] for x in rows)))},f,indent=2)
