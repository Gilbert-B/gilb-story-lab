#!/usr/bin/env python3
"""Reproduce GILB-003 calculations from the dated Bank of Ghana transcription.
Source: https://www.bog.gov.gh/wp-content/uploads/2026/09/Summary-of-Economic-and-Financial-Data-September-2026.pdf
Printed page 13, Table 11. Source values rounded at publication; not underlying unrounded counts.
"""
from pathlib import Path
import csv, json
BASE = Path(__file__).resolve().parents[1]
SRC = BASE/'data'/'raw'/'GILB-003_BoG_Table11_2025-08_to_2026-08.csv'
OUT = BASE/'analysis'/'GILB-003_computed_metrics.json'

def main():
    with SRC.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows)==13
    assert [r['month'] for r in rows]==['2025-08','2025-09','2025-10','2025-11','2025-12','2026-01','2026-02','2026-03','2026-04','2026-05','2026-06','2026-07','2026-08']
    for r in rows:
        for k in ('registered_accounts_millions','active_accounts_millions','number_of_transactions_millions','value_of_transactions_billion_GHS'):
            r[k]=float(r[k])
        assert 0 <= r['active_accounts_millions'] <= r['registered_accounts_millions']
    aug25, aug26 = rows[0], rows[-1]
    def calc(r):
        a=r['active_accounts_millions']; reg=r['registered_accounts_millions']
        return {'registered_millions':reg,'active_millions':a,'not_active_millions':round(reg-a,4),
                'active_percent':round(100*a/reg,4),'not_active_percent':round(100*(reg-a)/reg,4)}
    b=calc(aug25); n=calc(aug26)
    data={'source_pdf':'https://www.bog.gov.gh/wp-content/uploads/2026/09/Summary-of-Economic-and-Financial-Data-September-2026.pdf',
          'source_table':'Printed page 13, Table 11, Mobile Money (MM) Data, official published rounded values',
          'observations':len(rows),
          'aug_2025':b,'aug_2026':n,
          'change_2025_08_to_2026_08':{
              'registered_accounts_millions':round(n['registered_millions']-b['registered_millions'],4),
              'active_accounts_millions':round(n['active_millions']-b['active_millions'],4),
              'not_active_accounts_millions':round(n['not_active_millions']-b['not_active_millions'],4),
              'active_share_percentage_points':round(n['active_percent']-b['active_percent'],4),
              'registered_percent_growth':round(100*(n['registered_millions']/b['registered_millions']-1),4),
              'active_percent_growth':round(100*(n['active_millions']/b['active_millions']-1),4)},
          'aug_2026_transactions_millions':aug26['number_of_transactions_millions'],
          'aug_2026_transaction_value_billion_GHS':aug26['value_of_transactions_billion_GHS'],
          'limitations':['90-day rolling active definition; not monthly unique people',
                         'Accounts are not individuals','One BoG release, not multiple-release reconciliation',
                         'Values are rounded in millions and billions','Data subject to revision']}
    # independent arithmetic assertions
    assert round(n['not_active_millions'],1)==59.4
    assert round(n['active_percent'],1)==30.8
    assert round(n['not_active_percent'],1)==69.2
    assert round(data['change_2025_08_to_2026_08']['not_active_accounts_millions'],1)==6.8
    OUT.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(data,indent=2))
if __name__=='__main__': main()
