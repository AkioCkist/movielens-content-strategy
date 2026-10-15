# MovieLens MySQL pipeline (Python)

This folder replaces interactive execution of `sql/01` through `sql/07`.
Python still sends SQL to MySQL, but the connector waits indefinitely for an
active query and recovers from error 2013 while an index is still building.

## Why this avoids the 900-second failure

- `read_timeout=None` and `write_timeout=None`: no client-side 900-second cutoff.
- indexes are part of a new empty table, so a fresh import never performs a
  one-shot `CREATE INDEX` over 10 million existing rows;
- on an existing database, missing indexes are created one at a time with
  `ALGORITHM=INPLACE, LOCK=NONE`; after a dropped socket the script reconnects
  and checks whether MySQL is still building the index;
- derived tables are created with their keys already present, validated, then
  atomically published; the previous table is retained with a timestamp suffix
  as a rollback copy;
- each raw table is skipped when it already contains data. Destructive reloads
  happen only when `02_load_data.py --reload` is explicitly supplied.

## Setup

From the repository root in PowerShell:

```powershell
py -m pip install -r .\python_sql_scripts\requirements.txt
Copy-Item .\python_sql_scripts\.env.example .\python_sql_scripts\.env
notepad .\python_sql_scripts\.env
```

Set the MySQL user/password in `.env`. The file is ignored by Git. The default
data path is `data/ml-10M100K`; use `MOVIELENS_DATA_DIR` only if the files live
elsewhere. MySQL must allow `LOCAL INFILE` (server setting `local_infile=ON`).

## Run everything in order (recommended)

```powershell
py .\python_sql_scripts\run_all.py
```

`run_all.py` runs steps 01-07 strictly one at a time:

- holds a MySQL named lock for the whole run, so a second runner refuses to start;
- starts a step only after the previous step exited with code 0 and MySQL has
  no other active statement on the schema (e.g. an index still building
  server-side after a dropped connection);
- stops at the first failing step and prints the `--from-step` to resume with;
- before step 6 (and 7) waits until KNIME has written `user_segments`
  (and `rating_predictions`, `model_metrics`) and their row counts stop
  changing, then continues automatically. Use `--no-wait` to stop there instead.

Resume or limit the range with `--from-step N` and `--through N`.

## Run in two parts

The pipeline has a KNIME write-back boundary, so it can also be run in two parts:

```powershell
py .\python_sql_scripts\run_pipeline.py --through 5
```

After KNIME has populated `user_segments` (and later model output tables):

```powershell
py .\python_sql_scripts\run_pipeline.py --from-step 6 --through 7
```

Run one step directly when needed, for example:

```powershell
py .\python_sql_scripts\01_create_schema.py
py .\python_sql_scripts\03_quality_checks.py
```

Run only the four KPI queries in plan section 12.4 (without rebuilding the
feature tables from sections 12.1-12.3):

```powershell
py .\python_sql_scripts\05_feature_tables.py --queries-only
```

## Query result files

Scripts 02 through 07 write query results to
`python_sql_scripts/results/<script_name>_results.xlsx`. Each result table is a
separate worksheet in that script's workbook. For example, section 12.4 creates
`05_feature_tables_results.xlsx` with four KPI worksheets. Excel format is used
because CSV cannot contain multiple worksheets.

Set `MOVIELENS_RESULTS_DIR` in `.env` to store the workbooks elsewhere.

## CLI query progress

Long-running operations display a live CLI progress bar with elapsed time and
the current MySQL process state. When MySQL exposes stage estimates through
`performance_schema`, the bar also displays a real percentage. For operations
without an estimate (common for `SELECT`, `GROUP BY`, and joins), the bar is an
indeterminate activity indicator; elapsed time and server state remain real.

If raw data is partial or must be deliberately replaced:

```powershell
py .\python_sql_scripts\02_load_data.py --reload
```

`--reload` truncates `movies`, `ratings`, `tags`, and `movie_genres`; do not use
it when those tables contain data that cannot be recreated from the `.dat` files.
After a reload, rerun steps 4 and 5 so derived tables match the new raw rows.

## Rollback for rebuilt derived tables

Steps 4 and 5 retain the former table as
`<table>_backup_YYYYMMDD_HHMMSS`. To roll back, rename the current table aside
and rename the selected backup to the original name. Backups are not deleted
automatically.

