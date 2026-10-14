# Extended manuscript scaffold — Liquidity at Support & Resistance
Target: working paper → conference → journal. This scaffold mirrors README §§1–10 and adds PhD scaffolding.

## Title options
1. Lines Are Not Liquidity: Live Order-Book Verification of Support/Resistance Mechanics
2. Definition Fragility in Breakout Backtests: A Triple-Surface Approach
3. From Chart Line to Executable Quantity: Benchmarking Bounce vs Break on Public Crypto L2 Data

## Abstract (150–200 words)
See README §1. Expand with venue, N, and triple-surface result.

## 1. Introduction
- Retail pedagogy vs microstructure reality; research question: which lecture claims survive contact with live L2 data?
- Pre-registration: tolerance 0.2%, lookback 20, triple (close, +1%, hold-3).

## 2. Related work
- Gomes–Waelbroeck 2010; Krause et al. 2021 (two regimes); Cristelli et al. 2009 (granularity); Corradi et al. 2015 (timescales); latent-book models; CME 2025 fill-quality; Bookmap 2026 weak/strong; round-number clustering (Sonnemans 2003; Chiao–Wang 2009; Osler 2006).
- Gap: no public single-command benchmark mapping pedagogy → tests with nulls.

## 3. Data
- Coinbase L2 + 1h candles (keyless, archived with UTC stamp); Binance Vision path; venue-bias declaration; HTTP-451 note for api.binance.com from EU host.
- Ethics/ToS: public endpoints only, rate-limit respectful (3 polls × 6 s).

## 4. Methods (E01–E08)
- walk_cost simulator; swing/touch/break operators; dynamics counter; round-number uniform null; sweep proxy; triple-surface; V-event forward dispersion.
- Negative-result policy; sole-writer rule (run_all.py only).

## 5. Results
- Table from results/summary.json (paste live numbers; do not retype — quote file).
- Figures: depth_snapshot.png, closes_1h.png.

## 6. Hidden pattern: definition fragility
- Same 6 events: 100% / 0% / 33%. Implication: report surfaces, not points. Propose (δ, τ) grid 0–2% × 0–5 candles across assets/regimes.

## 7. Limitations & threats to validity
- Single venue/asset/day; snapshot staleness; hidden liquidity; small-N E08; candle-proxy touches.

## 8. Future work (PhD ladder)
1. 15m multi-asset power for E08. 2. Binance Vision replay. 3. Tardis tick-L2 cascade classifier. 4. Consolidation. 5. Live paper-trade guard (spread + fee + latency).

## References
- As §3 list + exchange docs + dataset checksums. Fill DOIs before submission.

## Appendix A. Reproduction log
- Paste `python3 src/run_all.py` output + `pytest -q` + `docker compose up research` build hash.
## Appendix B. Raw artefacts
- data/raw/*.json hashes (sha256sum).
