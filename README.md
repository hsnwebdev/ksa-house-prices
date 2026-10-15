# Saudi House Price Prediction

Predicting residential property transaction prices in Saudi Arabia from
Ministry of Justice open data, 2020–2026.

**Status:** in progress. Started 12 October 2026.

---

## The problem

<!-- One paragraph. What are you predicting, for whom, and why would
     anyone want it? Write this before you write any code. -->

## The data

- **Source:** Saudi Ministry of Justice real estate sale transactions,
  published as open data and mirrored at
  [civillizard/Saudi-Real-Estate-Data](https://github.com/civillizard/Saudi-Real-Estate-Data).
- **Licence:** KSA Open Data License. Attribution required; raw data
  redistributed unmodified.
- **Size:** 1,269,512 transactions, 23 quarterly files, 2020-01-01 to
  2026-03-31. 2021-Q1 is absent at source.
- **Not included in this repo.** Run `python build_dataset.py` to
  download and rebuild it.

See [`SCHEMA.md`](SCHEMA.md) for the column dictionary.

## Cleaning decisions

<!-- A table. Every choice you made and why. This section is the one a
     reviewer reads most carefully. Fill it in AS YOU GO, not after. -->

| Issue | Decision | Reasoning |
|---|---|---|
| | | |

## Leakage check

<!-- Paste the output of find_leaks() here, and say what you did about it. -->

## Baseline

<!-- The number the model has to beat, stated before the model exists. -->

## Model

<!-- Pipeline description. Every fitted step inside it. -->

## Validation

<!-- Which split, and one sentence saying why. Report the shuffled-KFold
     number too, with the gap. -->

## Results

| Model | Validation | Metric | Score |
|---|---|---|---|
| Baseline | | | |
| | | | |

## What this model cannot do

<!-- No bedrooms, no condition, no finish, no floor. Name the ceiling
     that imposes. Be specific. -->

## Reproducing this

```bash
git clone https://github.com/<your-username>/ksa-house-prices.git
cd ksa-house-prices
```

Then set up the environment either way — both are kept in sync.

**conda**

```bash
conda env create -f environment.yml
conda activate ksa-house
```

**pip / venv**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Then download the data and open the first notebook:

```bash
python build_dataset.py        # ~1.27M rows, downloads 23 quarterly CSVs
jupyter lab notebooks/01-profile.ipynb
```
