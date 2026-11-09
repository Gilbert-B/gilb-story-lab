# GILB-001 — Research findings (owner review required)

## The candidate question

How did Hearts of Oak keep 24 clean sheets and still finish third in Ghana's 2025/26 Premier League?

## Reproduced facts

- 34 matches: **13 wins, 15 draws and 6 losses** = **54 points**.
- **25 goals scored, 15 conceded**.
- **24 team clean sheets** (70.6% of matches).
- **13 goalless draws (0–0)**, accounting for 86.7% of all draws.
- In **13 of the 24 shutouts**, Hearts also failed to score (54.2%).
- **18 matches without a Hearts goal** in total.
- **11 clean-sheet wins**; remaining clean sheets ended scoreless.

## Comparison with league champions Medeama

- Medeama: **17 wins, 11 draws and 6 losses**, **62 points**.
- **Both teams lost 6 matches**. Medeama had 4 more wins and 4 fewer draws, yielding an **8-point lead**.
- Medeama scored **52 goals**, 27 more than Hearts, while Hearts conceded 13 fewer goals.

## Candidate storytelling angles (NOT approved headlines)

1. **The 24 clean-sheet paradox:** Exceptional defensive record, but 13 scoreless draws.
2. **Same losses, different champions:** Both Hearts and Medeama lost six matches; the extra four wins made the eight-point difference.
3. **When a clean sheet wasn't enough:** More than half of Hearts' shutouts yielded only one point.

## Interpretation boundaries

These are descriptive match-result findings, **not** evidence of the reasons for chance creation, individual performance or tactical decisions. Do not ascribe causes without additional data. The owner must review and explicitly approve any claim before it is published.

## Reproduction

Run `py -3 stories/GILB-001/analysis/analyze_matches.py` from the repository root. It validates all 34 rounds, recomputes the metrics and asserts they match the published final standings.

Sources and licensing notes: `stories/GILB-001/evidence/source_register.md`.
