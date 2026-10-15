"""
PHASE 1 · PROJECT 1 — House Price Prediction
Build the dataset: Saudi Ministry of Justice real estate SALE transactions.

  python build_dataset.py              download + harmonise + report
  python build_dataset.py --no-download   rebuild from CSVs already on disk

SOURCE
  Ministry of Justice (MOJ) open data, republished as CSV by the public
  mirror github.com/civillizard/Saudi-Real-Estate-Data under the KSA Open
  Data License. Raw files are unmodified government data. This script does
  not clean them -- cleaning is YOUR project.

WHAT IT PRODUCES
  out/ksa_sales_raw.parquet    every quarter, English headers, nothing else touched
  out/ksa_sales_typed.parquet  only the quarters that carry property_type
  out/SCHEMA.md                the column dictionary, Arabic -> English

WHAT IT DELIBERATELY DOES NOT DO
  No outlier removal. No imputation. No de-duplication. No price filtering.
  Those are exercises 33, 34, 38 and 39 of your labs, on real data.
"""
import sys, io, time
from pathlib import Path
import urllib.request
import pandas as pd

BASE = ("https://raw.githubusercontent.com/civillizard/"
        "Saudi-Real-Estate-Data/main/moj/sales")
RAW  = Path("raw"); OUT = Path("out")
RAW.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)

# 2021 Q1 is genuinely absent from the source. Not a bug here -- a gap there.
QUARTERS = [f"{y}-Q{q}" for y in range(2020, 2027) for q in (1,2,3,4)]

# Arabic -> English. Two schemas exist; both map onto the same names.
COLMAP = {
    "المنطقة": "region", "المدينة": "city",
    "المدينة / الحي": "city_district", "الحي": "district",
    "المخطط": "plan", "رقم القطعة": "parcel_no",
    "الرقم المرجعي للصفقة": "deal_ref", "رقم مرجعي": "deal_ref",
    "تاريخ الصفقة ميلادي": "date_greg", "التاريخ": "date_greg",
    "تاريخ الصفقة هجري": "date_hijri",
    "تصنيف العقار": "classification", "نوع العقار": "property_type",
    "عدد العقارات": "n_properties",
    "السعر": "price_sar", "السعر بالريال السعودي": "price_sar",
    "المساحة": "area_m2", "المساحة ": "area_m2",
    "سعر المتر المربع": "price_per_m2",      # DERIVED -- see the warning below
}

def download(force=False):
    got = []
    for q in QUARTERS:
        name = f"MOJ-Sales-{q}.csv"; dest = RAW / name
        if dest.exists() and not force:
            got.append(dest); continue
        try:
            with urllib.request.urlopen(f"{BASE}/{name}", timeout=90) as r:
                dest.write_bytes(r.read())
            got.append(dest); print(f"  downloaded {name}")
        except Exception as e:
            print(f"  absent     {name}  ({type(e).__name__})")
        time.sleep(0.2)
    return got

def load(paths):
    frames = []
    for p in sorted(paths):
        df = pd.read_csv(p, encoding="utf-8-sig", dtype=str)
        df = df.rename(columns={c: COLMAP.get(c.strip(), c.strip()) for c in df.columns})
        df["source_file"] = p.name
        df["quarter"] = p.stem.replace("MOJ-Sales-", "")
        frames.append(df)
    return pd.concat(frames, ignore_index=True)

def to_numeric(s):
    """Prices and areas arrive as text with comma thousands separators."""
    return pd.to_numeric(s.astype(str).str.replace(",", "", regex=False)
                          .str.strip().replace({"": None, "nan": None}), errors="coerce")

def main():
    paths = ([RAW / f"MOJ-Sales-{q}.csv" for q in QUARTERS
              if (RAW / f"MOJ-Sales-{q}.csv").exists()]
             if "--no-download" in sys.argv else download())
    if not paths:
        print("no files; drop the --no-download flag"); return

    df = load(paths)
    df["price_sar"] = to_numeric(df["price_sar"])
    df["area_m2"]   = to_numeric(df["area_m2"])
    df["n_properties"] = pd.to_numeric(df["n_properties"], errors="coerce")
    df["date_greg"] = pd.to_datetime(df["date_greg"], format="mixed", dayfirst=False,
                                     errors="coerce")

    order = ["quarter","date_greg","date_hijri","region","city","city_district",
             "district","plan","parcel_no","classification","property_type",
             "n_properties","area_m2","price_sar","price_per_m2","deal_ref",
             "source_file"]
    df = df.reindex(columns=[c for c in order if c in df.columns])

    df.to_parquet(OUT / "ksa_sales_raw.parquet", index=False)
    typed = df[df.property_type.notna()].copy()
    typed.to_parquet(OUT / "ksa_sales_typed.parquet", index=False)

    # ── report, no cleaning ──
    p = lambda *a: print(*a)
    p("\n" + "="*70); p("  DATASET BUILT  (raw -- nothing cleaned)"); p("="*70)
    p(f"  files loaded        {len(paths)} quarters")
    p(f"  rows                {len(df):,}")
    p(f"  columns             {df.shape[1]}")
    p(f"  date range          {df.date_greg.min():%Y-%m-%d} to {df.date_greg.max():%Y-%m-%d}")
    p(f"  with property_type  {len(typed):,} rows ({len(typed)/len(df):.1%})")
    p(f"  regions             {df.region.nunique()}")
    p(f"  cities              {df.city.nunique()}")
    p("\n  nulls per column")
    for c in df.columns:
        n = df[c].isna().sum()
        if n: p(f"    {c:<16} {n:>9,}  {n/len(df):>6.1%}")
    p("\n  classification")
    for k, v in df.classification.value_counts().head(8).items(): p(f"    {k:<14} {v:>9,}")
    if len(typed):
        p("\n  property_type (2023 Q1-Q3 only)")
        for k, v in typed.property_type.value_counts().head(8).items(): p(f"    {k:<14} {v:>9,}")
    p("\n  price_sar")
    p(f"    min {df.price_sar.min():,.0f} · median {df.price_sar.median():,.0f} · "
      f"max {df.price_sar.max():,.0f} · skew {df.price_sar.skew():.1f}")
    p(f"    zero or negative: {int((df.price_sar <= 0).sum()):,}")
    p("\n  area_m2")
    p(f"    min {df.area_m2.min():,.2f} · median {df.area_m2.median():,.0f} · "
      f"max {df.area_m2.max():,.0f} · skew {df.area_m2.skew():.1f}")
    p(f"    zero or negative: {int((df.area_m2 <= 0).sum()):,}")
    p(f"\n  exact duplicate rows (ignoring source_file): "
      f"{int(df.drop(columns=['source_file','quarter']).duplicated().sum()):,}")
    p("\n" + "!"*70)
    p("  price_per_m2 IS price_sar / area_m2. It exists only in 2023 Q1.")
    p("  If you feed it to a model predicting price_sar you have built")
    p("  exercise 40 by accident. Run find_leaks() and watch it score 1.0.")
    p("!"*70)
    p(f"\n  written: {OUT/'ksa_sales_raw.parquet'}")
    p(f"           {OUT/'ksa_sales_typed.parquet'}\n")

if __name__ == "__main__":
    main()
