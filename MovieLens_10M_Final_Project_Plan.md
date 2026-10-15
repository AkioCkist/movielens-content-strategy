# MovieLens 10M Final Project — Kế hoạch triển khai chi tiết

| | |
|---|---|
| **Đề tài** | Segment-Based Movie Promotion and Content Discovery Strategy |
| **Tên tiếng Việt** | Phân khúc khán giả và dự báo khả năng yêu thích phim để hỗ trợ chiến lược quảng bá nội dung |
| **Dataset** | MovieLens 10M (GroupLens) |
| **Mô hình** | K-Means (phân khúc) + Logistic Regression (dự báo) |
| **Pipeline bắt buộc** | Dataset → MySQL → KNIME → MySQL (kết quả) → Power BI → Đề xuất quyết định |

> **Cách đọc tài liệu này**
> - Mỗi bước có 3 phần: **Làm gì** (thao tác), **Kết quả mong đợi**, **Bằng chứng cần chụp**.
> - Khối `sql` trong tài liệu được chép nguyên văn từ thư mục `sql/`. Nếu sửa SQL, sửa trong `sql/` và trong `python_sql_scripts/` cho khớp.
> - Các ngưỡng như số cluster, threshold `0.5`, minimum support `50` chỉ là giá trị khởi đầu. Giá trị cuối cùng phải chọn dựa trên dữ liệu và kết quả đánh giá thực tế.

## Mục lục

- [1. Mục tiêu tài liệu](#1-mục-tiêu-tài-liệu)
- [2. Đề bài và điều kiện đạt](#2-đề-bài-và-điều-kiện-đạt)
- [3. Linh hồn của project](#3-linh-hồn-của-project)
- [4. Dataset](#4-dataset)
- [5. Phần mềm cần cài](#5-phần-mềm-cần-cài)
- [6. Cấu trúc thư mục và cách chạy pipeline](#6-cấu-trúc-thư-mục-và-cách-chạy-pipeline)
- **Phase A — MySQL:** [7](#7-tải-và-kiểm-tra-dataset) · [8](#8-tạo-database-và-bảng) · [9](#9-import-movielens-vào-mysql) · [10](#10-kiểm-tra-chất-lượng-dữ-liệu) · [11](#11-chia-train--validation--test-theo-thời-gian) · [12](#12-tạo-feature-tables-chỉ-từ-train)
- **Phase B — KNIME K-Means:** [13](#13-chuẩn-bị-knime-và-kết-nối-mysql) · [14](#14-workflow-k-means-từng-node) · [15](#15-ghi-kết-quả-k-means-về-mysql)
- **Phase C — KNIME Logistic Regression:** [16](#16-tạo-view-feature-cho-logistic-regression) · [17](#17-workflow-logistic-regression-từng-node) · [18](#18-ghi-kết-quả-logistic-regression-về-mysql)
- **Phase D — Power BI:** [19](#19-tạo-dashboard-views-trong-mysql) · [20](#20-kết-nối-power-bi-với-mysql) · [21](#21-data-model-trong-power-bi) · [22](#22-dax-measures) · [23](#23-dựng-từng-trang-dashboard)
- **Phase E — Insight:** [24](#24-cách-viết-insight) · [25](#25-các-recommendation-bắt-buộc)
- **Phase F — Nộp bài:** [26](#26-cấu-trúc-final-report) · [27](#27-readme-bắt-buộc) · [28](#28-mẫu-khai-báo-sử-dụng-ai) · [29](#29-kịch-bản-demo-810-phút) · [30](#30-checklist-nộp-bài) · [31](#31-kế-hoạch-theo-buổi) · [32](#32-definition-of-done) · [33](#33-các-lỗi-dễ-mất-điểm) · [34](#34-điểm-cộng)

---

## 1. Mục tiêu tài liệu

Đây là kế hoạch thực hiện end-to-end cho final project, gồm:

- tải và kiểm tra MovieLens 10M;
- thiết kế bài toán ra quyết định;
- thao tác trong MySQL (Workbench hoặc Python);
- thao tác trong KNIME cho K-Means và Logistic Regression, từng node một;
- ghi kết quả từ KNIME về MySQL;
- dựng dashboard trong Power BI, từng bước;
- code SQL và DAX cần thiết;
- cấu trúc report, README, video demo, GitHub;
- checklist nộp bài bám sát rubric.

---

## 2. Đề bài và điều kiện đạt

Project được chấm trên 6 phần:

| Phần | Điểm | Bằng chứng cần có |
|---|---:|---|
| Data Problem Definition & Decision Questions | 1.5 | Dataset thật, stakeholder, problem statement, ít nhất 3 câu hỏi đo lường được |
| MySQL Database & SQL Queries | 1.5 | Schema, import, keys, filter, aggregate, join, KPI, script chạy lại được |
| KNIME Workflow & Data Preparation | 2.0 | Đọc trực tiếp từ MySQL, cleaning, transform, EDA, tên node/annotation rõ, write-back |
| Machine Learning & Evaluation | 2.0 | Mô hình phù hợp, features/target, preprocessing, metric, kiểm soát leakage, limitations |
| Dashboard, Insights & Decisions | 2.0 | Dữ liệu từ MySQL, KPI, visual, filter, output ML, ít nhất 3 recommendation |
| Documentation & Demonstration | 1.0 | Report, nguồn dataset, SQL, KNIME, PBIX, README, demo, trích dẫn, khai báo AI |

### Điều kiện không được vi phạm

- KNIME phải kết nối **trực tiếp** MySQL.
- KNIME phải **ghi kết quả mô hình trở lại** MySQL.
- Dashboard phải dùng dữ liệu có nguồn từ MySQL.
- Không nộp giải pháp chỉ đọc CSV.
- Không commit password, credentials hoặc dữ liệu cá nhân lên GitHub.
- Phải ghi nguồn dataset và khai báo phần hỗ trợ của AI.

---

## 3. Linh hồn của project

### 3.1 Stakeholder

**Content Programming and Personalization Manager** của một nền tảng xem phim.

### 3.2 Problem statement

> A movie platform serves users with different preferences, but popularity-based promotion treats all audiences similarly. This project identifies audience segments from historical rating behaviour and predicts the probability that a user will positively rate a movie. The results support segment-specific movie promotion and content discovery decisions.

### 3.3 Quyết định trung tâm

> Nền tảng nên ưu tiên quảng bá phim hoặc thể loại nào cho từng phân khúc khán giả?

### 3.4 Định nghĩa positive engagement

```text
Positive engagement = rating >= 4.0
```

Đây là proxy cho việc người dùng yêu thích phim. **Không** được diễn giải thành lượt xem, doanh thu, churn hay subscription.

### 3.5 Bốn decision questions

1. Hành vi rating và sở thích thể loại khác nhau như thế nào giữa các nhóm người dùng?
2. Có thể chia người dùng thành những audience segment rõ ràng nào?
3. Dựa trên lịch sử người dùng và đặc điểm phim, xác suất người dùng rating một phim từ 4 sao trở lên là bao nhiêu?
4. Phim/thể loại nào có predicted positive engagement cao nhưng mức độ phổ biến hiện tại còn thấp trong từng segment?

### 3.6 Liên kết giữa hai mô hình

```text
10M ratings
  → tạo user profiles (chỉ từ TRAIN)
  → K-Means tạo audience segments
  → segment trở thành một feature của Logistic Regression
  → Logistic Regression tạo probability of like
  → tổng hợp Segment × Movie
  → dashboard Content Opportunity Matrix
  → quyết định Promote / Maintain / Reduce priority / Monitor
```

---

## 4. Dataset

### 4.1 Dataset được chọn

**MovieLens 10M** của GroupLens:

| Chỉ số | Giá trị |
|---|---:|
| Ratings | 10,000,054 |
| Tag applications | 95,580 |
| Movies | 10,681 |
| Users (theo README GroupLens, gồm cả user chỉ gắn tag) | 71,567 |
| Users có ít nhất 1 rating (đếm thực tế trong MySQL) | 69,878 |
| Thang rating | 0.5 – 5.0, bước 0.5 |

- Mỗi user có ít nhất 20 ratings; user được ẩn danh; không có thông tin nhân khẩu học.
- Khi báo cáo số user, dùng **69,878** (con số `total_users` trên dashboard) và giải thích chênh lệch với 71,567 trong README.

Nguồn chính thức:

- Dataset page: <https://grouplens.org/datasets/movielens/10m/>
- README và data dictionary: <https://files.grouplens.org/datasets/movielens/ml-10m-README.html>

### 4.2 Các file trong dataset

```text
movies.dat   → MovieID::Title::Genres
ratings.dat  → UserID::MovieID::Rating::Timestamp
tags.dat     → UserID::MovieID::Tag::Timestamp
```

### 4.3 Giới hạn phải nêu trong report

- Dataset phát hành năm 2009, không đại diện đầy đủ cho thị trường streaming hiện tại.
- Không có lượt xem, exposure, click, watch time, subscription, doanh thu hay chi phí bản quyền.
- Không có thông tin nhân khẩu học.
- Mọi user đều có ít nhất 20 ratings, nên dữ liệu thiên về nhóm người rating tích cực.
- Nếu user không rating một phim, ta không biết họ chưa xem hay đã xem nhưng không quan tâm.
- Prediction chỉ là `probability of positive rating`, không phải `probability of watching`.

### 4.4 Quy tắc license và GitHub

Không commit file dataset gốc lên GitHub nếu chưa có quyền phân phối lại. Repository chỉ cần:

- link tải chính thức;
- citation;
- checksum (nếu có);
- hướng dẫn tải và import;
- script tái tạo pipeline.

---

## 5. Phần mềm cần cài

| Phần mềm | Mục đích | Ghi chú cài đặt |
|---|---|---|
| MySQL Server 8.0 | Lưu 10M ratings, feature tables, kết quả mô hình | Bật `local_infile` (xem 9.1) |
| MySQL Workbench 8.0 | Chạy SQL, chụp bằng chứng | Tăng read timeout (xem 9.1) |
| Python 3.10+ | Chạy pipeline SQL không bị timeout | `py -m pip install -r python_sql_scripts/requirements.txt` |
| KNIME Analytics Platform 5.x | Data preparation, K-Means, Logistic Regression, write-back | Driver MySQL đã có sẵn trong KNIME Database extension |
| Power BI Desktop | Dashboard | Cần cài thêm **MySQL Connector/NET** (xem 20.1) |
| Git / GitHub | Nộp source, scripts, workflow | |
| Screen recorder | Quay demo nếu không demo live | |

### Tài nguyên máy khuyến nghị

- RAM: tối thiểu 16 GB, 32 GB sẽ thoải mái hơn.
- Ổ đĩa trống: 30–50 GB.
- Không đọc 10M rows vào KNIME cho mọi thao tác: filter/aggregate trong MySQL trước.
- Power BI chỉ đọc dashboard views (bảng tổng hợp nhỏ), không đọc bảng `ratings` 10M rows.

---

## 6. Cấu trúc thư mục và cách chạy pipeline

### 6.1 Cấu trúc thư mục

```text
movielens-content-strategy/
├── README.md
├── .gitignore
├── data/
│   ├── README_DATA.md
│   └── checksums.txt
├── sql/                         ← chạy trong MySQL Workbench, chụp bằng chứng
│   ├── 01_create_schema.sql
│   ├── 02_load_data.sql
│   ├── 03_quality_checks.sql
│   ├── 04_create_splits.sql
│   ├── 05_feature_tables.sql
│   ├── 06_logistic_features.sql
│   ├── 07_dashboard_views.sql
│   └── knime_logit_metrics.sql  ← KNIME chạy sau khi ghi predictions (section 18)
├── python_sql_scripts/          ← cùng SQL, chạy bằng Python, không bị timeout
│   ├── README.md
│   ├── requirements.txt
│   ├── .env.example
│   ├── common.py
│   ├── 01_create_schema.py … 07_dashboard_views.py
│   ├── run_all.py               ← chạy toàn bộ 01 → 07 theo thứ tự
│   ├── run_pipeline.py
│   └── results/                 ← Excel kết quả query, mỗi script một file
├── knime/
│   ├── movielens_audience_segmentation.knwf
│   └── movielens_like_prediction.knwf
├── dashboard/
│   └── movielens_content_strategy.pbix
├── report/
│   └── final_report.pdf
├── screenshots/
├── demo/
│   └── demo_script.md
└── docs/
    ├── data_dictionary.md
    └── ai_use_statement.md
```

`.gitignore` đề xuất:

```gitignore
data/ml-10M100K/
*.zip
*.log
*.tmp
.env
credentials*
```

### 6.2 Hai cách chạy cùng một pipeline

`sql/` và `python_sql_scripts/` chứa **cùng các câu SQL**:

| Cách | Khi nào dùng | Ưu điểm |
|---|---|---|
| `sql/*.sql` trong MySQL Workbench | Chụp bằng chứng cho rubric, chạy thử từng query | Nhìn thấy SQL và kết quả ngay |
| `python_sql_scripts/*.py` | Chạy thật toàn bộ pipeline | Không bị giới hạn 900 giây của Workbench, tự kết nối lại khi đang tạo index, xuất kết quả ra `python_sql_scripts/results/<script>_results.xlsx` |

### 6.3 Chạy toàn bộ pipeline bằng một lệnh (khuyến nghị)

**Bước 1 — cài thư viện và khai báo kết nối (làm một lần):**

```powershell
py -m pip install -r .\python_sql_scripts\requirements.txt
Copy-Item .\python_sql_scripts\.env.example .\python_sql_scripts\.env
notepad .\python_sql_scripts\.env
```

Điền `MYSQL_USER` và `MYSQL_PASSWORD` trong `.env`. File này đã bị `.gitignore` chặn, không bị commit.

**Bước 2 — chạy:**

```powershell
py .\python_sql_scripts\run_all.py
```

`run_all.py` đảm bảo:

1. chỉ một pipeline chạy tại một thời điểm (MySQL named lock);
2. bước sau chỉ bắt đầu khi bước trước thoát thành công **và** MySQL không còn câu lệnh nào đang chạy trên schema;
3. dừng ngay ở bước lỗi và in lệnh `--from-step N` để chạy tiếp;
4. trước bước 06, tự chờ KNIME ghi xong `user_segments`; trước bước 07, chờ thêm `rating_predictions` và `model_metrics`. Khi các bảng có dữ liệu và số dòng không đổi trong 45 giây, pipeline tự chạy tiếp.

| Lệnh | Tác dụng |
|---|---|
| `py .\python_sql_scripts\run_all.py` | Chạy 01 → 07, chờ KNIME ở giữa |
| `py .\python_sql_scripts\run_all.py --through 5` | Chỉ chạy phần MySQL trước KNIME |
| `py .\python_sql_scripts\run_all.py --from-step 6` | Chạy tiếp sau khi KNIME đã xong |
| `py .\python_sql_scripts\run_all.py --no-wait` | Dừng (không chờ) nếu KNIME chưa ghi dữ liệu |

---

# PHASE A — MYSQL DATABASE

## 7. Tải và kiểm tra dataset

**Làm gì:**

1. Mở trang MovieLens 10M chính thức.
2. Tải `ml-10m.zip`.
3. Đọc README và license.
4. Giải nén vào `data/ml-10M100K/` (thư mục này không commit lên GitHub).
5. Kiểm tra có đủ ba file `movies.dat`, `ratings.dat`, `tags.dat`.
6. Ghi link dataset và ngày truy cập vào `data/README_DATA.md`.

**Bằng chứng cần chụp:**

- Trang nguồn GroupLens.
- Thư mục dataset sau khi giải nén.
- README cho thấy số dòng và định dạng dữ liệu.

---

## 8. Tạo database và bảng

**Làm gì:** mở `sql/01_create_schema.sql` trong Workbench và chạy toàn bộ (`Ctrl+Shift+Enter`), hoặc chạy `py .\python_sql_scripts\01_create_schema.py`.

Script tạo database `movielens_strategy`, bốn bảng dữ liệu gốc (`movies`, `ratings`, `tags`, `movie_genres`) và ba bảng để KNIME ghi kết quả (`user_segments`, `rating_predictions`, `model_metrics`).

```sql
CREATE DATABASE IF NOT EXISTS movielens_strategy
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE movielens_strategy;

CREATE TABLE IF NOT EXISTS movies (
    movie_id INT UNSIGNED NOT NULL,
    title VARCHAR(500) NOT NULL,
    genres VARCHAR(255) NOT NULL,
    PRIMARY KEY (movie_id)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS ratings (
    rating_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    movie_id INT UNSIGNED NOT NULL,
    rating DECIMAL(2,1) NOT NULL,
    rating_ts INT UNSIGNED NOT NULL,
    PRIMARY KEY (rating_id),
    INDEX idx_ratings_user (user_id),
    INDEX idx_ratings_movie (movie_id),
    -- InnoDB appends the primary key, so this index is ordered by
    -- (rating_ts, rating_id): the exact order of the chronological split.
    INDEX idx_ratings_ts (rating_ts)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS tags (
    tag_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    movie_id INT UNSIGNED NOT NULL,
    tag_text VARCHAR(500) NOT NULL,
    tag_ts INT UNSIGNED NOT NULL,
    PRIMARY KEY (tag_id),
    INDEX idx_tags_user (user_id),
    INDEX idx_tags_movie (movie_id)
) ENGINE = InnoDB;

-- The primary key (movie_id, genre) already serves lookups by movie_id.
CREATE TABLE IF NOT EXISTS movie_genres (
    movie_id INT UNSIGNED NOT NULL,
    genre VARCHAR(50) NOT NULL,
    PRIMARY KEY (movie_id, genre),
    INDEX idx_movie_genres_genre (genre)
) ENGINE = InnoDB;

-- Tables populated by the KNIME write-back steps.
CREATE TABLE IF NOT EXISTS user_segments (
    user_id INT UNSIGNED NOT NULL,
    cluster_id INT NOT NULL,
    segment_name VARCHAR(100) NOT NULL,
    distance_to_centroid DECIMAL(18,8) NULL,
    model_version VARCHAR(50) NOT NULL,
    model_run_date DATETIME NOT NULL,
    PRIMARY KEY (user_id),
    INDEX idx_user_segments_cluster (cluster_id),
    INDEX idx_user_segments_version (model_version)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS rating_predictions (
    rating_id BIGINT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    movie_id INT UNSIGNED NOT NULL,
    cluster_id INT NOT NULL,
    actual_liked TINYINT UNSIGNED NOT NULL,
    predicted_liked TINYINT UNSIGNED NOT NULL,
    probability_liked DECIMAL(10,8) NOT NULL,
    data_split VARCHAR(5) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    model_run_date DATETIME NOT NULL,
    PRIMARY KEY (rating_id, model_version),
    INDEX idx_predictions_movie (movie_id),
    INDEX idx_predictions_cluster (cluster_id),
    INDEX idx_predictions_split (data_split),
    INDEX idx_predictions_version (model_version)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS model_metrics (
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    split_name VARCHAR(10) NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    metric_value DECIMAL(18,8) NOT NULL,
    run_timestamp DATETIME NOT NULL,
    PRIMARY KEY (model_name, model_version, split_name, metric_name)
) ENGINE = InnoDB;
```

### Vì sao tạo index ngay trong `CREATE TABLE`?

- Trên máy thực tế (`innodb_buffer_pool_size` = 128M), một lệnh `CREATE INDEX` riêng trên 10M rows có sẵn chạy quá giới hạn 900 giây của Workbench (Error 2013).
- Khai báo index ngay trên bảng rỗng để MySQL xây index trong lúc `LOAD DATA`, không còn một lệnh DDL dài riêng.
- Nếu database cũ thiếu index, `01_create_schema.py` thêm từng index một bằng `ALGORITHM=INPLACE, LOCK=NONE` và tự kiểm tra lại nếu mất kết nối.
- Chỉ giữ index mà query thực sự dùng: `user_id`, `movie_id`, `rating_ts` trên `ratings`; `user_id`, `movie_id` trên `tags`.

**Bằng chứng cần chụp:** cây schema trong Workbench, `SHOW CREATE TABLE ratings;` (thấy keys và indexes).

---

## 9. Import MovieLens vào MySQL

### 9.1 Chuẩn bị (làm một lần)

1. Bật `LOCAL INFILE` trên server (cần quyền admin):

   ```sql
   SET GLOBAL local_infile = 1;
   ```

2. Trong Workbench: **Database → Manage Connections →** chọn connection **→ Advanced →** ô *Others* thêm dòng `OPT_LOCAL_INFILE=1` → reconnect.
3. Tăng timeout của Workbench: **Edit → Preferences → SQL Editor →** *DBMS connection read timeout interval* = `0` (không giới hạn) hoặc `3600`. Nếu vẫn bị Error 2013, chạy bằng Python (section 6.3).

### 9.2 Load dữ liệu

**Làm gì:** sửa ba đường dẫn trong `sql/02_load_data.sql` cho đúng máy của bạn (dùng dấu `/`), rồi chạy toàn bộ. Hoặc chạy `py .\python_sql_scripts\02_load_data.py` (tự lấy đường dẫn `data/ml-10M100K`).

> **Cảnh báo:** `LOAD DATA` ghi **thêm** vào bảng. Chạy lại trên bảng đã có dữ liệu sẽ nhân đôi số dòng. Bản Python tự bỏ qua bảng đã có dữ liệu. Muốn nạp lại có chủ đích: `py .\python_sql_scripts\02_load_data.py --reload` (xoá sạch `movies`, `ratings`, `tags`, `movie_genres` rồi nạp lại), sau đó chạy lại bước 04 và 05.

```sql
USE movielens_strategy;

-- Optional, requires the appropriate server privilege:
-- SET GLOBAL local_infile = 1;

LOAD DATA LOCAL INFILE 'C:/Users/doubl/Documents/movielens-content-strategy/data/ml-10M100K/movies.dat'
INTO TABLE movies
CHARACTER SET utf8mb4
FIELDS TERMINATED BY '::'
LINES TERMINATED BY '\n'
(@movie_id, @title, @genres)
SET
    movie_id = CAST(@movie_id AS UNSIGNED),
    title = @title,
    genres = TRIM(TRAILING '\r' FROM @genres);

LOAD DATA LOCAL INFILE 'C:/Users/doubl/Documents/movielens-content-strategy/data/ml-10M100K/ratings.dat'
INTO TABLE ratings
CHARACTER SET utf8mb4
FIELDS TERMINATED BY '::'
LINES TERMINATED BY '\n'
(@user_id, @movie_id, @rating, @rating_ts)
SET
    user_id = CAST(@user_id AS UNSIGNED),
    movie_id = CAST(@movie_id AS UNSIGNED),
    rating = CAST(@rating AS DECIMAL(2,1)),
    rating_ts = CAST(TRIM(TRAILING '\r' FROM @rating_ts) AS UNSIGNED);

LOAD DATA LOCAL INFILE 'C:/Users/doubl/Documents/movielens-content-strategy/data/ml-10M100K/tags.dat'
INTO TABLE tags
CHARACTER SET utf8mb4
FIELDS TERMINATED BY '::'
LINES TERMINATED BY '\n'
(@user_id, @movie_id, @tag_text, @tag_ts)
SET
    user_id = CAST(@user_id AS UNSIGNED),
    movie_id = CAST(@movie_id AS UNSIGNED),
    tag_text = @tag_text,
    tag_ts = CAST(TRIM(TRAILING '\r' FROM @tag_ts) AS UNSIGNED);

-- One row per (movie, genre). The Python script splits the same '|' list in
-- Python; both produce identical rows. INSERT IGNORE makes it safe to rerun.
INSERT IGNORE INTO movie_genres (movie_id, genre)
SELECT
    m.movie_id,
    jt.genre
FROM movies AS m
JOIN JSON_TABLE(
    CONCAT('["', REPLACE(m.genres, '|', '","'), '"]'),
    '$[*]' COLUMNS (
        genre VARCHAR(50) PATH '$'
    )
) AS jt;

SELECT 'movies' AS table_name, COUNT(*) AS row_count FROM movies
UNION ALL SELECT 'ratings', COUNT(*) FROM ratings
UNION ALL SELECT 'tags', COUNT(*) FROM tags
UNION ALL SELECT 'movie_genres', COUNT(*) FROM movie_genres;
```

Bảng `movie_genres` tách cột `genres` (dạng `Action|Comedy`) thành từng dòng `(movie_id, genre)`. Bản Python tách bằng Python và ghi bằng `INSERT IGNORE`; hai cách cho ra cùng các dòng.

**Kết quả mong đợi:**

| Bảng | Số dòng |
|---|---:|
| movies | 10,681 |
| ratings | 10,000,054 |
| tags | 95,580 |
| movie_genres | 21,564 |

**Bằng chứng cần chụp:** kết quả query đếm số dòng cuối file.

---

## 10. Kiểm tra chất lượng dữ liệu

**Làm gì:** chạy `sql/03_quality_checks.sql` (hoặc `py .\python_sql_scripts\03_quality_checks.py`, kết quả nằm trong `results/03_quality_checks_results.xlsx`).

Phần 1 trùng với script Python. Phần 2 là bằng chứng bổ sung, chỉ chạy trong Workbench.

```sql
USE movielens_strategy;

-- =====================================================================
-- 1. Core checks (same queries as the Python pipeline)
-- =====================================================================

-- Row counts
SELECT
    (SELECT COUNT(*) FROM ratings) AS rating_rows,
    (SELECT COUNT(*) FROM movies) AS movie_rows,
    (SELECT COUNT(*) FROM tags) AS tag_rows,
    (SELECT COUNT(DISTINCT user_id) FROM ratings) AS users,
    (SELECT COUNT(DISTINCT movie_id) FROM ratings) AS rated_movies;

-- Rating range
SELECT
    MIN(rating) AS minimum_rating,
    MAX(rating) AS maximum_rating,
    AVG(rating) AS average_rating
FROM ratings;

-- Rating period
SELECT
    FROM_UNIXTIME(MIN(rating_ts)) AS first_rating,
    FROM_UNIXTIME(MAX(rating_ts)) AS last_rating
FROM ratings;

-- Rating distribution
SELECT
    rating,
    COUNT(*) AS rating_count
FROM ratings
GROUP BY rating
ORDER BY rating;

-- Orphan ratings
SELECT COUNT(*) AS orphan_ratings
FROM ratings AS r
LEFT JOIN movies AS m ON m.movie_id = r.movie_id
WHERE m.movie_id IS NULL;

-- Orphan tags
SELECT COUNT(*) AS orphan_tags
FROM tags AS t
LEFT JOIN movies AS m ON m.movie_id = t.movie_id
WHERE m.movie_id IS NULL;

-- Duplicate user/movie pairs (sample).
-- ~10M distinct groups overflow the in-memory temp table; SQL_BIG_RESULT
-- makes MySQL group by sorting instead of a disk-based temp table.
SELECT SQL_BIG_RESULT
    user_id,
    movie_id,
    COUNT(*) AS duplicate_count
FROM ratings
GROUP BY user_id, movie_id
HAVING COUNT(*) > 1
ORDER BY user_id, movie_id
LIMIT 20;

-- Invalid rows (one scan for both checks)
SELECT
    SUM(rating NOT BETWEEN 0.5 AND 5.0 OR MOD(rating * 10, 5) <> 0) AS invalid_rating_rows,
    SUM(rating_ts = 0) AS invalid_timestamp_rows
FROM ratings;

-- Users below 20 ratings (MovieLens guarantees >= 20)
SELECT COUNT(*) AS users_below_minimum_history
FROM (
    SELECT user_id
    FROM ratings
    GROUP BY user_id
    HAVING COUNT(*) < 20
) AS user_counts;

-- =====================================================================
-- 2. Additional evidence (Workbench only, not in the Python pipeline)
-- =====================================================================

-- Completeness: NULL or empty values
SELECT
    SUM(title IS NULL OR TRIM(title) = '') AS empty_titles,
    SUM(genres IS NULL OR TRIM(genres) = '') AS empty_genres,
    SUM(genres = '(no genres listed)') AS no_genre_movies,
    SUM(title NOT REGEXP '\\([0-9]{4}\\)[[:space:]]*$') AS titles_without_year
FROM movies;

SELECT
    SUM(tag_text IS NULL OR TRIM(tag_text) = '') AS empty_tags,
    COUNT(DISTINCT LOWER(TRIM(tag_text))) AS distinct_tags_normalised,
    COUNT(DISTINCT tag_text) AS distinct_tags_raw
FROM tags;

-- Uniqueness: total number of duplicated user-movie pairs
SELECT COUNT(*) AS duplicate_pairs
FROM (
    SELECT SQL_BIG_RESULT user_id, movie_id
    FROM ratings
    GROUP BY user_id, movie_id
    HAVING COUNT(*) > 1
) AS d;

-- Plausibility / outliers
SELECT COUNT(*) AS movies_with_lt_5_ratings
FROM (
    SELECT movie_id
    FROM ratings
    GROUP BY movie_id
    HAVING COUNT(*) < 5
) AS x;

SELECT
    MAX(c) AS max_ratings_per_user,
    AVG(c) AS avg_ratings_per_user
FROM (
    SELECT COUNT(*) AS c
    FROM ratings
    GROUP BY user_id
) AS u;

-- Consistency: movies without any rating
SELECT COUNT(*) AS movies_without_ratings
FROM movies AS m
WHERE NOT EXISTS (
    SELECT 1 FROM ratings AS r WHERE r.movie_id = m.movie_id
);
```

**Kết quả mong đợi:**

- `rating_rows` = 10,000,054; `users` = 69,878; `rated_movies` = 10,677.
- Rating nằm trong 0.5 – 5.0, `invalid_rating_rows` = 0.
- Không có orphan movie ID (`orphan_ratings` = 0, `orphan_tags` = 0).
- Không có cặp user–movie trùng. Nếu có, phải xác định đó là rating update hay duplicate trước khi loại.

**Bằng chứng cần chụp:** số dòng ratings, rating distribution, khoảng thời gian dataset, kết quả orphan/invalid.

---

## 11. Chia TRAIN / VALIDATION / TEST theo thời gian

Không random split, vì mục tiêu là dự báo tương lai từ lịch sử. Mọi rating được sắp theo `(rating_ts, rating_id)` rồi chia:

| Split | Tỷ lệ | Vai trò |
|---|---:|---|
| TRAIN | 70% (7,000,042 dòng) | Tạo feature tables, train mô hình |
| VALID | 15% (1,500,006 dòng) | Chọn threshold, chỉnh feature, kiểm tra overfitting |
| TEST | 15% (1,500,006 dòng) | Đánh giá cuối cùng, **chỉ chạy một lần** |

> Không dùng TEST để chọn K, chọn threshold hay chỉnh feature.

**Làm gì:** chạy `sql/04_create_splits.sql` (hoặc `py .\python_sql_scripts\04_create_splits.py`).

**Cách hoạt động:** ban đầu dùng `NTILE(20) OVER (ORDER BY rating_ts, rating_id)`, nhưng window function trên 10M rows chạy quá 900 giây. Bản hiện tại cho **đúng cùng kết quả** với `NTILE(20)` (bucket 1–14 TRAIN, 15–17 VALID, 18–20 TEST) nhưng nhanh hơn nhiều:

1. tính số dòng của TRAIN/VALID theo đúng công thức của NTILE;
2. đọc 2 dòng ranh giới `(rating_ts, rating_id)` từ `idx_ratings_ts` (index này đã sắp đúng thứ tự đó);
3. gán nhãn bằng `CASE` trong một lần quét, ghi vào bảng staging đã có key;
4. kiểm tra số dòng, rồi `RENAME TABLE` một lần. Bảng cũ được giữ lại là `rating_split_previous` (bản Python giữ thành `rating_split_backup_<timestamp>`).

Đã kiểm tra trên dữ liệu thật: nhãn của cách mới khớp 100% với bảng tạo bằng Python (0 dòng lệch).

```sql
USE movielens_strategy;

-- 1. Bucket sizes exactly as NTILE(20) assigns them: the first
--    (total MOD 20) buckets each receive one extra row.
SELECT COUNT(*) INTO @total FROM ratings;
SET @bucket_size = @total DIV 20;  -- integer: LIMIT/OFFSET ? rejects DECIMAL
SET @remainder = MOD(@total, 20);
SET @train_rows = 14 * @bucket_size + LEAST(@remainder, 14);
SET @valid_rows = 3 * @bucket_size + GREATEST(0, LEAST(@remainder - 14, 3));

-- 2. Last (rating_ts, rating_id) of TRAIN and of VALID.
SET @train_offset = @train_rows - 1;
SET @valid_offset = @train_rows + @valid_rows - 1;
PREPARE find_boundary FROM
    'SELECT rating_ts, rating_id INTO @boundary_ts, @boundary_id
     FROM ratings ORDER BY rating_ts, rating_id LIMIT 1 OFFSET ?';
EXECUTE find_boundary USING @train_offset;
SET @train_end_ts = @boundary_ts, @train_end_id = @boundary_id;
EXECUTE find_boundary USING @valid_offset;
SET @valid_end_ts = @boundary_ts, @valid_end_id = @boundary_id;
DEALLOCATE PREPARE find_boundary;

SELECT
    @total AS total_rows,
    @train_rows AS train_rows,
    @valid_rows AS valid_rows,
    @total - @train_rows - @valid_rows AS test_rows;

-- 3. Build into a staging table that already has its keys.
DROP TABLE IF EXISTS rating_split_staging;

CREATE TABLE rating_split_staging (
    rating_id BIGINT UNSIGNED NOT NULL,
    data_split VARCHAR(5) NOT NULL,
    PRIMARY KEY (rating_id),
    INDEX idx_rating_split_name (data_split)
) ENGINE = InnoDB;

INSERT INTO rating_split_staging (rating_id, data_split)
SELECT
    rating_id,
    CASE
        WHEN rating_ts < @train_end_ts
          OR (rating_ts = @train_end_ts AND rating_id <= @train_end_id) THEN 'TRAIN'
        WHEN rating_ts < @valid_end_ts
          OR (rating_ts = @valid_end_ts AND rating_id <= @valid_end_id) THEN 'VALID'
        ELSE 'TEST'
    END
FROM ratings;

-- 4. Validate: staged_rows must equal total_rows (is_valid = 1).
--    Do NOT run step 5 if is_valid = 0.
SELECT
    COUNT(*) AS staged_rows,
    @total AS total_rows,
    COUNT(*) = @total AS is_valid
FROM rating_split_staging;

-- 5. Publish atomically; the former table is kept as rating_split_previous
--    for rollback. CREATE ... LIKE makes the RENAME work on the first run.
DROP TABLE IF EXISTS rating_split_previous;
CREATE TABLE IF NOT EXISTS rating_split LIKE rating_split_staging;
RENAME TABLE
    rating_split TO rating_split_previous,
    rating_split_staging TO rating_split;

-- 6. Split summary
SELECT
    s.data_split,
    COUNT(*) AS rows_in_split,
    FROM_UNIXTIME(MIN(r.rating_ts)) AS period_start,
    FROM_UNIXTIME(MAX(r.rating_ts)) AS period_end
FROM rating_split AS s
JOIN ratings AS r ON r.rating_id = s.rating_id
GROUP BY s.data_split
ORDER BY MIN(r.rating_ts);
```

**Bằng chứng cần chụp:** bảng split summary (số dòng và khoảng thời gian của từng split).

---

## 12. Tạo feature tables chỉ từ TRAIN

Mọi profile phải tạo từ TRAIN để không "nhìn thấy tương lai" (data leakage).

**Làm gì:** chạy `sql/05_feature_tables.sql` (hoặc `py .\python_sql_scripts\05_feature_tables.py`).

**Cách hoạt động:**

- Mỗi bảng được xây vào bảng `*_staging` đã có sẵn primary key/index.
- Kiểm tra số dòng > 0, rồi cả ba bảng được đổi tên cùng lúc bằng một lệnh `RENAME TABLE`. Bảng cũ giữ lại là `*_previous` (bản Python: `*_backup_<timestamp>`) để rollback.
- `STRAIGHT_JOIN` bắt MySQL đi từ `rating_split` sang `ratings` theo thứ tự primary key thay vì tra cứu ngẫu nhiên.

```sql
USE movielens_strategy;

-- Disable the server-side statement time limit for this session.
SET SESSION max_execution_time = 0;

-- =====================================================================
-- 12.0 User segments write-back target
-- =====================================================================
-- KNIME writes the K-Means clustering result into this table after this
-- script completes. Recreate it so every feature-table run starts with a
-- clean target for the next model run.
DROP TABLE IF EXISTS user_segments;

CREATE TABLE user_segments (
    user_id INT UNSIGNED NOT NULL,
    cluster_id INT NOT NULL,
    segment_name VARCHAR(100) NOT NULL,
    distance_to_centroid DECIMAL(18,8) NULL,
    model_version VARCHAR(50) NOT NULL,
    model_run_date DATETIME NOT NULL,
    PRIMARY KEY (user_id),
    INDEX idx_user_segments_cluster (cluster_id),
    INDEX idx_user_segments_version (model_version)
) ENGINE = InnoDB;
```

### 12.1 User statistics — `train_user_stats`

Một dòng cho mỗi user: số rating, trung bình, độ lệch chuẩn, tỷ lệ positive, số phim, số ngày hoạt động.

```sql
DROP TABLE IF EXISTS train_user_stats_staging;

CREATE TABLE train_user_stats_staging (
    user_id INT UNSIGNED NOT NULL,
    rating_count BIGINT UNSIGNED NOT NULL,
    rating_sum DECIMAL(20,2) NOT NULL,
    avg_rating DOUBLE NOT NULL,
    rating_stddev DOUBLE NULL,
    positive_count BIGINT UNSIGNED NOT NULL,
    positive_rate DOUBLE NOT NULL,
    distinct_movies BIGINT UNSIGNED NOT NULL,
    first_rating_ts INT UNSIGNED NOT NULL,
    last_rating_ts INT UNSIGNED NOT NULL,
    active_days INT NOT NULL,
    PRIMARY KEY (user_id)
) ENGINE = InnoDB;

-- STRAIGHT_JOIN drives from rating_split, so ratings are read in primary-key
-- order instead of random lookups.
INSERT INTO train_user_stats_staging
SELECT
    r.user_id,
    COUNT(*),
    SUM(r.rating),
    AVG(r.rating),
    STDDEV_SAMP(r.rating),
    SUM(r.rating >= 4.0),
    AVG(r.rating >= 4.0),
    COUNT(DISTINCT r.movie_id),
    MIN(r.rating_ts),
    MAX(r.rating_ts),
    DATEDIFF(FROM_UNIXTIME(MAX(r.rating_ts)), FROM_UNIXTIME(MIN(r.rating_ts)))
FROM rating_split AS s
STRAIGHT_JOIN ratings AS r ON r.rating_id = s.rating_id
WHERE s.data_split = 'TRAIN'
GROUP BY r.user_id;
```

### 12.2 Movie statistics — `train_movie_stats`

```sql
DROP TABLE IF EXISTS train_movie_stats_staging;

CREATE TABLE train_movie_stats_staging (
    movie_id INT UNSIGNED NOT NULL,
    rating_count BIGINT UNSIGNED NOT NULL,
    rating_sum DECIMAL(20,2) NOT NULL,
    avg_rating DOUBLE NOT NULL,
    rating_stddev DOUBLE NULL,
    positive_count BIGINT UNSIGNED NOT NULL,
    positive_rate DOUBLE NOT NULL,
    distinct_users BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (movie_id)
) ENGINE = InnoDB;

INSERT INTO train_movie_stats_staging
SELECT
    r.movie_id,
    COUNT(*),
    SUM(r.rating),
    AVG(r.rating),
    STDDEV_SAMP(r.rating),
    SUM(r.rating >= 4.0),
    AVG(r.rating >= 4.0),
    COUNT(DISTINCT r.user_id)
FROM rating_split AS s
STRAIGHT_JOIN ratings AS r ON r.rating_id = s.rating_id
WHERE s.data_split = 'TRAIN'
GROUP BY r.movie_id;
```

### 12.3 User-genre statistics — `train_user_genre_stats`, kiểm tra và publish

```sql
DROP TABLE IF EXISTS train_user_genre_stats_staging;

CREATE TABLE train_user_genre_stats_staging (
    user_id INT UNSIGNED NOT NULL,
    genre VARCHAR(50) NOT NULL,
    genre_rating_count BIGINT UNSIGNED NOT NULL,
    genre_avg_rating DOUBLE NOT NULL,
    genre_positive_rate DOUBLE NOT NULL,
    PRIMARY KEY (user_id, genre),
    INDEX idx_user_genre_genre (genre)
) ENGINE = InnoDB;

INSERT INTO train_user_genre_stats_staging
SELECT
    r.user_id,
    mg.genre,
    COUNT(*),
    AVG(r.rating),
    AVG(r.rating >= 4.0)
FROM rating_split AS s
STRAIGHT_JOIN ratings AS r ON r.rating_id = s.rating_id
STRAIGHT_JOIN movie_genres AS mg ON mg.movie_id = r.movie_id
WHERE s.data_split = 'TRAIN'
GROUP BY r.user_id, mg.genre;

-- Validate: every count must be > 0 before publishing.
SELECT
    (SELECT COUNT(*) FROM train_user_stats_staging) AS user_rows,
    (SELECT COUNT(*) FROM train_movie_stats_staging) AS movie_rows,
    (SELECT COUNT(*) FROM train_user_genre_stats_staging) AS user_genre_rows;

-- Publish all three tables in one atomic RENAME.
DROP TABLE IF EXISTS train_user_stats_previous, train_movie_stats_previous,
                     train_user_genre_stats_previous;
CREATE TABLE IF NOT EXISTS train_user_stats LIKE train_user_stats_staging;
CREATE TABLE IF NOT EXISTS train_movie_stats LIKE train_movie_stats_staging;
CREATE TABLE IF NOT EXISTS train_user_genre_stats LIKE train_user_genre_stats_staging;
RENAME TABLE
    train_user_stats TO train_user_stats_previous,
    train_user_stats_staging TO train_user_stats,
    train_movie_stats TO train_movie_stats_previous,
    train_movie_stats_staging TO train_movie_stats,
    train_user_genre_stats TO train_user_genre_stats_previous,
    train_user_genre_stats_staging TO train_user_genre_stats;
```

### 12.4 KPI SQL queries cho rubric

Bốn query minh hoạ **filter, group/aggregate, join + KPI, minimum support**. Chỉ chạy riêng 4 query này (không xây lại feature tables):

```powershell
py .\python_sql_scripts\05_feature_tables.py --queries-only
```

Kết quả nằm trong `python_sql_scripts/results/05_feature_tables_results.xlsx`.

> **Query 3 đã được tối ưu.** Bản đầu nối từng rating với `movie_genres` (~20M dòng sau join) và bị treo trong Workbench. Bản hiện tại gom 10M ratings theo phim trước (~10.7K dòng, một lần quét tuần tự), rồi mới nối sang genre. Kết quả giống hệt vì count, sum và positive count cộng dồn được: `AVG = SUM(sum) / SUM(count)`. Thời gian đo thực tế: khoảng 13 giây.
>
> Không cần tạo thêm `idx_ratings_movie_id` hay `idx_movie_genres_movie_id`: `idx_ratings_movie` và primary key `(movie_id, genre)` đã đảm nhiệm việc đó.

```sql
-- 1. Filtering
SELECT *
FROM ratings
WHERE rating >= 4.0
  AND rating_ts >= UNIX_TIMESTAMP('2005-01-01')
LIMIT 100;

-- 2. Grouping / aggregation
SELECT
    rating,
    COUNT(*) AS rating_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS rating_percent
FROM ratings
GROUP BY rating
ORDER BY rating;

-- 3. Join + KPI by genre.
-- Aggregate 10M ratings to ~10.7K movie rows in one sequential scan, then fan
-- out to genres. Same result as joining every rating to movie_genres
-- (~20M joined rows), because count, sum and positive count are additive:
-- AVG = SUM(sum) / SUM(count). NO_INDEX keeps the inner GROUP BY on a
-- sequential scan instead of 10M random primary-key lookups through
-- idx_ratings_movie (which does not contain rating).
SELECT
    mg.genre,
    CAST(SUM(ma.rating_count) AS UNSIGNED) AS rating_count,
    SUM(ma.rating_sum) / SUM(ma.rating_count) AS avg_rating,
    SUM(ma.positive_count) / SUM(ma.rating_count) AS positive_rate
FROM (
    SELECT /*+ NO_INDEX(ratings) */
        movie_id,
        COUNT(*) AS rating_count,
        SUM(rating) AS rating_sum,
        SUM(rating >= 4.0) AS positive_count
    FROM ratings
    GROUP BY movie_id
) AS ma
JOIN movie_genres AS mg ON mg.movie_id = ma.movie_id
GROUP BY mg.genre
ORDER BY rating_count DESC;

-- 4. Movie popularity with minimum support
SELECT
    m.movie_id,
    m.title,
    ms.rating_count,
    ms.avg_rating,
    ms.positive_rate
FROM train_movie_stats AS ms
JOIN movies AS m ON m.movie_id = ms.movie_id
WHERE ms.rating_count >= 100
ORDER BY ms.avg_rating DESC, ms.rating_count DESC
LIMIT 20;
```

**Bằng chứng cần chụp:** kết quả và thời gian chạy (Action Output) của từng query.

---

# PHASE B — KNIME MODEL 1: K-MEANS

> **Quy ước khi đọc các bảng node:**
> - **Node** = tên node trong *Node Repository* (gõ tên vào ô tìm kiếm rồi kéo ra canvas).
> - Sau khi kéo node, nối cổng output (tam giác bên phải) của node trước vào cổng input của node sau.
> - Cấu hình: double-click node (hoặc chuột phải → *Configure*). Chạy: chuột phải → *Execute* (`F7`). Đèn xanh = chạy xong.
> - Đổi tên node: click vào dòng chữ dưới node, gõ tên mới như cột **Tên node** (rubric chấm tên node và annotation).
> - Annotation: chuột phải trên canvas → *New Workflow Annotation*, kéo khung bao quanh nhóm node, ghi mục đích của nhóm.

## 13. Chuẩn bị KNIME và kết nối MySQL

### 13.1 Tạo workflow

1. Mở KNIME Analytics Platform.
2. Trong *KNIME Explorer* (hoặc *Space Explorer*): chuột phải *LOCAL* → **New KNIME Workflow** → đặt tên `movielens_audience_segmentation`.
3. Ghi một workflow annotation ở góc trên: tên project, database `movielens_strategy`, mục tiêu workflow, ngày chạy.

### 13.2 Khai báo credential (không lưu password trong workflow)

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 0 | **Credentials Configuration** | `00 MySQL Credentials` | *Credential identifier*: `mysql_local` · *User name*: tài khoản MySQL · bỏ chọn *Save password in configuration* (mỗi lần mở workflow sẽ hỏi password) |

### 13.3 Kết nối MySQL

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 1 | **MySQL Connector** | `01 Connect to MovieLens MySQL` | Tab *Connection Settings*: Hostname `localhost`, Port `3306`, Database name `movielens_strategy` · *Authentication*: chọn **Credentials** → `mysql_local` |

Nối cổng flow variable (chấm đỏ) của node 0 vào node 1: chuột phải node 1 → *Show Flow Variable Ports*, kéo dây từ node 0.

Execute node 1. Đèn xanh = kết nối thành công. Lỗi thường gặp:

| Lỗi | Cách sửa |
|---|---|
| `Access denied` | Sai user/password trong node 0 |
| `Communications link failure` | MySQL Server chưa chạy (Services → `MySQL80` → Start) |
| `Unknown database` | Chưa chạy bước 01 (section 8) |

**Bằng chứng cần chụp:** MySQL Connector đèn xanh; danh sách bảng trong Workbench.

---

## 14. Workflow K-Means từng node

### 14.0 Sơ đồ tổng thể

```text
00 Credentials → 01 MySQL Connector
                   ├─ 02 Read TRAIN User Statistics ─ 04 Fill Missing Stddev ─ 05 Log-transform Counts ─┐
                   └─ 03 Read TRAIN Genre Statistics ─ 06 Pivot Genres to User Level ──────────────────┤
                                                                                                         07 Join User + Genre
                                                                                                         08 Build Genre Affinity
                                                                                                         09 Fill Missing Affinity
                                                                                                         10 Z-score Normalization
                                                                                                         11 K-Means (K = 3..8)
                                                                                                         12 Sample for Silhouette → 13 Silhouette
                                                                                                         14 Profile Clusters
                                                                                                         15 Attach Segment Labels
                                                                                                         16 Write User Segments to MySQL
```

### 14.1 Đọc dữ liệu từ MySQL

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 2 | **DB Table Selector** → **DB Reader** | `02 Read TRAIN User Statistics` | Table Selector: *Select a table* → `train_user_stats`. DB Reader: không cần cấu hình |
| 3 | **DB Table Selector** → **DB Reader** | `03 Read TRAIN Genre Statistics` | Table Selector: `train_user_genre_stats` |

Hai node *DB Table Selector* đều nối từ cổng DB (hình vuông nâu) của node 1. *DB Reader* mới thực sự kéo dữ liệu về KNIME.

Cột dùng cho clustering (từ `train_user_stats`): `rating_count`, `avg_rating`, `rating_stddev`, `positive_rate`, `distinct_movies`, `active_days`. Giữ `user_id` để join, nhưng **không** đưa vào K-Means. Không dùng `rating_sum`, `positive_count`, timestamps vì trùng ý nghĩa hoặc scale lớn.

### 14.2 Làm sạch và biến đổi user features

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 4 | **Missing Value** | `04 Fill Missing Stddev` | Tab *Column Settings*: `rating_stddev` → *Fix Value* `0` (user chỉ có 1 rating TRAIN thì không có độ lệch chuẩn) |
| 5 | **Math Formula** (3 node nối tiếp) | `05 Log-transform Counts` | Expression `ln(1 + $rating_count$)`, chọn *Replace Column* `rating_count`. Lặp lại cho `distinct_movies` và `active_days` |

Log-transform kéo các user hoạt động cực nhiều về gần nhóm chính, nên K-Means không bị outlier chi phối. (Cách khác: node **Numeric Outliers** với *Treatment* = *Replace outlier values → Closest value* để winsorize.) Ghi rõ lựa chọn này trong report.

### 14.3 Genre affinity

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 6 | **Pivot** | `06 Pivot Genres to User Level` | *Groups*: `user_id` · *Pivots*: `genre` · *Manual Aggregation*: `genre_avg_rating`, method **First** · *Column name*: chọn **Pivot name** (mỗi cột tên đúng bằng genre, ví dụ `Action`) |
| 7 | **Joiner** | `07 Join User + Genre` | Input trên: output node 5 · input dưới: output node 6 · *Join columns*: `user_id` = `user_id` · *Include in output*: **Matching rows** |
| 8 | **Math Formula (Multi Column)** | `08 Build Genre Affinity` | Chọn tất cả cột genre (bỏ `(no genres listed)`, `IMAX` nếu muốn) · Expression `$$CURRENTCOLUMN$$ - $avg_rating$` · *Replace selected columns* |
| 9 | **Missing Value** | `09 Fill Missing Affinity` | Mọi cột Number → *Fix Value* `0` |

Ý nghĩa:

```text
genre_affinity = genre_avg_rating − user_avg_rating
  > 0 : user chấm thể loại này cao hơn mức trung bình của chính họ
  = 0 : chưa rating thể loại này (không có bằng chứng) hoặc trung tính
```

Nếu muốn phân biệt "trung tính" và "không có bằng chứng", thêm `genre_rating_count` vào pivot làm cột phụ.

### 14.4 Chuẩn hoá và chạy K-Means

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 10 | **Normalizer** | `10 Z-score Normalization` | *Normalization method*: **Z-Score Normalization (Gaussian)** · chọn tất cả cột feature, **bỏ** `user_id` |
| 11 | **k-Means** | `11 K-Means K=4` | *Number of clusters*: `4` · *Centroid initialization*: Random, tick **Use static random seed** (ví dụ `42`) · *Max. number of iterations*: `300` · *Column selection*: tất cả feature, **bỏ** `user_id` |

Output 1 của k-Means có thêm cột `Cluster` (giá trị `cluster_0`, `cluster_1`, …). Output 2 là toạ độ tâm cụm.

### 14.5 Chọn K

Thử `K = 3, 4, 5, 6, 7, 8`. Cách dễ chụp và so sánh nhất: copy node 11 thành 6 nhánh, mỗi nhánh một K (hoặc dùng **Parameter Optimization Loop Start/End** nếu đã quen).

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 12 | **Row Sampling** | `12 Sample for Silhouette` | *Absolute*: `10000` · *Draw randomly*, seed `42` |
| 13 | **Silhouette Coefficient** | `13 Silhouette K=4` | *Cluster column*: `Cluster` · *Include*: các cột feature đã chuẩn hoá |

> Silhouette tính khoảng cách giữa mọi cặp điểm. Trên 69K user là ~4.8 tỷ cặp, rất chậm. Lấy mẫu 10,000 user (seed cố định) là đủ để so sánh các K.

Với mỗi K, ghi lại vào một bảng so sánh:

| K | Silhouette (mean) | Cỡ cluster nhỏ nhất / lớn nhất | Giải thích được bằng ngôn ngữ kinh doanh? | Ổn định khi đổi seed? |
|---:|---:|---|---|---|
| 3 | | | | |
| … | | | | |

Không chọn K chỉ vì silhouette cao nhất. Chọn K có silhouette chấp nhận được **và** tạo segment có thể hành động.

Lưu silhouette từng K vào MySQL để vẽ trên dashboard (Page 5): xem 15.3.

### 14.6 Profile cluster và đặt tên segment

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 14a | **Joiner** | `14 Join Cluster to Raw Features` | Nối cột `user_id`, `Cluster` (output node 11 của K đã chọn) với bảng **trước khi chuẩn hoá** (output node 9), để xem giá trị gốc dễ hiểu |
| 14b | **GroupBy** | `14 Profile Clusters` | *Group*: `Cluster` · *Manual Aggregation*: **Mean** cho các feature, **Count** cho `user_id` |

Đọc bảng profile rồi mới đặt tên. Ví dụ tên có thể xuất hiện: *Diverse Explorers*, *Mainstream Enthusiasts*, *Selective Critics*, *Genre Specialists*, *Casual Raters*. **Không** đặt tên trước khi xem profile thực tế.

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 15a | **Rule Engine** | `15 Attach Segment Labels` | Ví dụ: `$Cluster$ = "cluster_0" => "Selective Critics"` · `$Cluster$ = "cluster_1" => "Mainstream Enthusiasts"` · … · `TRUE => "Unlabelled"` · *Append column*: `segment_name` |
| 15b | **String Manipulation** | `15 Cluster Number` | `toInt(replace($Cluster$, "cluster_", ""))` · *Append*: `cluster_id` (kiểu Integer) |

---

## 15. Ghi kết quả K-Means về MySQL

### 15.1 Chuẩn bị bảng output

Bảng `user_segments` đã được tạo ở bước 01 với các cột:

```text
user_id · cluster_id · segment_name · distance_to_centroid (NULL được) · model_version · model_run_date
```

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 16a | **Constant Value Column** | `16 Add Model Version` | *New column* `model_version`, String, giá trị `kmeans_v1` |
| 16b | **Constant Value Column** | `16 Add Run Date` | *New column* `model_run_date`, String, giá trị dạng `2026-10-15 10:00:00` (MySQL tự chuyển sang DATETIME) |
| 16c | **Column Filter** | `16 Keep Output Columns` | Giữ đúng: `user_id`, `cluster_id`, `segment_name`, `model_version`, `model_run_date` |

### 15.2 Ghi vào MySQL

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 16d | **DB SQL Executor** | `16 Clear Old Segments` | Nối cổng DB từ node 1 · SQL: `DELETE FROM user_segments` |
| 16e | **DB Writer** | `16 Write User Segments to MySQL` | Cổng DB: nối từ **output DB của node 16d** (để chắc chắn xoá xong mới ghi) · cổng data: output node 16c · *Table name*: `user_segments` · **bỏ chọn** *Remove existing table* (nếu không KNIME sẽ xoá bảng và tạo lại không có primary key) · *Batch size*: `10000` |

> `user_segments` có primary key `user_id`, mỗi user chỉ có một segment. Muốn giữ lịch sử nhiều phiên bản K-Means thì export bảng cũ trước khi xoá.

**Kiểm tra trong Workbench:**

```sql
SELECT * FROM user_segments LIMIT 20;

SELECT cluster_id, segment_name, COUNT(*) AS users
FROM user_segments
GROUP BY cluster_id, segment_name
ORDER BY cluster_id;
```

Tổng số users phải bằng số dòng của `train_user_stats` (54,873 trên dữ liệu hiện tại). Khoảng 15,000 user còn lại chỉ có rating trong VALID/TEST nên không có segment: đây là nhóm cold-start, bị loại khỏi `ml_rating_features`.

### 15.3 Ghi silhouette của từng K vào `model_metrics`

Để Page 5 của dashboard vẽ được biểu đồ "Silhouette theo K" từ MySQL:

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 17a | **Row Filter** (mỗi nhánh K) | `17 Overall Silhouette K=4` | Giữ dòng silhouette tổng (overall/mean) của output node 13 |
| 17b | **Constant Value Column** ×5 | `17 Metric Columns K=4` | `model_name` = `kmeans` · `model_version` = `kmeans_v1` · `split_name` = `TRAIN` · `metric_name` = `silhouette_k4` · `run_timestamp` = `2026-10-15 10:00:00` |
| 17c | **Column Rename** | `17 Rename Silhouette Value` | Cột giá trị silhouette → `metric_value` |
| 17d | **Concatenate** | `17 All K` | Gộp 6 nhánh K = 3..8 |
| 17e | **DB SQL Executor** | `17 Clear Old Silhouette` | `DELETE FROM model_metrics WHERE model_name = 'kmeans' AND model_version = 'kmeans_v1'` |
| 17f | **DB Writer** | `17 Write Silhouette to MySQL` | Table `model_metrics`, bỏ chọn *Remove existing table* |

**Bằng chứng cần chụp:** toàn bộ workflow (tên node đọc được), bảng so sánh K, bảng profile cluster, DB Writer đèn xanh, query kiểm tra trong Workbench.

---

# PHASE C — KNIME MODEL 2: LOGISTIC REGRESSION

## 16. Tạo view feature cho Logistic Regression

**Mục tiêu:**

```text
liked = 1  nếu rating >= 4.0
liked = 0  nếu rating <  4.0
```

- Feature chỉ lấy từ lịch sử TRAIN.
- Riêng các dòng TRAIN, dùng **leave-one-out** (bỏ chính rating đang dự báo ra khỏi trung bình) để tránh leakage.
- Cờ genre dùng `FIND_IN_SET`, khớp đúng tên genre (`LIKE '%War%'` sẽ khớp cả chuỗi con).

**Làm gì:** sau khi `user_segments` đã có dữ liệu (section 15), chạy `sql/06_logistic_features.sql` (hoặc `py .\python_sql_scripts\run_all.py --from-step 6 --through 6`).

```sql
USE movielens_strategy;

DROP VIEW IF EXISTS ml_rating_features;

-- TRAIN rows use leave-one-out aggregates (the row's own rating is removed);
-- VALID/TEST rows use the plain TRAIN aggregates.
-- Genre flags use FIND_IN_SET on the '|' list, which matches whole genre names
-- only (LIKE '%...%' would match any substring).
CREATE VIEW ml_rating_features AS
SELECT
    r.rating_id,
    r.user_id,
    r.movie_id,
    s.data_split,
    CASE WHEN r.rating >= 4.0 THEN 1 ELSE 0 END AS liked,

    CASE
        WHEN s.data_split = 'TRAIN' AND us.rating_count > 1
        THEN (us.rating_sum - r.rating) / (us.rating_count - 1)
        ELSE us.avg_rating
    END AS user_prior_avg_rating,
    CASE
        WHEN s.data_split = 'TRAIN' AND us.rating_count > 1
        THEN (us.positive_count - (r.rating >= 4.0)) / (us.rating_count - 1)
        ELSE us.positive_rate
    END AS user_prior_positive_rate,
    us.rating_count AS user_activity,
    us.rating_stddev AS user_rating_stddev,
    us.active_days AS user_active_days,

    CASE
        WHEN s.data_split = 'TRAIN' AND ms.rating_count > 1
        THEN (ms.rating_sum - r.rating) / (ms.rating_count - 1)
        ELSE ms.avg_rating
    END AS movie_prior_avg_rating,
    CASE
        WHEN s.data_split = 'TRAIN' AND ms.rating_count > 1
        THEN (ms.positive_count - (r.rating >= 4.0)) / (ms.rating_count - 1)
        ELSE ms.positive_rate
    END AS movie_prior_positive_rate,
    ms.rating_count AS movie_popularity,
    ms.rating_stddev AS movie_rating_stddev,
    seg.cluster_id,

    CASE WHEN FIND_IN_SET('Action', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_action,
    CASE WHEN FIND_IN_SET('Adventure', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_adventure,
    CASE WHEN FIND_IN_SET('Animation', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_animation,
    CASE WHEN FIND_IN_SET('Children', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_children,
    CASE WHEN FIND_IN_SET('Comedy', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_comedy,
    CASE WHEN FIND_IN_SET('Crime', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_crime,
    CASE WHEN FIND_IN_SET('Documentary', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_documentary,
    CASE WHEN FIND_IN_SET('Drama', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_drama,
    CASE WHEN FIND_IN_SET('Fantasy', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_fantasy,
    CASE WHEN FIND_IN_SET('Film-Noir', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_film_noir,
    CASE WHEN FIND_IN_SET('Horror', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_horror,
    CASE WHEN FIND_IN_SET('Musical', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_musical,
    CASE WHEN FIND_IN_SET('Mystery', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_mystery,
    CASE WHEN FIND_IN_SET('Romance', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_romance,
    CASE WHEN FIND_IN_SET('Sci-Fi', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_scifi,
    CASE WHEN FIND_IN_SET('Thriller', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_thriller,
    CASE WHEN FIND_IN_SET('War', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_war,
    CASE WHEN FIND_IN_SET('Western', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_western
FROM ratings AS r
JOIN rating_split AS s ON s.rating_id = r.rating_id
JOIN movies AS m ON m.movie_id = r.movie_id
JOIN train_user_stats AS us ON us.user_id = r.user_id
JOIN train_movie_stats AS ms ON ms.movie_id = r.movie_id
JOIN user_segments AS seg ON seg.user_id = r.user_id
WHERE us.rating_count > 1
  AND ms.rating_count > 1;
```

### Ghi chú cold-start

View chỉ giữ user/movie có đủ lịch sử TRAIN (`rating_count > 1`) và user đã có segment. Report phải nêu:

- mô hình đánh giá **warm-start** users và movies;
- recommendation cho cold-start nằm ngoài phạm vi;
- bao nhiêu dòng VALID/TEST bị loại vì cold-start — query dưới đây (đã có trong `06_logistic_features.sql`/`.py`) cho mỗi split: tổng số dòng, số dòng feature, số dòng và tỷ lệ bị loại.

```sql
-- Feature rows and cold-start exclusions per split (required for the report).
-- Split totals come from the small rating_split index, so this is still one
-- pass over the view.
SELECT
    t.data_split,
    t.total_rows,
    COALESCE(f.feature_rows, 0) AS feature_rows,
    t.total_rows - COALESCE(f.feature_rows, 0) AS cold_start_excluded_rows,
    (t.total_rows - COALESCE(f.feature_rows, 0)) / t.total_rows AS cold_start_excluded_rate
FROM (
    SELECT data_split, COUNT(*) AS total_rows
    FROM rating_split
    GROUP BY data_split
) AS t
LEFT JOIN (
    SELECT data_split, COUNT(*) AS feature_rows
    FROM ml_rating_features
    GROUP BY data_split
) AS f ON f.data_split = t.data_split
ORDER BY t.data_split;
```

---

## 17. Workflow Logistic Regression từng node

Tạo workflow mới `movielens_like_prediction`. Copy node `00 MySQL Credentials` và `01 Connect to MovieLens MySQL` từ workflow K-Means sang.

> **Đã có sẵn:** `knime/movielens_like_prediction.knwf` dựng đúng theo section 17–18 (49 node, đã đặt tên và annotation). Import bằng *File → Import KNIME Workflow*, mở node `01 Connect to MovieLens MySQL` nhập password MySQL (file không lưu password), rồi execute theo thứ tự trong annotation. Khác biệt so với bảng dưới: không có node Credentials Configuration và ROC Curve (AUC đã được tính bằng SQL ở 18.2; muốn có hình ROC thì thêm node *ROC Curve* nối sau node `10 Threshold`); Column Filter của bước 07 được thay bằng phần chọn feature ngay trong Learner.

### 17.0 Sơ đồ tổng thể

```text
00 Credentials → 01 MySQL Connector
   ├─ 02 Read TRAIN Sample → 03 Prepare Columns → 04 Missing Value → 05 Log-transform → 06 Normalizer → 07 Column Filter → 08 Logistic Regression Learner
   │                                                  │ (model)              │ (model)                                    │ (model, coefficients)
   ├─ 10 Read VALID ──────── 03 → 04 Apply ─────────┘ → 05 → 06 Apply ─────┘ ───────────────────────────── 11 Predictor → 12 Threshold → 13 Scorer / 14 ROC
   └─ 20 Read TEST  ──────── 03 → 04 Apply → 05 → 06 Apply ────────────────────────────────────────────── 21 Predictor → 22 Threshold → 23 Scorer / 24 ROC → 25-28 Write-back
```

### 17.1 Đọc TRAIN sample và chuẩn bị cột

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 2 | **DB Query Reader** | `02 Read TRAIN Sample` | SQL bên dưới |
| 3a | **String Manipulation** | `03 Target as Label` | `string($liked$)` · *Append*: `liked_label` (Learner cần target dạng chuỗi; giữ `liked` số nguyên để ghi về MySQL) |
| 3b | **String Manipulation** | `03 Segment as Category` | `string($cluster_id$)` · *Append*: `cluster_label` (Learner tự tạo dummy cho cột chuỗi) |

```sql
SELECT *
FROM ml_rating_features
WHERE data_split = 'TRAIN'
  AND MOD(rating_id, 5) = 0;
```

Đây là mẫu 20% cố định của TRAIN (~1.4M dòng). Máy yếu thì đổi `5` thành `10`. Ghi rõ tỷ lệ lấy mẫu trong report.

### 17.2 Preprocessing (fit trên TRAIN)

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 4 | **Missing Value** | `04 Missing Value` | `user_rating_stddev`, `movie_rating_stddev` → *Fix Value* `0` (hoặc *Median*). Output thứ 2 (PMML) là "công thức" để áp lại cho VALID/TEST |
| 5 | **Math Formula** ×3 | `05 Log-transform Counts` | `ln(1 + $user_activity$)`, `ln(1 + $movie_popularity$)`, `ln(1 + $user_active_days$)`, mỗi node *Replace Column* |
| 6 | **Normalizer (PMML)** | `06 Normalizer` | Z-Score · chỉ chọn các cột liên tục: `user_prior_avg_rating`, `user_prior_positive_rate`, `user_activity`, `user_rating_stddev`, `user_active_days`, `movie_prior_avg_rating`, `movie_prior_positive_rate`, `movie_popularity`, `movie_rating_stddev` · **không** chọn cờ `genre_*` |
| 7 | **Column Filter** | `07 Select Model Features` | **Bỏ** `rating_id`, `user_id`, `movie_id`, `data_split`, `liked`, `cluster_id` (đã có `cluster_label`) |

### 17.3 Learner

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 8 | **Logistic Regression Learner** | `08 Logistic Regression Learner` | *Target column*: `liked_label` · *Reference category*: `0` · *Solver*: **Stochastic average gradient** · *Perform regularization*: Gauss prior (L2), variance `1` · *Maximal number of epochs*: `100` (tăng nếu cảnh báo chưa hội tụ) |

Output 2 của Learner là **coefficient table** (`Variable`, `Coeff.`, `Std. Err.`, `z-score`, `P>|z|`). Lưu bảng này để diễn giải và ghi về MySQL (18.3).

### 17.4 Validation

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 10 | **DB Query Reader** | `10 Read VALID` | `SELECT * FROM ml_rating_features WHERE data_split = 'VALID'` |
| — | copy node 3a, 3b, 5 | | Cấu hình giữ nguyên |
| 10b | **Missing Value (Apply)** | `10 Apply Missing Value` | Input model: output PMML của node 4 |
| 10c | **Normalizer Apply (PMML)** | `10 Apply Normalizer` | Input model: output PMML của node 6 (**không** fit lại trên VALID) |
| 11 | **Logistic Regression Predictor** | `11 Predict VALID` | Model: output 1 của node 8 · tick **Append columns with predicted probabilities** → có cột `P (liked_label=1)` |
| 12 | **Rule Engine** | `12 Apply Threshold` | `$P (liked_label=1)$ >= 0.5 => "1"` · `TRUE => "0"` · *Append*: `predicted_label` |
| 13 | **Scorer** | `13 Scorer VALID` | First column `liked_label`, second column `predicted_label` |
| 14 | **ROC Curve** | `14 ROC VALID` | Class column `liked_label`, positive class `1`, probability column `P (liked_label=1)` |

Dùng VALID để:

- kiểm tra overfitting (so với chỉ số trên TRAIN);
- chọn threshold: thử `0.40, 0.45, 0.50, 0.55, 0.60` trong node 12, ghi precision/recall/F1 từng mức;
- xem precision–recall trade-off;
- điều chỉnh feature set;
- **không** xem TEST ở giai đoạn này.

### 17.5 Final test (chạy một lần)

Sau khi đóng băng model và threshold, copy nguyên nhánh VALID thành nhánh TEST:

| # | Node | Tên node | Thay đổi so với nhánh VALID |
|---|---|---|---|
| 20 | **DB Query Reader** | `20 Read TEST` | `SELECT * FROM ml_rating_features WHERE data_split = 'TEST'` |
| 21–24 | Predictor, Rule Engine, Scorer, ROC Curve | `21 Predict TEST` … `24 ROC TEST` | Threshold = giá trị đã chọn ở VALID |

### 17.6 Metrics phải báo cáo

- Accuracy;
- Precision và Recall cho class liked;
- F1-score;
- Confusion matrix;
- ROC-AUC;
- Số dòng TEST;
- So sánh với **majority-class baseline** (luôn đoán class phổ biến nhất).

Accuracy, precision, recall, F1, AUC, baseline và số dòng TEST được tính lại bằng SQL từ `rating_predictions` và ghi vào `model_metrics` (18.2), nên số trên dashboard luôn khớp với dữ liệu trong MySQL.

### 17.7 Diễn giải coefficient

Từ coefficient table, trả lời:

- chất lượng lịch sử của phim (movie prior) có ảnh hưởng mạnh không;
- xu hướng chấm điểm của user có làm thay đổi xác suất không;
- cluster nào có baseline propensity cao/thấp;
- genre nào có liên hệ dương/âm sau khi đã kiểm soát các feature khác.

Không diễn giải coefficient thành quan hệ nhân quả.

---

## 18. Ghi kết quả Logistic Regression về MySQL

### 18.1 Ghi predictions TEST → `rating_predictions`

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 25a | **String Manipulation** | `25 Predicted as Integer` | `toInt($predicted_label$)` · *Append*: `predicted_liked` (threshold chỉ cần đặt một chỗ: node Rule Engine) |
| 25b | **Column Rename** | `25 Rename Output Columns` | `liked` → `actual_liked` · `P (liked_label=1)` → `probability_liked` |
| 25c | **Constant Value Column** ×2 | `25 Add Version and Date` | `model_version` = `logit_v1` · `model_run_date` = `2026-10-15 10:00:00` (String) |
| 25d | **Column Filter** | `25 Keep Output Columns` | Đúng 10 cột: `rating_id`, `user_id`, `movie_id`, `cluster_id`, `actual_liked`, `predicted_liked`, `probability_liked`, `data_split`, `model_version`, `model_run_date` |
| 26 | **DB SQL Executor** | `26 Clear Old Predictions` | `DELETE FROM rating_predictions WHERE model_version = 'logit_v1'` |
| 27 | **DB Writer** | `27 Write Predictions to MySQL` | Cổng DB từ node 26 · Table `rating_predictions` · bỏ chọn *Remove existing table* · Batch size `10000` (~1.5M dòng, có thể mất 5–15 phút) |

`rating_predictions` có primary key `(rating_id, model_version)`. Model mới thì đổi `model_version` (ví dụ `logit_v2`) để giữ cả hai bản và so sánh trên dashboard.

### 18.2 Tính metrics TEST → `model_metrics`

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 28 | **DB SQL Executor** | `28 Compute TEST Metrics` | Cổng DB nối từ **output DB của node 27** (chạy sau khi ghi predictions xong) · dán nội dung `sql/knime_logit_metrics.sql` (bỏ dòng `USE`) |

File `sql/knime_logit_metrics.sql` xoá metrics TEST cũ của phiên bản này rồi ghi lại 7 metric: `accuracy`, `precision`, `recall`, `f1`, `baseline_accuracy`, `test_rows`, `auc`. AUC tính theo công thức Mann–Whitney (tie được tính rank trung bình). Đã kiểm tra trên dữ liệu thử: cả 7 giá trị khớp tuyệt đối với tính tay.

```sql
USE movielens_strategy;

DELETE FROM model_metrics
WHERE model_name = 'logistic_regression'
  AND model_version = 'logit_v1'
  AND split_name = 'TEST';

INSERT INTO model_metrics
    (model_name, model_version, split_name, metric_name, metric_value, run_timestamp)
SELECT 'logistic_regression', 'logit_v1', 'TEST', m.metric_name, m.metric_value, NOW()
FROM (
    SELECT 'accuracy' AS metric_name, AVG(actual_liked = predicted_liked) AS metric_value
    FROM rating_predictions WHERE model_version = 'logit_v1' AND data_split = 'TEST'
    UNION ALL
    SELECT 'precision', SUM(actual_liked = 1 AND predicted_liked = 1) / NULLIF(SUM(predicted_liked = 1), 0)
    FROM rating_predictions WHERE model_version = 'logit_v1' AND data_split = 'TEST'
    UNION ALL
    SELECT 'recall', SUM(actual_liked = 1 AND predicted_liked = 1) / NULLIF(SUM(actual_liked = 1), 0)
    FROM rating_predictions WHERE model_version = 'logit_v1' AND data_split = 'TEST'
    UNION ALL
    SELECT 'f1', 2 * SUM(actual_liked = 1 AND predicted_liked = 1)
                 / NULLIF(2 * SUM(actual_liked = 1 AND predicted_liked = 1)
                          + SUM(actual_liked = 0 AND predicted_liked = 1)
                          + SUM(actual_liked = 1 AND predicted_liked = 0), 0)
    FROM rating_predictions WHERE model_version = 'logit_v1' AND data_split = 'TEST'
    UNION ALL
    -- Majority-class baseline: always predict the most frequent class.
    SELECT 'baseline_accuracy', GREATEST(AVG(actual_liked), 1 - AVG(actual_liked))
    FROM rating_predictions WHERE model_version = 'logit_v1' AND data_split = 'TEST'
    UNION ALL
    SELECT 'test_rows', COUNT(*)
    FROM rating_predictions WHERE model_version = 'logit_v1' AND data_split = 'TEST'
    UNION ALL
    -- ROC-AUC = Mann-Whitney U / (positives * negatives), tied scores get their average rank.
    SELECT 'auc',
           (SUM(CASE WHEN actual_liked = 1 THEN rnk + (ties - 1) / 2 END)
            - SUM(actual_liked) * (SUM(actual_liked) + 1) / 2)
           / (SUM(actual_liked) * SUM(1 - actual_liked))
    FROM (
        SELECT actual_liked,
               RANK() OVER (ORDER BY probability_liked) AS rnk,
               COUNT(*) OVER (PARTITION BY probability_liked) AS ties
        FROM rating_predictions
        WHERE model_version = 'logit_v1' AND data_split = 'TEST'
    ) AS ranked
) AS m;
```

> Khi đổi sang `logit_v2`, thay mọi chữ `logit_v1` trong SQL này. Không viết dấu `;` trong comment: DB SQL Executor tách câu lệnh theo dấu `;`.

### 18.3 Ghi coefficients → `model_metrics`

Để vẽ biểu đồ coefficient trên dashboard (Page 3) từ MySQL:

| # | Node | Tên node | Cấu hình |
|---|---|---|---|
| 29a | **String Manipulation** | `29 Coefficient Name` | Trên output 2 của Learner: `join("coef_", $Variable$)` · *Append*: `metric_name` |
| 29b | **Column Rename** | `29 Coefficient Value` | `Coeff.` → `metric_value` |
| 29c | **Constant Value Column** ×4 | `29 Metric Columns` | `model_name` = `logistic_regression` · `model_version` = `logit_v1` · `split_name` = `TRAIN` · `run_timestamp` = `2026-10-15 10:00:00` |
| 29d | **Column Filter** | `29 Keep Metric Columns` | `model_name`, `model_version`, `split_name`, `metric_name`, `metric_value`, `run_timestamp` |
| 29e | **DB SQL Executor** | `29 Clear Old Coefficients` | `DELETE FROM model_metrics WHERE model_name = 'logistic_regression' AND model_version = 'logit_v1' AND split_name = 'TRAIN'` |
| 29f | **DB Writer** | `29 Write Coefficients to MySQL` | Table `model_metrics`, bỏ chọn *Remove existing table* |

> `metric_name` tối đa 50 ký tự. Tên coefficient của cột chuỗi có dạng `coef_cluster_label=2`, vẫn trong giới hạn.

**Kiểm tra trong Workbench:**

```sql
SELECT COUNT(*) FROM rating_predictions WHERE model_version = 'logit_v1';

SELECT actual_liked, predicted_liked, COUNT(*) AS rows_count
FROM rating_predictions
WHERE model_version = 'logit_v1'
GROUP BY actual_liked, predicted_liked;

SELECT * FROM model_metrics ORDER BY model_name, split_name, metric_name;
```

**Bằng chứng cần chụp:** workflow đầy đủ, Scorer VALID và TEST, ROC curve, coefficient table, các DB Writer đèn xanh, 3 query kiểm tra.

---

# PHASE D — DASHBOARD VIEWS VÀ POWER BI

## 19. Tạo dashboard views trong MySQL

**Làm gì:** sau khi KNIME đã ghi `user_segments`, `rating_predictions`, `model_metrics`, chạy `sql/07_dashboard_views.sql` (hoặc `py .\python_sql_scripts\run_all.py --from-step 7`).

Power BI **chỉ** đọc các view dưới đây (đều nhỏ, đã tổng hợp sẵn), không đọc bảng `ratings` 10M dòng.

| View | Số dòng (xấp xỉ) | Dùng ở trang | Thời gian refresh |
|---|---:|---|---|
| `dashboard_kpis` | 1 | Page 1 | ~8 giây |
| `dashboard_rating_distribution` | 10 | Page 1 | ~7 giây |
| `dashboard_genre_kpis` | 20 | Page 1 | ~13 giây |
| `dashboard_movie_popularity` | ~4,600 | Page 1 | < 1 giây |
| `dashboard_split_summary` | 3 | Page 5 | vài phút (join 10M dòng) |
| `dashboard_segment_profiles` | = số cluster | Page 2 | nhanh |
| `dashboard_segment_genres` | cluster × 20 | Page 2 | nhanh |
| `dashboard_content_opportunities` | cluster × phim × version | Page 4 | vài giây |
| `dashboard_confusion_matrix` | 4 / version | Page 3 | vài giây |
| `dashboard_model_metrics` | vài chục | Page 3, 5 | nhanh |

### 19.1 Overall KPI

```sql
USE movielens_strategy;

CREATE OR REPLACE VIEW dashboard_kpis AS
SELECT
    ra.total_ratings,
    (SELECT COUNT(DISTINCT user_id) FROM ratings) AS total_users,
    (SELECT COUNT(*) FROM movies) AS total_movies,
    (SELECT COUNT(*) FROM tags) AS total_tags,
    ra.average_rating,
    ra.positive_rating_rate
FROM (
    -- One scan of ratings instead of three separate full scans.
    SELECT
        COUNT(*) AS total_ratings,
        AVG(rating) AS average_rating,
        AVG(rating >= 4.0) AS positive_rating_rate
    FROM ratings
) AS ra;
```

### 19.2 Rating distribution, genre KPI, movie popularity

`dashboard_genre_kpis` dùng lại đúng query đã tối ưu ở 12.4 (gom theo phim trước, rồi mới nối sang genre).

```sql
-- Page 1: rating distribution (10 rows).
CREATE OR REPLACE VIEW dashboard_rating_distribution AS
SELECT
    rating,
    COUNT(*) AS rating_count,
    COUNT(*) / SUM(COUNT(*)) OVER () AS rating_share
FROM ratings
GROUP BY rating;

-- Page 1: KPI by genre. Same optimised query as rubric query 3 in
-- 05_feature_tables.sql: aggregate per movie first, then fan out to genres.
CREATE OR REPLACE VIEW dashboard_genre_kpis AS
SELECT
    mg.genre,
    CAST(SUM(ma.rating_count) AS UNSIGNED) AS rating_count,
    SUM(ma.rating_sum) / SUM(ma.rating_count) AS avg_rating,
    SUM(ma.positive_count) / SUM(ma.rating_count) AS positive_rate
FROM (
    SELECT /*+ NO_INDEX(ratings) */
        movie_id,
        COUNT(*) AS rating_count,
        SUM(rating) AS rating_sum,
        SUM(rating >= 4.0) AS positive_count
    FROM ratings
    GROUP BY movie_id
) AS ma
JOIN movie_genres AS mg ON mg.movie_id = ma.movie_id
GROUP BY mg.genre;

-- Page 1: TRAIN movie popularity with minimum support (Top N is set in Power BI).
CREATE OR REPLACE VIEW dashboard_movie_popularity AS
SELECT
    m.movie_id,
    m.title,
    m.genres,
    ms.rating_count,
    ms.avg_rating,
    ms.positive_rate
FROM train_movie_stats AS ms
JOIN movies AS m ON m.movie_id = ms.movie_id
WHERE ms.rating_count >= 100;
```

### 19.3 Split summary (cho trang Model Governance)

```sql
-- Page 5: rows and time period of each split. Joins 10M rows, so it takes a
-- few minutes; the split only changes when 04 is rerun.
CREATE OR REPLACE VIEW dashboard_split_summary AS
SELECT
    s.data_split,
    COUNT(*) AS rows_in_split,
    FROM_UNIXTIME(MIN(r.rating_ts)) AS period_start,
    FROM_UNIXTIME(MAX(r.rating_ts)) AS period_end
FROM rating_split AS s
JOIN ratings AS r ON r.rating_id = s.rating_id
GROUP BY s.data_split;
```

### 19.4 Segment profiles và segment–genre

```sql
CREATE OR REPLACE VIEW dashboard_segment_profiles AS
SELECT
    seg.cluster_id,
    seg.segment_name,
    COUNT(*) AS user_count,
    AVG(us.rating_count) AS avg_user_ratings,
    AVG(us.avg_rating) AS avg_rating,
    AVG(us.positive_rate) AS avg_positive_rate,
    AVG(us.rating_stddev) AS avg_rating_stddev,
    AVG(us.active_days) AS avg_active_days
FROM user_segments AS seg
JOIN train_user_stats AS us ON us.user_id = seg.user_id
GROUP BY seg.cluster_id, seg.segment_name;

CREATE OR REPLACE VIEW dashboard_segment_genres AS
SELECT
    seg.cluster_id,
    seg.segment_name,
    ugs.genre,
    COUNT(DISTINCT ugs.user_id) AS users_with_genre,
    SUM(ugs.genre_rating_count) AS genre_rating_count,
    AVG(ugs.genre_avg_rating) AS avg_genre_rating,
    AVG(ugs.genre_positive_rate) AS avg_genre_positive_rate
FROM user_segments AS seg
JOIN train_user_genre_stats AS ugs ON ugs.user_id = seg.user_id
GROUP BY seg.cluster_id, seg.segment_name, ugs.genre;
```

### 19.5 Content opportunity

So với bản đầu của kế hoạch, view này có hai thay đổi quan trọng:

1. Nối `user_segments` theo **cả** `user_id` và `cluster_id`, nên mỗi prediction chỉ khớp đúng một dòng segment (bản cũ nối qua `SELECT DISTINCT cluster_id, segment_name` có thể nhân dòng nếu một cluster có hai tên).
2. Có thêm cột `model_version` và group theo nó. Nếu KNIME ghi thêm `logit_v2`, bản cũ sẽ cộng chung hai version, làm `test_support` gấp đôi. Trên Power BI phải luôn lọc **một** `model_version`.

```sql
-- Joined to user_segments by user_id AND cluster_id, so each prediction row
-- matches exactly one segment row. rating_predictions is keyed by
-- (rating_id, model_version); grouping by version stops a second model run
-- from doubling test_support. Filter one model_version in Power BI.
CREATE OR REPLACE VIEW dashboard_content_opportunities AS
SELECT
    rp.model_version,
    rp.cluster_id,
    seg.segment_name,
    rp.movie_id,
    m.title,
    m.genres,
    COUNT(*) AS test_support,
    AVG(rp.probability_liked) AS predicted_like_probability,
    AVG(rp.actual_liked) AS actual_positive_rate,
    ms.rating_count AS train_popularity,
    ms.avg_rating AS train_avg_rating
FROM rating_predictions AS rp
JOIN movies AS m ON m.movie_id = rp.movie_id
JOIN train_movie_stats AS ms ON ms.movie_id = rp.movie_id
JOIN user_segments AS seg
    ON seg.user_id = rp.user_id
   AND seg.cluster_id = rp.cluster_id
WHERE rp.data_split = 'TEST'
GROUP BY
    rp.model_version,
    rp.cluster_id,
    seg.segment_name,
    rp.movie_id,
    m.title,
    m.genres,
    ms.rating_count,
    ms.avg_rating;
```

Dashboard nên lọc `test_support >= 30` hoặc `>= 50`. Chọn ngưỡng cuối dựa trên phân phối support (vẽ histogram `test_support` trước), không chọn tuỳ ý.

### 19.6 Confusion matrix và model metrics

```sql
-- Page 3: confusion matrix per model version and split (4 rows per version),
-- so Power BI does not have to import millions of prediction rows.
CREATE OR REPLACE VIEW dashboard_confusion_matrix AS
SELECT
    model_version,
    data_split,
    actual_liked,
    predicted_liked,
    COUNT(*) AS row_count
FROM rating_predictions
GROUP BY model_version, data_split, actual_liked, predicted_liked;

-- Pages 3 and 5: metrics, Logistic coefficients (metric_name 'coef_<feature>')
-- and K-Means silhouette by K (metric_name 'silhouette_k<K>') written by KNIME.
CREATE OR REPLACE VIEW dashboard_model_metrics AS
SELECT
    model_name,
    model_version,
    split_name,
    metric_name,
    metric_value,
    run_timestamp
FROM model_metrics;
```

### 19.7 Kiểm tra trước khi mở Power BI

```sql
-- Check the marts before connecting Power BI.
SELECT * FROM dashboard_kpis;
SELECT * FROM dashboard_rating_distribution LIMIT 20;
SELECT * FROM dashboard_genre_kpis LIMIT 20;
SELECT * FROM dashboard_movie_popularity LIMIT 20;
SELECT * FROM dashboard_split_summary LIMIT 20;
SELECT * FROM dashboard_segment_profiles LIMIT 20;
SELECT * FROM dashboard_segment_genres LIMIT 20;
SELECT * FROM dashboard_content_opportunities LIMIT 20;
SELECT * FROM dashboard_confusion_matrix LIMIT 20;
SELECT * FROM dashboard_model_metrics LIMIT 20;
```

---

## 20. Kết nối Power BI với MySQL

> **Đã có sẵn project Power BI:** `dashboard/movielens_content_strategy.pbip` (sinh bằng `py dashboard/build_pbip.py`) đã gồm đủ các bảng, relationship, measure ở section 20–22 và 5 trang ở section 23.
> 1. Chạy xong Part C và bước 07 (`py .\python_sql_scripts\run_all.py --from-step 7`).
> 2. Mở file `.pbip` bằng Power BI Desktop → **Refresh** → nhập user/password MySQL (tab *Database*).
> 3. Chuột phải bảng `dashboard_split_summary` → *Refresh data* (bảng này không tự refresh, vì join 10M dòng).
> 4. **File → Save As → Power BI file (.pbix)** → lưu thành `dashboard/movielens_content_strategy.pbix`.
> 5. Làm thêm bằng tay (chưa có trong file): đường median trong pane *Analytics* của scatter Page 4, màu nền có điều kiện cho matrix heatmap Page 2, ảnh ROC từ KNIME ở Page 3.
>
> Các bước dưới đây mô tả cách dựng thủ công, dùng khi muốn hiểu hoặc sửa từng phần.

### 20.1 Cài driver (làm một lần)

Power BI Desktop cần **MySQL Connector/NET** để đọc MySQL.

1. Tải *MySQL Connector/NET* (bản 8.0.x hoặc mới hơn) từ trang MySQL Downloads, cài bản Windows (x64).
2. Khởi động lại Power BI Desktop.

Nếu khi kết nối gặp lỗi *"This connector requires one or more additional components to be installed"* thì chưa cài driver này.

### 20.2 Lấy dữ liệu

1. **Home → Get data → More… →** gõ `MySQL` → chọn **MySQL database** → *Connect*.
2. *Server*: `localhost:3306` · *Database*: `movielens_strategy` → *OK*.
3. Cửa sổ credential: chọn tab **Database** (bên trái) → nhập user/password MySQL → *Connect*. Nếu hỏi mã hoá, chọn *OK* để kết nối không mã hoá (máy local).
4. Cửa sổ *Navigator*: tick các bảng/view sau:

   | Chọn | Ghi chú |
   |---|---|
   | `movielens_strategy dashboard_kpis` | |
   | `… dashboard_rating_distribution` | |
   | `… dashboard_genre_kpis` | |
   | `… dashboard_movie_popularity` | |
   | `… dashboard_split_summary` | xem bước 6 |
   | `… dashboard_segment_profiles` | |
   | `… dashboard_segment_genres` | |
   | `… dashboard_content_opportunities` | |
   | `… dashboard_confusion_matrix` | |
   | `… dashboard_model_metrics` | |
   | `… movie_genres` | bảng gốc nhỏ (~21K dòng), dùng để lọc theo genre ở Page 4 |

5. Bấm **Transform Data** (không bấm *Load* ngay) để mở Power Query.
6. Trong Power Query, chuột phải query `dashboard_split_summary` → bỏ tick **Include in report refresh**. View này join 10M dòng, chỉ đổi khi chạy lại bước 04; refresh nó mỗi lần là lãng phí vài phút.
7. Đổi tên query cho gọn: bỏ tiền tố `movielens_strategy ` (double-click tên query).
8. Kiểm tra kiểu dữ liệu (biểu tượng ở đầu cột):

   | Cột | Kiểu |
   |---|---|
   | `*_rate`, `*_probability`, `rating_share`, `avg_*`, `metric_value` | Decimal Number |
   | `*_count`, `test_support`, `train_popularity`, `rows_in_split`, `cluster_id` | Whole Number |
   | `period_start`, `period_end`, `run_timestamp` | Date/Time |
   | `model_version`, `segment_name`, `genre`, `title` | Text |

9. **Home → Close & Apply**.

> Chế độ kết nối: dùng **Import** (mặc định). Không dùng DirectQuery vì mỗi lần click visual sẽ chạy lại view trên MySQL.

### 20.3 Refresh khi có kết quả mới

Sau khi chạy lại pipeline hoặc KNIME: **Home → Refresh**. Muốn cập nhật `dashboard_split_summary`, chuột phải bảng đó trong pane *Data* → **Refresh data**.

---

## 21. Data model trong Power BI

### 21.1 Bảng phụ cần tạo

Vào **Modeling → New table**, tạo hai bảng:

```DAX
Model Versions =
DISTINCT (
    UNION (
        SELECTCOLUMNS ( dashboard_content_opportunities, "model_version", dashboard_content_opportunities[model_version] ),
        SELECTCOLUMNS ( dashboard_confusion_matrix, "model_version", dashboard_confusion_matrix[model_version] ),
        SELECTCOLUMNS ( dashboard_model_metrics, "model_version", dashboard_model_metrics[model_version] )
    )
)
```

```DAX
Genres =
DISTINCT (
    UNION (
        SELECTCOLUMNS ( movie_genres, "genre", movie_genres[genre] ),
        SELECTCOLUMNS ( dashboard_segment_genres, "genre", dashboard_segment_genres[genre] )
    )
)
```

Tham số ngưỡng support: **Modeling → New parameter → Numeric range**:

| Ô | Giá trị |
|---|---|
| Name | `Min Support` |
| Data type | Whole number |
| Minimum / Maximum / Increment | `0` / `500` / `10` |
| Default | `50` |
| Add slicer to this page | tick |

Power BI tự tạo bảng `Min Support` và measure `Min Support Value`.

### 21.2 Relationships

Vào **Model view** (biểu tượng sơ đồ bên trái), kéo cột từ bảng này sang bảng kia, rồi double-click đường nối để chỉnh:

| Từ (phía 1) | Đến (phía nhiều) | Cardinality | Cross filter |
|---|---|---|---|
| `Model Versions[model_version]` | `dashboard_content_opportunities[model_version]` | One to many | Single |
| `Model Versions[model_version]` | `dashboard_confusion_matrix[model_version]` | One to many | Single |
| `Model Versions[model_version]` | `dashboard_model_metrics[model_version]` | One to many | Single |
| `dashboard_segment_profiles[cluster_id]` | `dashboard_segment_genres[cluster_id]` | One to many | Single |
| `dashboard_segment_profiles[cluster_id]` | `dashboard_content_opportunities[cluster_id]` | One to many | Single |
| `Genres[genre]` | `dashboard_segment_genres[genre]` | One to many | Single |
| `Genres[genre]` | `movie_genres[genre]` | One to many | Single |
| `movie_genres[movie_id]` | `dashboard_content_opportunities[movie_id]` | **Many to many** | **Single: `movie_genres` filters `dashboard_content_opportunities`** |

Vì sao cần `movie_genres`: cột `genres` trong `dashboard_content_opportunities` là chuỗi `Action|Comedy`, không lọc trực tiếp theo một genre được. Đường `Genres → movie_genres → dashboard_content_opportunities` cho phép slicer genre lọc đúng mọi phim có genre đó.

Các bảng `dashboard_kpis`, `dashboard_rating_distribution`, `dashboard_genre_kpis`, `dashboard_movie_popularity`, `dashboard_split_summary` đứng độc lập, không cần relationship.

### 21.3 Định dạng cột

Trong *Data view*, chọn cột → tab **Column tools**:

- `positive_rate`, `positive_rating_rate`, `rating_share`, `predicted_like_probability`, `actual_positive_rate`, `avg_positive_rate`, `avg_genre_positive_rate`: **Format → Percentage**, 1 chữ số thập phân.
- `rating_count`, `test_support`, `total_*`: **Whole number**, bật dấu phân cách hàng nghìn.

---

## 22. DAX measures

Tạo bảng chứa measure cho gọn: **Home → Enter data →** đặt tên `_Measures` → *Load*. Chọn bảng đó → **Home → New measure** cho từng measure dưới đây.

### 22.1 KPI tổng quan (Page 1)

```DAX
Total Ratings = MAX ( dashboard_kpis[total_ratings] )

Total Users = MAX ( dashboard_kpis[total_users] )

Total Movies = MAX ( dashboard_kpis[total_movies] )

Total Tags = MAX ( dashboard_kpis[total_tags] )

Average Rating = MAX ( dashboard_kpis[average_rating] )

Positive Rating Rate = MAX ( dashboard_kpis[positive_rating_rate] )
```

`dashboard_kpis` chỉ có 1 dòng, nên `MAX` trả đúng giá trị đó.

### 22.2 Content opportunity (Page 4)

```DAX
Test Support =
SUM ( dashboard_content_opportunities[test_support] )

Predicted Like Probability =
DIVIDE (
    SUMX (
        dashboard_content_opportunities,
        dashboard_content_opportunities[predicted_like_probability]
            * dashboard_content_opportunities[test_support]
    ),
    [Test Support]
)

Actual Positive Rate =
DIVIDE (
    SUMX (
        dashboard_content_opportunities,
        dashboard_content_opportunities[actual_positive_rate]
            * dashboard_content_opportunities[test_support]
    ),
    [Test Support]
)

Calibration Gap =
[Predicted Like Probability] - [Actual Positive Rate]

Train Popularity =
MAX ( dashboard_content_opportunities[train_popularity] )

Passes Min Support =
IF ( [Test Support] >= [Min Support Value], 1, 0 )

Supported Movies =
COUNTROWS (
    FILTER (
        VALUES ( dashboard_content_opportunities[movie_id] ),
        [Test Support] >= [Min Support Value]
    )
)
```

> **Sửa so với bản đầu của kế hoạch:**
> - Trung bình xác suất được **weight theo `test_support`**. Bản cũ dùng `AVERAGE` trên từng dòng phim, nên một phim có 1 rating TEST có trọng số bằng phim có 5,000 rating.
> - Bản cũ gọi `predicted − actual` là *Opportunity Gap*. Thực ra đó là sai số hiệu chuẩn của mô hình (**Calibration Gap**), không phải cơ hội. Cơ hội = *predicted cao + popularity thấp* (Page 4).
> - Ngưỡng support lấy từ slicer `Min Support` thay vì cố định `50`.

### 22.3 Đánh giá mô hình (Page 3, 5)

```DAX
Test Metric =
// dùng chung: lọc metric_name bằng visual hoặc CALCULATE
CALCULATE (
    MAX ( dashboard_model_metrics[metric_value] ),
    dashboard_model_metrics[split_name] = "TEST"
)

Test Accuracy = CALCULATE ( [Test Metric], dashboard_model_metrics[metric_name] = "accuracy" )

Test Precision = CALCULATE ( [Test Metric], dashboard_model_metrics[metric_name] = "precision" )

Test Recall = CALCULATE ( [Test Metric], dashboard_model_metrics[metric_name] = "recall" )

Test F1 = CALCULATE ( [Test Metric], dashboard_model_metrics[metric_name] = "f1" )

Test AUC = CALCULATE ( [Test Metric], dashboard_model_metrics[metric_name] = "auc" )

Baseline Accuracy = CALCULATE ( [Test Metric], dashboard_model_metrics[metric_name] = "baseline_accuracy" )

Lift vs Baseline = [Test Accuracy] - [Baseline Accuracy]

Prediction Rows = SUM ( dashboard_confusion_matrix[row_count] )

Coefficient =
CALCULATE (
    MAX ( dashboard_model_metrics[metric_value] ),
    dashboard_model_metrics[split_name] = "TRAIN",
    dashboard_model_metrics[model_name] = "logistic_regression"
)

Silhouette =
CALCULATE (
    MAX ( dashboard_model_metrics[metric_value] ),
    dashboard_model_metrics[model_name] = "kmeans"
)
```

Không tạo một "magic score" với trọng số tuỳ ý nếu không có lý do kinh doanh.

---

## 23. Dựng từng trang dashboard

> **Thao tác chung:** thêm trang bằng dấu `+` ở dưới; chọn visual trong pane **Visualizations**; kéo field từ pane **Data** vào các ô (*X-axis*, *Y-axis*, *Values*, *Legend*…). Slicer: chọn visual **Slicer**, kéo một cột vào *Field*. Muốn slicer áp cho nhiều trang: **View → Sync slicers**.

### Page 1 — Executive Overview

**Mục tiêu:** quy mô dữ liệu và hành vi tổng quan.

| Visual | Cách dựng |
|---|---|
| 4–6 **Card** | Mỗi card một measure: `Total Ratings`, `Total Users`, `Total Movies`, `Total Tags`, `Average Rating`, `Positive Rating Rate` |
| **Clustered column chart** — Rating distribution | X-axis: `dashboard_rating_distribution[rating]` · Y-axis: `rating_count` · Tooltips: `rating_share` |
| **Clustered bar chart** — Top genres | Y-axis: `dashboard_genre_kpis[genre]` · X-axis: `rating_count` · Tooltips: `avg_rating`, `positive_rate` · sắp xếp giảm dần theo `rating_count` |
| **Table** — Top supported movies | Columns: `title`, `rating_count`, `avg_rating`, `positive_rate` từ `dashboard_movie_popularity` · Filter pane: `title` → *Filter type* **Top N** = 20, *By value* `avg_rating` |

**Thông điệp:** dữ liệu đủ lớn và có cấu trúc phù hợp cho phân tích khán giả.

### Page 2 — Audience Segments

**Mục tiêu:** trình bày kết quả K-Means.

| Visual | Cách dựng |
|---|---|
| **Clustered bar chart** — Segment size | Y-axis: `dashboard_segment_profiles[segment_name]` · X-axis: `user_count` |
| **Table** — Segment profile | `segment_name`, `user_count`, `avg_user_ratings`, `avg_rating`, `avg_positive_rate`, `avg_rating_stddev`, `avg_active_days` |
| **Matrix** — Heatmap genre | Rows: `dashboard_segment_profiles[segment_name]` · Columns: `Genres[genre]` · Values: `dashboard_segment_genres[avg_genre_positive_rate]` (Average) · **Format → Cell elements → Background color = On** (màu theo giá trị) |
| **Scatter chart** | X-axis: `avg_user_ratings` · Y-axis: `avg_positive_rate` · Values/Legend: `segment_name` · Size: `user_count` |
| **Slicer** | `segment_name`; `Genres[genre]` |
| **Text box** | Mô tả ý nghĩa kinh doanh của từng segment |

**Thông điệp:** một chiến lược "top movies cho mọi người" là không phù hợp.

### Page 3 — Positive Engagement Model

**Mục tiêu:** trình bày Logistic Regression.

| Visual | Cách dựng |
|---|---|
| **Slicer** — Model version | `Model Versions[model_version]` · *Format → Slicer settings → Selection → Single select* · chọn `logit_v1` |
| 6 **Card** | `Test Accuracy`, `Test Precision`, `Test Recall`, `Test F1`, `Test AUC`, `Baseline Accuracy` (thêm `Lift vs Baseline` nếu muốn) |
| **Matrix** — Confusion matrix | Rows: `dashboard_confusion_matrix[actual_liked]` · Columns: `predicted_liked` · Values: `Prediction Rows` · Filter visual: `data_split` = `TEST` |
| **Clustered bar chart** — Coefficients | Y-axis: `dashboard_model_metrics[metric_name]` · X-axis: `Coefficient` · Filter visual: `metric_name` → *Advanced filtering* → **starts with** `coef_` · sắp xếp theo `Coefficient` |
| **Image** — ROC curve | Screenshot ROC từ KNIME (node 24) |

**Thông điệp:** mô hình xếp hạng được cơ hội nội dung tốt hơn baseline, nhưng không chứng minh quan hệ nhân quả.

### Page 4 — Content Opportunity Matrix (trang ra quyết định chính)

| Visual | Cách dựng |
|---|---|
| **Slicer** — Model version | `Model Versions[model_version]`, single select |
| **Slicer** — Segment | `dashboard_segment_profiles[segment_name]` |
| **Slicer** — Genre | `Genres[genre]` |
| **Slicer** — Min support | `Min Support` (đã tạo ở 21.1) |
| **Scatter chart** | *Values* (Details): `dashboard_content_opportunities[title]` · X-axis: measure `Train Popularity` · Y-axis: measure `Predicted Like Probability` · Size: measure `Test Support` · Tooltips: `Actual Positive Rate`, `Calibration Gap` |
| Filter của scatter | Kéo measure `Passes Min Support` vào *Filters on this visual* → *is* `1` |
| Đường chia 4 vùng | Chọn scatter → pane **Analytics** (biểu tượng kính lúp) → **X-axis median line** và **Y-axis median line** → *Add* |
| Trục X | **Format → X-axis → Scale type = Log** (popularity rất lệch) |
| **Table** — Danh sách ứng viên | `segment_name`, `title`, `Test Support`, `Predicted Like Probability`, `Train Popularity`, áp cùng filter `Passes Min Support = 1`, sắp giảm dần theo `Predicted Like Probability` |

Bốn vùng diễn giải:

| Popularity | Predicted like | Diễn giải | Hành động |
|---|---|---|---|
| Cao | Cao | Proven hit | Duy trì hiển thị |
| Thấp | Cao | **Hidden opportunity** | Promote / curate |
| Cao | Thấp | Overexposed cho segment này | Giảm targeting cho segment |
| Thấp | Thấp | Low priority | Không ưu tiên |

Không kết luận "promotion sẽ tăng doanh thu". Kết luận đúng: "đây là **ứng viên** để thử nghiệm promotion".

### Page 5 — Model Governance (khuyến nghị)

| Visual | Cách dựng |
|---|---|
| **Table** — Các split | `dashboard_split_summary`: `data_split`, `rows_in_split`, `period_start`, `period_end` |
| **Table** — Phiên bản mô hình | `dashboard_model_metrics`: `model_name`, `model_version`, `run_timestamp` (bỏ trùng bằng cách để *Don't summarize*) |
| **Line chart** — Silhouette theo K | X-axis: `dashboard_model_metrics[metric_name]` · Y-axis: `Silhouette` · Filter visual: `metric_name` **starts with** `silhouette_k` |
| **Card** — Logistic vs baseline | `Test Accuracy`, `Baseline Accuracy`, `Lift vs Baseline` |
| **Text box** — Known limitations | Tóm tắt section 4.3 và ghi chú cold-start |

> Không đặt (hoặc không sync) slicer `Model Versions` ở trang này: silhouette thuộc version `kmeans_v1`, nếu slicer đang chọn `logit_v1` thì biểu đồ silhouette sẽ trống. Trong **View → Sync slicers**, chỉ tick Page 3 và Page 4 cho slicer model version.

Trang này cho thấy tính học thuật và khả năng tái lập (reproducibility).

---

# PHASE E — INSIGHTS VÀ QUYẾT ĐỊNH

## 24. Cách viết insight

Mỗi insight theo cấu trúc:

```text
Observation → Evidence → Meaning → Decision implication
```

Mẫu:

> Segment [tên] chiếm [x%] users, có positive rate của [genre] là [y%] và predicted like probability [z%] cho nhóm phim [loại]. Điều này cho thấy một chiến lược quảng bá riêng có thể phù hợp hơn bảng xếp hạng toàn nền tảng.

Không điền số giả. Chỉ điền sau khi pipeline và dashboard có kết quả thật.

---

## 25. Các recommendation bắt buộc

### Recommendation 1 — Segment-specific promotion

```text
Target segment:
Evidence:
Recommended content/genre:
Action:
Success KPI:
Limitation:
```

### Recommendation 2 — Hidden-content discovery

Chọn phim (từ vùng *Hidden opportunity* của Page 4) có:

- predicted like cao;
- popularity thấp hoặc trung bình;
- support đủ lớn (qua slicer `Min Support`);
- actual positive rate chấp nhận được.

Đề xuất đưa vào curated collection cho đúng segment.

### Recommendation 3 — Reduce broad promotion

Chọn phim phổ biến toàn hệ thống nhưng predicted like thấp trong một segment cụ thể (vùng *Overexposed*). Đề xuất giảm ưu tiên cho segment đó, không xoá phim khỏi catalog.

### Recommendation 4 — Controlled experiment (điểm cộng)

Đề xuất A/B test ngoài phạm vi dataset:

- control: danh sách theo popularity;
- treatment: danh sách theo segment;
- KPI: click-through, play-start, completion hoặc tỷ lệ rating.

Đây là đề xuất thử nghiệm tương lai, không được tuyên bố MovieLens đã chứng minh uplift.

---

# PHASE F — REPORT, GITHUB VÀ DEMO

## 26. Cấu trúc final report

| Mục | Nội dung |
|---|---|
| Cover page | Tên project, môn học, thành viên và mã số sinh viên, cam kết học thuật (nếu được yêu cầu) |
| 1. Executive Summary | Bài toán kinh doanh, quy mô dataset, hai mô hình, phát hiện chính, ba quyết định |
| 2. Business Context and Decision Questions | Stakeholder, vì sao quyết định quan trọng, ràng buộc, problem statement, bốn câu hỏi |
| 3. Dataset | Nguồn và citation, số rows/users/movies/tags, biến, license, mức phù hợp, giới hạn |
| 4. MySQL Architecture and SQL Analysis | ER diagram, cấu trúc bảng và keys, quy trình import, quality checks, query filter/aggregate/join/KPI, bằng chứng 10M rows, cách tối ưu query (12.4, 11) |
| 5. KNIME Data Preparation | Kết nối MySQL, feature engineering, time split, missing values/outliers, chuẩn hoá, screenshot workflow có tên node đọc được |
| 6. K-Means Audience Segmentation | Features và lý do, các K đã thử, silhouette, profile cluster, đặt tên segment, giới hạn |
| 7. Logistic Regression | Định nghĩa target, features, thiết kế leave-one-out, train/validation/test, baseline, metrics, diễn giải coefficient, giới hạn |
| 8. MySQL Write-back and Reproducibility | `user_segments`, `rating_predictions`, `model_metrics`, số dòng và model version, cách chạy lại bằng `run_all.py` |
| 9. Dashboard and Insights | Screenshot từng trang, câu hỏi mà trang trả lời, các insight có số liệu |
| 10. Recommendations | Ít nhất 3 recommendation theo dạng Evidence → Action → KPI |
| 11. Limitations and Future Work | Tuổi dataset, selection/exposure bias, không có dữ liệu xem/doanh thu, phạm vi warm-start, không có kết luận nhân quả, A/B test tương lai |
| 12. Conclusion | |
| References | GroupLens dataset, MovieLens paper, tài liệu KNIME/MySQL/Power BI đã dùng, AI-use statement |

---

## 27. README bắt buộc

README phải có:

1. Project overview.
2. Business decision.
3. Nguồn dataset và ghi chú license.
4. Prerequisites (section 5).
5. Folder structure (section 6.1).
6. MySQL setup (`.env`, `local_infile`).
7. Thứ tự chạy SQL scripts.
8. Cách cấu hình credential trong KNIME (13.2).
9. Thứ tự chạy hai workflow.
10. Bảng nào được write-back.
11. Cách refresh Power BI (20.3).
12. Expected outputs.
13. Known limitations.
14. Team contributions.
15. Khai báo sử dụng AI.

Thứ tự tái tạo:

```text
01_create_schema.sql
 → 02_load_data.sql
 → 03_quality_checks.sql
 → 04_create_splits.sql
 → 05_feature_tables.sql
 → chạy workflow KNIME K-Means          (ghi user_segments + silhouette)
 → kiểm tra user_segments
 → 06_logistic_features.sql
 → chạy workflow KNIME Logistic          (ghi rating_predictions, chạy knime_logit_metrics.sql, ghi coefficients)
 → kiểm tra rating_predictions / model_metrics
 → 07_dashboard_views.sql
 → refresh Power BI
```

Hoặc chạy cả phần MySQL bằng một lệnh, pipeline tự chờ KNIME ở giữa:

```powershell
py .\python_sql_scripts\run_all.py
```

Chi tiết: `python_sql_scripts/README.md`.

---

## 28. Mẫu khai báo sử dụng AI

Chỉnh theo quy định của VNUK và phần việc thực tế:

```text
Generative AI was used to support project planning, explain technical concepts,
review SQL/workflow structure, and improve the clarity of documentation. All
dataset choices, SQL execution, KNIME workflow construction, model evaluation,
dashboard development, interpretations, and final recommendations were verified
and completed by the project team. AI-generated suggestions were not treated as
evidence and were checked against the dataset and official documentation.
```

Không khai sai phạm vi AI đã hỗ trợ.

---

## 29. Kịch bản demo 8–10 phút

| Thời gian | Nội dung | Cần cho xem |
|---|---|---|
| 0:00–1:00 | Business problem | Stakeholder, quyết định, bốn câu hỏi, vì sao MovieLens 10M phù hợp |
| 1:00–2:30 | MySQL | Row count 10,000,054; schema và joins; các khoảng thời gian train/validation/test; feature tables; (tuỳ chọn) chạy `run_all.py` |
| 2:30–4:30 | KNIME K-Means | Execute connection/read nodes; giải thích user profile và genre affinity; so sánh K/silhouette; profile cluster; write-back `user_segments` |
| 4:30–6:30 | KNIME Logistic Regression | Target và features; time split và kiểm soát leakage; metrics/confusion matrix; diễn giải coefficient; write-back `rating_predictions` và `model_metrics` |
| 6:30–9:00 | Power BI | Executive overview; segment profiles; hiệu năng dự báo; Content Opportunity Matrix; ba recommendation có số liệu |
| 9:00–10:00 | Giới hạn và kết luận | Không có dữ liệu xem/doanh thu/exposure; tuổi dataset; A/B test là bước kiểm chứng tương lai |

---

## 30. Checklist nộp bài

### File bắt buộc

- [ ] Final report PDF.
- [ ] Nguồn/reference chính thức của dataset (không cần nộp raw data nếu license/dung lượng không phù hợp).
- [ ] `sql/01_create_schema.sql` … `sql/07_dashboard_views.sql`, `sql/knime_logit_metrics.sql`.
- [ ] `python_sql_scripts/` (01–07 `.py`, `common.py`, `run_all.py`, `requirements.txt`, `.env.example`; **không** commit `.env`).
- [ ] Excel kết quả query trong `python_sql_scripts/results/`.
- [ ] Workflow KNIME K-Means đã export (`.knwf`).
- [ ] Workflow KNIME Logistic Regression đã export (`.knwf`).
- [ ] Power BI `.pbix`.
- [ ] README.
- [ ] Link GitHub/workspace.
- [ ] Live demo hoặc video.
- [ ] Trích dẫn nguồn.
- [ ] Khai báo sử dụng AI.

### Bằng chứng rubric

- [ ] Row count cho thấy 10M ratings.
- [ ] MySQL schema, keys và indexes.
- [ ] SQL filter, aggregate, join và KPI.
- [ ] KNIME đọc trực tiếp MySQL.
- [ ] Tên node và annotation rõ ràng.
- [ ] K-Means silhouette và diễn giải cluster.
- [ ] Logistic accuracy, precision, recall, F1, AUC, confusion matrix và baseline.
- [ ] Time-based split và giải thích data leakage.
- [ ] `user_segments` đã ghi về MySQL.
- [ ] `rating_predictions` và `model_metrics` đã ghi về MySQL.
- [ ] Dashboard đọc dữ liệu từ MySQL.
- [ ] Output ML xuất hiện trên dashboard.
- [ ] Ít nhất 3 recommendation có số liệu.
- [ ] Limitations không bị che giấu.

---

## 31. Kế hoạch theo buổi

| Buổi | Công việc | Đầu ra |
|---:|---|---|
| 1 | Chốt problem, stakeholder, câu hỏi, dataset | Project charter 1 trang |
| 2 | Tải data, tạo database, import | Raw tables + row counts |
| 3 | Quality checks, genres, indexes | Bằng chứng SQL |
| 4 | Time split và feature tables | SQL tái lập được |
| 5 | Chuẩn bị dữ liệu K-Means trong KNIME | Workflow user profile |
| 6 | Chọn K, profile, write-back | `user_segments` |
| 7 | View feature Logistic và workflow training | Mô hình ứng viên |
| 8 | Validation, threshold, final test | Metrics cuối cùng |
| 9 | Write-back và dashboard views | Lớp kết quả trong MySQL |
| 10 | Các trang Power BI | Dashboard chạy được |
| 11 | Insight, recommendation, report | Bản nháp report |
| 12 | Chạy lại pipeline sạch, quay demo | Bộ hồ sơ nộp bài |

Nếu làm nhóm:

| Thành viên | Phụ trách |
|---|---|
| A | MySQL / import / SQL |
| B | K-Means / EDA |
| C | Logistic Regression / evaluation |
| D | Power BI / report / ghép demo |

Mỗi thành viên vẫn phải hiểu toàn bộ pipeline để demo.

---

## 32. Definition of Done

Project chỉ được xem là hoàn thành khi một người khác có thể:

1. Tải MovieLens 10M từ link chính thức.
2. Chạy các SQL scripts theo đúng thứ tự (trong Workbench, hoặc `py .\python_sql_scripts\run_all.py`).
3. Mở KNIME, nhập credential và execute hai workflow.
4. Thấy `user_segments`, `rating_predictions`, `model_metrics` trong MySQL.
5. Refresh Power BI từ MySQL.
6. Tái tạo các KPI, model metrics và recommendation trong report.

Nếu chỉ có screenshot mà không chạy lại được pipeline, project chưa đạt yêu cầu reproducibility của đề bài.

---

## 33. Các lỗi dễ mất điểm

- Gọi đây là dự báo lượt xem trong khi target chỉ là rating.
- Random split dữ liệu có timestamp.
- Tạo user/movie averages từ toàn bộ dataset, làm rò rỉ TEST vào TRAIN.
- Đưa `user_id` và `movie_id` trực tiếp vào Logistic Regression như biến số liên tục.
- Chọn K chỉ vì hình cluster đẹp.
- Dashboard chỉ có top movies và average rating, không có output ML.
- Recommendation không kèm số liệu.
- Đưa raw CSV trực tiếp vào Power BI.
- Không ghi kết quả trở lại MySQL.
- Commit dataset hoặc database password lên GitHub.
- Tuyên bố tăng doanh thu/giảm churn khi không có dữ liệu tài chính/subscription.
- Không nêu tuổi dataset, exposure bias và giới hạn warm-start.
- Trộn nhiều `model_version` trên cùng một visual (luôn có slicer model version).

---

## 34. Điểm cộng

Khi các mục bắt buộc đã xong, ưu tiên nâng cấp theo thứ tự:

1. Có model version và run timestamp trong mọi bảng kết quả.
2. Có baseline cho Logistic Regression.
3. Có bảng so sánh K và silhouette.
4. Có chronological split và giải thích leakage rõ ràng.
5. Có minimum-support filter trên Content Opportunity Matrix.
6. Có trang Model Governance.
7. Mỗi recommendation có evidence, action và success KPI.
8. Pipeline chạy lại được từ README (`run_all.py`).
9. Phân biệt rõ observed evidence, prediction và thử nghiệm tương lai.
10. Demo được MySQL → KNIME → MySQL → Power BI mà không cần sửa tay dữ liệu.
