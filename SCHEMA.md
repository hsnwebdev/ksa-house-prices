# Saudi MOJ real estate sale transactions — schema

**Source:** Ministry of Justice (Saudi Arabia) open data, republished as CSV by
`github.com/civillizard/Saudi-Real-Estate-Data` under the KSA Open Data License.
Raw files are unmodified government data; `build_dataset.py` only renames headers
to English, parses numbers and dates, and concatenates.

**Rows:** 1,269,512 · **Quarters:** 23 · **Range:** 2020-01-01 to 2026-03-31
**Built:** 12 October 2026

## Columns

| English | Arabic | Type | Coverage | Notes |
|---|---|---|---|---|
| `quarter` | — | text | 100% | added by the loader, e.g. `2024-Q1` |
| `date_greg` | تاريخ الصفقة ميلادي / التاريخ | date | 100% | Gregorian transaction date |
| `date_hijri` | تاريخ الصفقة هجري | text | 96.5% | absent from the 2023-Q1 schema |
| `region` | المنطقة | text | 100% | 16 distinct strings for 13 real regions — spelling variants |
| `city` | المدينة | text | 100% | 174 distinct |
| `city_district` | المدينة / الحي | text | 96.5% | `city/district` in one field, needs splitting |
| `district` | الحي | text | 3.5% | 2023-Q1 only |
| `plan` | المخطط | text | 3.5% | 2023-Q1 only |
| `parcel_no` | رقم القطعة | text | 3.5% | 2023-Q1 only |
| `classification` | تصنيف العقار | text | 100% | سكني residential · تجاري commercial · زراعي agricultural · صناعي industrial |
| `property_type` | نوع العقار | text | 10.4% | **2023 Q1–Q3 only.** قطعة أرض land plot · شقة apartment · فيلا villa · بيت house · عمارة building · معرض/محل shop |
| `n_properties` | عدد العقارات | int | 100% | a deal can cover several properties — price is for the DEAL |
| `area_m2` | المساحة | float | 100% | square metres; one row is 0 |
| `price_sar` | السعر / السعر بالريال السعودي | float | 100% | deal price in SAR |
| `price_per_m2` | سعر المتر المربع | float | 3.5% | **DERIVED = price_sar / area_m2. A leak. 2023-Q1 only.** |
| `deal_ref` | الرقم المرجعي للصفقة / رقم مرجعي | text | 100% | transaction reference |
| `source_file` | — | text | 100% | provenance |

## Known defects — these are the project, do not expect them fixed

- **2021-Q1 is missing from the source.** A real gap, not a download failure.
- **12 rows are null in every field** — trailing blank lines in some CSVs.
- **44,842 exact duplicate rows** once `source_file` and `quarter` are ignored.
- **`price_sar` skew is 428** · min 5,000 · median 375,000 · max 31,837,504,626.
- **`area_m2` skew is 52.8** · one row has area 0 · max 24,007,240 m².
- **`region` has 16 spellings for 13 regions.** `data/region_mapping.csv` in the
  source repo maps 33 variants onto canonical names.
- **Two schemas.** 2023-Q1 has 13 columns, 2023 Q2–Q3 have 11, everything else 10.
  The loader unions them, so the extra columns are null outside those quarters.
- **Hijri and Gregorian dates both present**, formats inconsistent across years.
- **`n_properties` > 1 on some rows**, so `price_sar` is not a per-property price.

## What this dataset does NOT have

No bedrooms, bathrooms, age, condition, finish quality, or floor. It is a
*transaction register*, not a property listing. Your features are location,
area, classification, type (where present), and time.
