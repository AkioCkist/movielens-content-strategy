# MovieLens Content Strategy — Segment-Based Movie Promotion

**VNUK Big Data Analytics — Final Project 2026**
Team: Hồ Anh Tuấn · Trần Ngọc Quân — Lecturer: Trần Thế Vũ

This project turns the MovieLens 10M dataset (10,000,054 ratings, 69,878 users, 10,681 movies) into decisions about **which titles to promote to which audience segment**. The pipeline goes from MySQL to KNIME (K-Means and Logistic Regression), writes the results back to MySQL and shows them in Power BI.

```
MovieLens .dat files ──► MySQL 8 (raw tables, chronological split, TRAIN features)
                              │
                              ▼
                KNIME: K-Means (K = 4) ──► user_segments
                KNIME: Logistic Regression ──► rating_predictions, model_metrics
                              │
                              ▼
            MySQL dashboard_* views ──► Power BI (5 pages) ──► 4 recommendations
```

## Key results (model version `logit_v1`, TEST split)

| Metric | Value |
|---|---|
| Accuracy | 69.26 % (majority baseline 59.32 %, +9.93 pp) |
| ROC AUC | 0.758 |
| Precision / Recall / F1 | 60.58 % / 69.94 % / 64.92 % |
| Scored TEST rows | 76,633 of 1,500,006 (5.11 % coverage) |
| Segments | Genre Specialists, Diverse Explorers, Selective Critics, Mainstream Enthusiasts |

---

## 1. Requirements

| Tool | Version used | Purpose |
|---|---|---|
| MySQL Server + Workbench | 8.0 | Storage, SQL transformations, dashboard views |
| Python | 3.10+ | Runs `sql/01`–`sql/07` through `python_sql_scripts/` |
| KNIME Analytics Platform | 5.x (with the MySQL connector) | Data-quality, clustering and classification workflows |
| Power BI Desktop | Current | Dashboard (`dashboard/movielens_content_strategy_full.pbix`) |

Python packages are listed in `python_sql_scripts/requirements.txt` (`mysql-connector-python`, `openpyxl`).

## 2. Get the data

1. Download **MovieLens 10M** (`ml-10m.zip`) from GroupLens: <https://grouplens.org/datasets/movielens/10m/>.
2. Extract it so the files are at:
   ```
   data/ml-10M100K/movies.dat
   data/ml-10M100K/ratings.dat
   data/ml-10M100K/tags.dat
   ```
   The `data/` folder and `*.zip` are git-ignored, so the dataset is never committed.

## 3. Configure credentials (never commit them)

```powershell
py -m pip install -r .\python_sql_scripts\requirements.txt
Copy-Item .\python_sql_scripts\.env.example .\python_sql_scripts\.env
notepad .\python_sql_scripts\.env
```

`.env` holds placeholders only in the template:

```ini
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=<your_mysql_user>
MYSQL_PASSWORD=<your_mysql_password>
MYSQL_DATABASE=movielens_strategy
# MOVIELENS_DATA_DIR=C:/path/to/ml-10M100K   (optional)
```

- `.env` and `credentials*` are in `.gitignore`. Do not put real passwords in code, SQL files, KNIME workflows or this README.
- In KNIME, enter the MySQL password in the **MySQL Connector** node (or a workflow credential) on your machine. Do not save it into the exported `.knwf`.
- MySQL must allow local file loading: set `local_infile=ON` on the server.

## 4. Run order

Run the steps **in this order**. Steps 2 and 4 are KNIME write-back points: later steps read the tables they create.

| # | Where | What to run | Creates / updates |
|---|---|---|---|
| 1 | Python | `py .\python_sql_scripts\run_pipeline.py --through 5`  (scripts 01–05) | Schema, raw tables, data-quality checks, `rating_split` (TRAIN 70 % / VALIDATION 15 % / TEST 15 % by time), `train_user_stats`, `train_movie_stats`, `train_user_genre_stats` |
| 1b | KNIME *(optional)* | `knime/movielens_data_quality_finalterm.knwf` | `movies_clean`, `tags_clean`, `dq_summary`, `eda_user_stats_summary` |
| 2 | KNIME | `knime/movielens_audience_segmentation.knwf` — K-Means with **K = 4** | `user_segments` (one segment per TRAIN user, version `kmeans_v1`) |
| 2b | MySQL *(only if needed)* | `sql/migrate_user_segments.sql` | Repairs `user_segments` if the KNIME DB Writer recreated it with a VARCHAR `cluster_id` |
| 3 | Python | `py .\python_sql_scripts\06_logistic_features.py` | `ml_rating_features` (segment-aware features for the classifier) |
| 4 | KNIME | `knime/movielens_like_prediction.knwf` — Logistic Regression; the **DB SQL Executor** node runs `sql/knime_logit_metrics.sql` | `rating_predictions`, `model_metrics` (version `logit_v1`) |
| 5 | Python | `py .\python_sql_scripts\07_dashboard_views.py` | All `dashboard_*` views |
| 6 | Power BI | Open `dashboard/movielens_content_strategy_full.pbix` → **Refresh** | 5 report pages |

Shortcut: `py .\python_sql_scripts\run_all.py` runs steps 01–07 one at a time. Before steps 6 and 7 it waits until KNIME has finished writing `user_segments`, `rating_predictions` and `model_metrics`. Use `--from-step N` / `--through N` to resume. See `python_sql_scripts/README.md` for details such as long-running index builds, `--reload` and rollback tables.

### Checks after each stage

- After step 1: `ratings` has 10,000,054 rows; each user's ratings are split by time.
- After step 2: `user_segments` has one row per TRAIN user and 4 clusters.
- After step 4: `model_metrics` has TEST rows for `logit_v1`. Expected accuracy ≈ 69.3 % and AUC ≈ 0.758.
- After step 6: the Power BI cards match the numbers in the table above.

## 5. Repository structure

```
├── sql/                      01–07 SQL scripts, knime_logit_metrics.sql, migrate_user_segments.sql
├── python_sql_scripts/       Python runners for sql/01–07, .env.example, results/*.xlsx
├── knime/                    3 exported KNIME workflows (.knwf)
├── kmeans/                   Silhouette / cluster exports for K = 3 … 7
├── dashboard/                movielens_content_strategy_full.pbix (+ PBIP project source)
├── powerbi/                  Screenshots of the 5 dashboard pages
├── screenshots/knime/        Screenshots of the KNIME workflows
├── docs/                     Data dictionary, AI-use statement
├── demo/                     Demo script
├── output/                   Final report (EN + VI), IEEE paper source, weekly slides
├── requirement/              Course brief and weekly requirements
└── MovieLens_10M_Final_Project_Plan.md
```

## 6. Deliverables

| Deliverable | File |
|---|---|
| Final report (English) | `output/MovieLens_Content_Strategy_Final_Report.docx` |
| IEEE paper (LaTeX source + figures) | `output/ieee_paper/BigDataFinalTerm.tex`, `output/ieee_paper/figures/` (upload both to Overleaf to build the PDF) |
| Dashboard | `dashboard/movielens_content_strategy_full.pbix`, screenshots in `powerbi/` |
| Weekly presentations | `output/weekly_presentations/` |
| Data dictionary | `docs/data_dictionary.md` |

## 7. Notes and limitations

- Every statistic used as a model feature is computed on **TRAIN only**, so no information leaks from VALIDATION or TEST.
- The classifier only scores TEST ratings whose user and movie both have TRAIN history and a segment. That is why coverage is 5.11 % of TEST rows. Results apply to known users and known titles, not to cold-start cases.
- MovieLens ratings are a proxy for engagement. The recommendations should be validated with an A/B test before rollout (see the report, Section 8).

## Data licence

MovieLens 10M is provided by GroupLens Research, University of Minnesota, for research use. Cite: F. M. Harper and J. A. Konstan, "The MovieLens Datasets: History and Context," *ACM TiiS*, 5(4), 2015. Do not redistribute the dataset from this repository.
