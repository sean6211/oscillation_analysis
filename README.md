# Oscillation analysis

Within-person 24 h tests for blood aging-clock predictions. Predictions are calculated with Biolearn 0.9.1 before these scripts are run.

A scores file has the columns `participant`, `time`, `condition`, `clock`, and `value`. `time` is in hours. Add `cohort` to keep series separate. Leukocyte fractions are columns named `cell_*`. `compartment` marks mixed blood, purified neutrophils, or mononuclear cells.

Gene contributions use `participant`, `time`, `gene`, and `contribution`. Call the full Peters score `score`. Module scores use `participant`, `time`, `module`, and `value`.

The expression and methylation matrices are not in this repository.

- Ämmälä leukocytes, OSF qx7w3
- Nilsson whole blood, E-MTAB-4664
- Oh neutrophils, GSE83944
- Koncevičius neutrophils, GSE247193 and GSE247195
- Neutrophil-depleted remainder, GSE247197
- Jiang mononuclear cells, GSE56553
- Braun whole-blood RNA, GSE113883
- Arnardottir whole-blood RNA, GSE56931
- Möller-Levet leukocytes, GSE39445
- Archer 2014 leukocytes, GSE48113
- Archer 2024 whole blood, GSE253864
- Kervezee mononuclear-cell RNA, GSE107537
- Manella whole-blood RNA, GSE196728
- Depner plasma SomaScan, Figshare 5752650

From this directory:

```text
python analysis/epigenetic_rhythm.py scores.csv epigenetic_rhythm.csv
python analysis/transcriptomic_rhythm.py scores.csv transcriptomic_rhythm.csv
python analysis/proteomic_clock.py scores.csv proteomic_clock.csv
python analysis/intervention_and_time.py scores.csv contrasts.csv --intervention tsd --control baseline --day 12 --night 0
python analysis/leukocyte_composition.py scores.csv cell_composition.csv
python analysis/leukocyte_composition.py jiang.csv jiang_times.csv --timepoints 0,6,30
python analysis/transcriptomic_drivers.py contributions.csv drivers.csv
```

The rhythm test shuffles sampling time within participant (499 permutations, seed 1). Peak-to-trough is twice the amplitude. q values are Benjamini-Hochberg across clocks.
