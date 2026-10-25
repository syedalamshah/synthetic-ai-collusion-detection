# Synthetic AI-Collusion Detection Pilot

This repository contains the Apart Research AI Collusion Research Sprint
project **“Comparing Message and Action Evidence for Synthetic AI-Collusion
Detection.”** It evaluates whether messages, actions, or both provide useful
evidence for detecting harmful coordinated behavior in a controlled,
synthetic two-agent resource-allocation game.

## Research question

Does combining what agents say with what they do improve detection of harmful
coordinated execution over messages or actions alone?

## Experimental design

The benchmark contains 40 deterministic three-round trajectories generated
with master seed `20261023`:

- 20 scripted positive cases with coordinated harmful execution
- 10 hard negatives with independent but similar harmful actions
- 5 independent negatives with distinct behavior
- 5 talk-only negatives with coordination-like discussion but no harmful execution

Four transparent, deterministic rule-based evidence conditions are evaluated
on the same cases:

| View | Evidence available |
|---|---|
| **M** | Agent messages only |
| **A** | Actions and outcomes only |
| **MA** | Messages plus actions and outcomes |
| **S** | Structured audit fields recording claims, actions, coordination, excess, and rejection |

The final S classifier uses aggregate coordination, excess, and rejection
signals; recorded claim/action alignment fields are available for auditing but
are not required by its binary decision rule.

## Results

Balanced accuracy from the saved canonical artifacts is:

| View | Balanced accuracy | F1 | FPR | TP/TN/FP/FN |
|---|---:|---:|---:|---|
| M | 0.475 | 0.222 | 0.200 | 3/16/4/17 |
| A | 0.700 | 0.769 | 0.600 | 20/8/12/0 |
| MA | 0.575 | 0.261 | 0.000 | 3/20/0/17 |
| S | 0.800 | 0.750 | 0.000 | 12/20/0/8 |

These are descriptive results from a 40-case synthetic, rule-based pilot.
They do not establish real-world generalization, spontaneous LLM collusion
detection, or production monitoring performance. Labels are scripted
provenance and were not independently verified by a separate label verifier.
Only one master seed was evaluated; same-seed reruns demonstrate deterministic
replay, not across-seed variance or uncertainty. The 20 positive cases are
part of the main benchmark, not a separate positive-control experiment.

## Reproducibility

The implementation uses Python's standard library for the experiment and
`pytest` for tests. No language-model calls or paid APIs are required.

From the repository root:

```text
python -m pytest tests/test_experiment.py -q
python -m src.run_experiment --output-dir results
```

The canonical machine-readable artifacts are:

- `results/dataset.jsonl`
- `results/predictions_M.json`
- `results/predictions_A.json`
- `results/predictions_MA.json`
- `results/predictions_S.json`
- `results/metrics.json`
- `results/metrics.csv`
- `results/paired_comparison.json`
- `results/experiment_log.json`

The report source and submission files are in `report/`, including
`final_submission.md`, `final_submission.pdf`, and the CSS/HTML used to build
the PDF.

## Repository structure

```text
src/                         Simulator, generator, views, detectors, metrics
tests/                       Focused experiment tests
results/                     Canonical dataset, predictions, metrics, provenance
report/                      Research report source and final submission
RESEARCH_DESIGN.md           Research design and scope
DECISION_LOG.md              Design decisions and project history
TEAM_HANDOFF.md              Handoff documentation
```

## Reference material and attribution

The local `LLM-Trust-Breaking` directory is a pre-existing external reference
repository about strategic deception and trust dynamics. It was inspected for
context only, was not used as collusion data, and was not used to generate the
results in this repository. It is excluded by the root `.gitignore`; its
original repository is available at:

<https://github.com/Jerick-1380/LLM-Trust-Breaking>

The final report records the Apart Research sprint citation, the related
research citation, the template-access limitation, and the distinction
between this project and the reference repository.

## License and publication note

This is a research prototype for the Apart Research sprint. Before publishing,
review the report, attribution, and any desired license with the project
organizers. The root workspace is intentionally prepared here but has not
been connected to or pushed to a GitHub repository.
