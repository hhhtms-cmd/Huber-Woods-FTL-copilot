# Huber Woods — FTL Smart Dispatch Co-pilot

Prototype v1.1 · 2026-11-15

## Changelog — v1.1 (code-review fixes)
- Escape carrier names with `escapeHTML()` before rendering (`rankOut` and the carrier table) — closes the self-XSS path Gemini flagged.
- `rankCarriers()` returns `[]` early on an empty carrier list, and the UI shows "add at least one carrier" instead of a blank result. (Verified: the v1 empty case already returned `[]` with no NaN; this makes it explicit.)
- Rate check rejects a historical average ≤ 0 with a plain-language message instead of showing Infinity%. A quote ≤ 0 now falls back to price competitiveness 1.0 instead of Infinity.
- Default ranking unchanged: B 59.8, A 45.0, C 43.54.

A co-pilot, not a black box, for FTL point-to-point shippers who dispatch on Wed/Thu and fine-tune on Friday. The dispatcher keeps the final decision.

## What it does

1. **Data Guardrail** — flags a new rate that deviates from the historical average by more than 15% (adjustable).
2. **Acceptance Prediction** — history + price competitiveness − 5% on peak dispatch days, clipped to 5%–99%.
3. **Carrier Ranking** — `Total = w1·Cost + w2·Commitment + w3·Acceptance`, ×100. Default weights: 40% / 30% / 30%.

## Verified demo result (default weights, market avg $1,020)

| Rank | Carrier | Score | Quote | Predicted acceptance |
|---:|---|---:|---:|---:|
| 1 | Carrier B (low-price) | 59.8 | $980 | 56% ⚠️ |
| 2 | Carrier A (established) | 45.0 | $1,050 | 90% |
| 3 | Carrier C (balanced) | 43.54 | $1,020 | 83% |

Note: B ranks #1 on price, but its 56% acceptance is flagged in the UI — the dispatcher can still pick A. That is the intended behaviour: cheapest is not automatically best.

Rate check demo: $1,450 vs $1,000 average = 45.0% deviation → alert.

## Files

- `index.html` — trilingual UI (English / Español / 中文), JavaScript port of the same formulas. No server, no data leaves the browser.
- `algorithm.py` — original Python algorithm (exact code as supplied).

## Run locally

Open `index.html` in a browser, or run `python3 algorithm.py`.

## Entry-point recommendation

Start with **Module 1, the contract/rate check**. It is the lightest, least disruptive cut-in: it runs in the background, changes no dispatch habit, and fixes the root cause (dirty data → invoice and allocation disputes). Module 3, the Wed/Thu co-pilot ranking, is the visible win to add second, once dispatchers trust the scores.
