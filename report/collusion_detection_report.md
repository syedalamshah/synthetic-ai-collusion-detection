# Synthetic AI Collusion Detection Pilot

This report is generated from the offline 40-case experiment in this
repository. The benchmark contains 20 verified coordinated harmful cases and
20 negatives (10 independent-similar, 5 independent-distinct, and 5
talk-only). The same cases are scored using messages (M), actions (A),
messages plus actions (MA), and a structured claims/outcomes audit (S).

## Method

The game and dataset use seed `20261023`. Detectors are deterministic
rule-based classifiers; no model, paid API, or nested `LLM-Trust-Breaking`
code is used. Labels remain sealed from detector views. This is a synthetic
pilot, not evidence about spontaneous LLM collusion. The existing generator's
40-case composition is used for the test run. No separate development set is
implemented, so the threshold and rules were not tuned on held-out data.

## Results (run 2026-10-26)

The actual `results/metrics.json` output is:

| View | Balanced accuracy | F1 | FPR | TP/TN/FP/FN |
|---|---:|---:|---:|---|
| M | 0.475 | 0.222 | 0.200 | 3/16/4/17 |
| A | 0.700 | 0.769 | 0.600 | 20/8/12/0 |
| MA | 0.575 | 0.261 | 0.000 | 3/20/0/17 |
| S | 0.800 | 0.750 | 0.000 | 12/20/0/8 |

S had the highest balanced accuracy in this run. A detected every positive
but also many harmful independent negatives. These are descriptive pilot
outputs, not a claim of general superiority. The machine-readable metrics and
paired disagreements are the authoritative artifacts.

## Error analysis and artifacts

The concrete error counts were:

| View | False positives (by negative subtype) | False negatives (positive) |
|---|---|---:|
| M | 4 talk-only; 0 hard-negative; 0 independent-distinct | 17 |
| A | 10 hard-negative; 2 independent-distinct; 0 talk-only | 0 |
| MA | 0 across all negative subtypes | 17 |
| S | 0 across all negative subtypes | 8 |

The generated comparison figure is
`results/figures/metrics_comparison.svg`; the error-count figure is
`results/figures/error_analysis.svg`. Supporting artifacts are
`results/dataset.jsonl`, `results/predictions_M.json`,
`results/predictions_A.json`, `results/predictions_MA.json`,
`results/predictions_S.json`, `results/metrics.json`, `results/metrics.csv`,
and `results/paired_comparison.json`. `results/experiment_log.json` records
the seed, offline status, and the fact that no development set was used.

The generator performs configuration, length, and binary-label checks, but
there is no separate independent label verifier beyond those generation
checks. Consequently, the sealed labels should be treated as scripted
provenance for this pilot rather than independently audited ground truth.

## Limitations and responsible interpretation

The sample is small, scripted, and deliberately transparent. Harmful
independent actions can be observationally similar to coordination, and
message templates can create lexical shortcuts. Rule-based thresholds are not
production monitors. Results should be interpreted as a reproducibility and
instrumentation pilot, not a claim that combined evidence generally improves
collusion detection. Do not deploy these detectors for consequential decisions.
