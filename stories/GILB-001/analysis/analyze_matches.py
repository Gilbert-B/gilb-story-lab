#!/usr/bin/env python3
"""GILB-001 reproducible match-level analysis. Standard-library only.

Run: py -3 stories/GILB-001/analysis/analyze_matches.py
This script recomputes every headline metric from the manually transcribed
season fixture table and checks against separately reported final standings.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path
from collections import Counter

STORY = Path(__file__).resolve().parents[1]
SRC = STORY / 'data/raw/hearts_2025-26_results_transcribed.csv'
CLEAN = STORY / 'data/clean/hearts_2025-26_match_metrics.csv'
COMPARISON = STORY / 'analysis/champion_comparison.csv'
OUT = STORY / 'analysis/results.json'
BRIEF = STORY / 'analysis/research_findings.md'

def main():
    with SRC.open(encoding='utf-8-sig',newline='') as f:
        games = list(csv.DictReader(f))
    with COMPARISON.open(encoding='utf-8-sig',newline='') as f:
        teams = {r['team']:r for r in csv.DictReader(f)}
    assert len(games) == 34, f'Expected 34 matches, got {len(games)}'
    assert sorted(int(g['round']) for g in games) == list(range(1,35)), 'Non-unique or missing rounds'
    data=[]
    for g in games:
        gf=int(g['hearts_goals']); ga=int(g['opponent_goals'])
        if gf<0 or ga<0:raise ValueError('Negative goals')
        result='Win' if gf>ga else 'Draw' if gf==ga else 'Loss'
        data.append({**g,'round':int(g['round']),'hearts_goals':gf,'opponent_goals':ga,
             'result':result,'points':3 if result=='Win' else 1 if result=='Draw' else 0,
             'clean_sheet':int(ga==0),'goalless_draw':int(gf==0 and ga==0),
             'failed_to_score':int(gf==0)})
    counts=Counter(d['result'] for d in data)
    summary={
        'matches':len(data),'wins':counts['Win'],'draws':counts['Draw'],'losses':counts['Loss'],
        'goals_for':sum(d['hearts_goals'] for d in data),
        'goals_against':sum(d['opponent_goals'] for d in data),
        'points':sum(d['points'] for d in data),
        'clean_sheets':sum(d['clean_sheet'] for d in data),
        'goalless_draws':sum(d['goalless_draw'] for d in data),
        'failed_to_score':sum(d['failed_to_score'] for d in data),
        'clean_sheet_percentage':round(100*sum(d['clean_sheet'] for d in data)/len(data),1),
        'goalless_draw_share_of_all_draws_pct':round(100*sum(d['goalless_draw'] for d in data)/counts['Draw'],1),
        'scoreless_shutout_share_pct':round(100*sum(d['goalless_draw'] for d in data)/sum(d['clean_sheet'] for d in data),1),
        'wins_with_clean_sheet':sum(d['result']=='Win' and d['clean_sheet'] for d in data),
    }
    hearts=teams['Hearts of Oak']; medeama=teams['Medeama SC']
    for key,col in [('matches','matches'),('wins','wins'),('draws','draws'),('losses','losses'),('goals_for','goals_for'),('goals_against','goals_against'),('points','points')]:
        assert summary[key] == int(hearts[col]), f'RSSSF final table mismatch for {key}: {summary[key]} vs {hearts[col]}'
    assert summary['clean_sheets']==24, '24 clean sheets failed independent match recount'
    assert summary['goalless_draws']==13, '13 goalless draws failed independent match recount'
    comparison={
        'champion':'Medeama SC','medeama_points':int(medeama['points']),
        'medeama_wins':int(medeama['wins']),'medeama_draws':int(medeama['draws']),
        'medeama_losses':int(medeama['losses']),
        'points_gap_to_champion':int(medeama['points'])-summary['points'],
        'win_gap_to_champion':int(medeama['wins'])-summary['wins'],
        'draw_excess_vs_champion':summary['draws']-int(medeama['draws']),
        'goals_for_gap_to_champion':int(medeama['goals_for'])-summary['goals_for'],
        'goals_conceded_advantage':int(medeama['goals_against'])-summary['goals_against'],
    }
    assert comparison['points_gap_to_champion']==8
    assert comparison['win_gap_to_champion']==4 and comparison['draw_excess_vs_champion']==4
    assert comparison['medeama_losses']==summary['losses']==6
    CLEAN.parent.mkdir(parents=True,exist_ok=True)
    with CLEAN.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    payload={'story_id':'GILB-001','season':'2025/26','data_provenance':'Manually transcribed RSSSF round-by-round match results',
             'calculation_status':'Reproduced and cross-checked; NOT owner-approved for publication',
             'hearts':summary,'comparison':comparison,'sources':[
              'https://www.rsssf.org/tablesg/gha2026.html',
              'https://www.ghanafa.org/official-ghana-premier-league-table-after-the-end-of-the-2025-26-season',
              'https://ghanafa.org/ghana-premier-league-2025-26-statistics?amp=1',
              'https://preview.gpl.com.gh/matches?season=2025-26']}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    BRIEF.write_text(f'''# GILB-001 — Research findings (owner review required)\n\n## The candidate question\n\nHow did Hearts of Oak keep {summary['clean_sheets']} clean sheets and still finish third in Ghana's 2025/26 Premier League?\n\n## Reproduced facts\n\n- {summary['matches']} matches: **{summary['wins']} wins, {summary['draws']} draws and {summary['losses']} losses** = **{summary['points']} points**.\n- **{summary['goals_for']} goals scored, {summary['goals_against']} conceded**.\n- **{summary['clean_sheets']} team clean sheets** ({summary['clean_sheet_percentage']}% of matches).\n- **{summary['goalless_draws']} goalless draws (0–0)**, accounting for {summary['goalless_draw_share_of_all_draws_pct']}% of all draws.\n- In **{summary['goalless_draws']} of the {summary['clean_sheets']} shutouts**, Hearts also failed to score ({summary['scoreless_shutout_share_pct']}%).\n- **{summary['failed_to_score']} matches without a Hearts goal** in total.\n- **{summary['wins_with_clean_sheet']} clean-sheet wins**; remaining clean sheets ended scoreless.\n\n## Comparison with league champions Medeama\n\n- Medeama: **{comparison['medeama_wins']} wins, {comparison['medeama_draws']} draws and {comparison['medeama_losses']} losses**, **{comparison['medeama_points']} points**.\n- **Both teams lost 6 matches**. Medeama had 4 more wins and 4 fewer draws, yielding an **8-point lead**.\n- Medeama scored **52 goals**, {comparison['goals_for_gap_to_champion']} more than Hearts, while Hearts conceded 13 fewer goals.\n\n## Candidate storytelling angles (NOT approved headlines)\n\n1. **The 24 clean-sheet paradox:** Exceptional defensive record, but 13 scoreless draws.\n2. **Same losses, different champions:** Both Hearts and Medeama lost six matches; the extra four wins made the eight-point difference.\n3. **When a clean sheet wasn't enough:** More than half of Hearts' shutouts yielded only one point.\n\n## Interpretation boundaries\n\nThese are descriptive match-result findings, **not** evidence of the reasons for chance creation, individual performance or tactical decisions. Do not ascribe causes without additional data. The owner must review and explicitly approve any claim before it is published.\n\n## Reproduction\n\nRun `py -3 stories/GILB-001/analysis/analyze_matches.py` from the repository root. It validates all 34 rounds, recomputes the metrics and asserts they match the published final standings.\n\nSources and licensing notes: `stories/GILB-001/evidence/source_register.md`.\n''',encoding='utf-8')
    print('PASS: 34 matches reconcile to final standings')
    print(json.dumps({'hearts':summary,'comparison':comparison},indent=2))

if __name__=='__main__':main()
