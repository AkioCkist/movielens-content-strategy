# MovieLens 10M Final Project - Ke hoach trien khai chi tiet

> **De tai:** Segment-Based Movie Promotion and Content Discovery Strategy  
> **Ten tieng Viet:** Phan khuc khan gia va du bao kha nang yeu thich phim de ho tro chien luoc quang ba noi dung  
> **Dataset:** MovieLens 10M  
> **Mo hinh chinh:** K-Means + Logistic Regression  
> **Pipeline bat buoc:** Dataset -> MySQL -> KNIME -> MySQL Results -> Power BI -> Decision Recommendations

---

## 1. Muc tieu cua tai lieu

Tai lieu nay la ke hoach thuc hien end-to-end cho final project. No bao gom:

- cach tai va kiem tra MovieLens 10M;
- thiet ke bai toan ra quyet dinh;
- cac thao tac trong MySQL Workbench;
- cac thao tac trong KNIME cho K-Means va Logistic Regression;
- cach ghi ket qua tu KNIME ve MySQL;
- cach tao dashboard trong Power BI;
- code SQL va DAX can thiet;
- cau truc report, README, video demo va GitHub/workspace;
- checklist deliverables bam sat rubric.

Day la tai lieu trien khai. Cac nguong nhu so cluster, xac suat `0.70` hay minimum support `50` chi la gia tri khoi dau. Ket qua cuoi cung phai duoc chon dua tren du lieu va evaluation thuc te.

---

## 2. Tom tat de bai va dieu kien dat

Project duoc cham tren 6 phan:

| Phan | Diem | Bang chung can co |
|---|---:|---|
| Data Problem Definition & Decision Questions | 1.5 | Dataset that, stakeholder, problem statement, it nhat 3 cau hoi do luong duoc |
| MySQL Database & SQL Queries | 1.5 | Schema, import, keys, filter, aggregate, join, KPI, script tai chay duoc |
| KNIME Workflow & Data Preparation | 2.0 | Doc truc tiep tu MySQL, cleaning, transform, EDA, node names/annotations, write-back |
| Machine Learning & Evaluation | 2.0 | Mo hinh phu hop, features/target, preprocessing, metric, leakage control, limitations |
| Dashboard, Insights & Decisions | 2.0 | Du lieu tu MySQL, KPI, visual, filter, ML output, it nhat 3 recommendations |
| Documentation & Demonstration | 1.0 | Report, dataset reference, SQL, KNIME, PBIX, README, demo, citations, AI disclosure |

### Dieu kien khong duoc vi pham

- KNIME phai ket noi truc tiep MySQL.
- KNIME phai ghi ket qua mo hinh tro lai MySQL.
- Dashboard phai dung du lieu co nguon tu MySQL.
- Khong nop giai phap chi doc CSV.
- Khong commit password, credentials hoac du lieu ca nhan len GitHub.
- Phai ghi nguon dataset va khai bao phan ho tro cua AI.

---

## 3. Linh hon cua project

### 3.1 Stakeholder

**Content Programming and Personalization Manager** cua mot nen tang xem phim.

### 3.2 Problem statement

> A movie platform serves users with different preferences, but popularity-based promotion treats all audiences similarly. This project identifies audience segments from historical rating behaviour and predicts the probability that a user will positively rate a movie. The results support segment-specific movie promotion and content discovery decisions.

### 3.3 Quyet dinh trung tam

> Nen tang nen uu tien quang ba phim hoac the loai nao cho tung phan khuc khan gia?

### 3.4 Dinh nghia positive engagement

Trong project nay:

```text
Positive engagement = rating >= 4.0
```

Day la proxy cho viec nguoi dung yeu thich phim. Khong duoc dien giai thanh luot xem, doanh thu, churn hoac subscription.

### 3.5 Bon decision questions

1. Hanh vi rating va so thich the loai khac nhau nhu the nao giua cac nhom nguoi dung?
2. Co the chia nguoi dung thanh nhung audience segments ro rang nao?
3. Dua tren lich su nguoi dung va dac diem phim, xac suat nguoi dung rating phim tu 4 sao tro len la bao nhieu?
4. Phim/the loai nao co predicted positive engagement cao nhung muc do pho bien hien tai con thap trong tung segment?

### 3.6 Lien ket giua hai mo hinh

```text
10M ratings
    -> tao user profiles
    -> K-Means tao audience segments
    -> segment tro thanh mot feature cua Logistic Regression
    -> Logistic Regression tao probability of like
    -> tong hop Segment x Movie
    -> dashboard Content Opportunity Matrix
    -> quyet dinh Promote / Maintain / Reduce priority / Monitor
```

---

## 4. Dataset

### 4.1 Dataset duoc chon

**MovieLens 10M** cua GroupLens:

- 10,000,054 ratings;
- 95,580 tag applications;
- 10,681 movies;
- 71,567 users;
- moi user co it nhat 20 ratings;
- rating tu 0.5 den 5.0;
- user duoc an danh;
- khong co demographic information.

Nguon chinh thuc:

- Dataset page: <https://grouplens.org/datasets/movielens/10m/>
- README va data dictionary: <https://files.grouplens.org/datasets/movielens/ml-10m-README.html>

### 4.2 Files trong dataset

```text
movies.dat   -> MovieID::Title::Genres
ratings.dat  -> UserID::MovieID::Rating::Timestamp
tags.dat     -> UserID::MovieID::Tag::Timestamp
```

### 4.3 Gioi han phai neu trong report

- Dataset duoc phat hanh nam 2009, khong dai dien day du cho thi truong streaming hien tai.
- Khong co luot xem, exposure, click, watch time, subscription, revenue hoac chi phi ban quyen.
- Khong co demographic information.
- User trong dataset deu co it nhat 20 ratings, do do thien ve nhom active raters.
- Neu user khong rating mot phim, ta khong biet ho chua thay phim hay da thay nhung khong quan tam.
- Prediction chi la `probability of positive rating`, khong phai `probability of watching`.

### 4.4 Quy tac license/GitHub

Khong commit file dataset goc len GitHub neu chua co quyen redistribute. Repository chi can:

- link tai chinh thuc;
- citation;
- checksum neu co;
- huong dan tai va import;
- script tai tao pipeline.

---

## 5. Phan mem can dung

| Phan mem | Muc dich |
|---|---|
| MySQL Server 8.x | Luu 10M ratings, join, aggregate, feature tables, model results |
| MySQL Workbench | Chay SQL, import va kiem tra database |
| KNIME Analytics Platform | Data preparation, K-Means, Logistic Regression, evaluation, write-back |
| Power BI Desktop | Dashboard va interaction |
| Git/GitHub hoac workspace | Nop source, scripts, workflow va huong dan |
| Screen recorder | Quay demo neu khong demo live |

### Tai nguyen may khuyen nghi

- RAM: 16 GB toi thieu, 32 GB se thoai mai hon.
- Disk trong: toi thieu 30-50 GB.
- Khong doc 10M rows vao KNIME cho moi thao tac; filter/aggregate trong MySQL truoc.
- Power BI chi doc dashboard marts va prediction summaries, khong doc raw review text vi dataset nay khong co review text.

---

## 6. Cau truc thu muc project

```text
movielens-content-strategy/
|-- README.md
|-- .gitignore
|-- data/
|   |-- README_DATA.md
|   `-- checksums.txt
|-- sql/
|   |-- 01_create_schema.sql
|   |-- 02_load_data.sql
|   |-- 03_quality_checks.sql
|   |-- 04_create_splits.sql
|   |-- 05_feature_tables.sql
|   |-- 06_logistic_features.sql
|   `-- 07_dashboard_views.sql
|-- knime/
|   |-- movielens_audience_segmentation.knwf
|   `-- movielens_like_prediction.knwf
|-- dashboard/
|   `-- movielens_content_strategy.pbix
|-- report/
|   `-- final_report.pdf
|-- screenshots/
|-- demo/
|   `-- demo_script.md
`-- docs/
    |-- data_dictionary.md
    `-- ai_use_statement.md
```

`.gitignore` de xuat:

```gitignore
data/ml-10M100K/
*.zip
*.log
*.tmp
.env
credentials*
```

---

# PHASE A - MYSQL DATABASE

## 7. Tai va kiem tra dataset

### Thao tac

1. Mo trang MovieLens 10M chinh thuc.
2. Tai `ml-10m.zip`.
3. Doc README va license.
4. Giai nen vao thu muc local khong commit len GitHub.
5. Kiem tra co ba file `movies.dat`, `ratings.dat`, `tags.dat`.
6. Ghi link dataset va ngay truy cap vao `data/README_DATA.md`.

### Bang chung can chup

- Trang nguon GroupLens.
- Thu muc dataset sau khi giai nen.
- README cho thay row counts va data format.

---

## 8. Tao database va raw tables

Trong MySQL Workbench, tao SQL tab va luu noi dung sau thanh `sql/01_create_schema.sql`.

```sql
CREATE DATABASE IF NOT EXISTS movielens_strategy
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE movielens_strategy;

CREATE TABLE movies (
    movie_id INT UNSIGNED NOT NULL,
    title VARCHAR(500) NOT NULL,
    genres VARCHAR(255) NOT NULL,
    PRIMARY KEY (movie_id)
) ENGINE=InnoDB;

CREATE TABLE ratings (
    rating_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    movie_id INT UNSIGNED NOT NULL,
    rating DECIMAL(2,1) NOT NULL,
    rating_ts INT UNSIGNED NOT NULL,
    PRIMARY KEY (rating_id)
) ENGINE=InnoDB;

CREATE TABLE tags (
    tag_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    movie_id INT UNSIGNED NOT NULL,
    tag_text VARCHAR(500) NOT NULL,
    tag_ts INT UNSIGNED NOT NULL,
    PRIMARY KEY (tag_id)
) ENGINE=InnoDB;

CREATE TABLE movie_genres (
    movie_id INT UNSIGNED NOT NULL,
    genre VARCHAR(50) NOT NULL,
    PRIMARY KEY (movie_id, genre),
    INDEX idx_movie_genres_genre (genre)
) ENGINE=InnoDB;
```

### Tai sao chua tao tat ca indexes ngay?

Bulk import 10M rows nhanh hon neu import truoc, tao secondary indexes sau. Primary key van duoc giu de tao `rating_id`.

---

## 9. Import MovieLens vao MySQL

### 9.1 Bat LOCAL INFILE

Neu co quyen administrator:

```sql
SET GLOBAL local_infile = 1;
```

Trong MySQL Workbench, mo connection settings va bat `OPT_LOCAL_INFILE=1` neu can. Sau do reconnect.

### 9.2 Load movies

Thay duong dan bang duong dan that tren may. Dung dau `/` trong MySQL path tren Windows.

```sql
USE movielens_strategy;

LOAD DATA LOCAL INFILE 'C:/path/to/ml-10M100K/movies.dat'
INTO TABLE movies
CHARACTER SET utf8mb4
FIELDS TERMINATED BY '::'
LINES TERMINATED BY '\n'
(@movie_id, @title, @genres)
SET
    movie_id = CAST(@movie_id AS UNSIGNED),
    title = @title,
    genres = TRIM(TRAILING '\r' FROM @genres);
```

### 9.3 Load ratings

```sql
LOAD DATA LOCAL INFILE 'C:/path/to/ml-10M100K/ratings.dat'
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
```

### 9.4 Load tags

```sql
LOAD DATA LOCAL INFILE 'C:/path/to/ml-10M100K/tags.dat'
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
```

### 9.5 Tao indexes sau import

```sql
CREATE INDEX idx_ratings_user ON ratings(user_id);
CREATE INDEX idx_ratings_movie ON ratings(movie_id);
CREATE INDEX idx_ratings_ts ON ratings(rating_ts);
CREATE INDEX idx_ratings_user_ts ON ratings(user_id, rating_ts);
CREATE INDEX idx_ratings_movie_ts ON ratings(movie_id, rating_ts);

CREATE INDEX idx_tags_user ON tags(user_id);
CREATE INDEX idx_tags_movie ON tags(movie_id);
```

### 9.6 Tach genres thanh bang quan he

Yeu cau MySQL 8.x:

```sql
INSERT IGNORE INTO movie_genres(movie_id, genre)
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
```

---

## 10. Data quality checks

Luu thanh `sql/03_quality_checks.sql`.

```sql
USE movielens_strategy;

SELECT COUNT(*) AS rating_rows FROM ratings;
SELECT COUNT(*) AS movie_rows FROM movies;
SELECT COUNT(*) AS tag_rows FROM tags;
SELECT COUNT(DISTINCT user_id) AS users FROM ratings;
SELECT COUNT(DISTINCT movie_id) AS rated_movies FROM ratings;

SELECT MIN(rating), MAX(rating), AVG(rating)
FROM ratings;

SELECT
    FROM_UNIXTIME(MIN(rating_ts)) AS first_rating,
    FROM_UNIXTIME(MAX(rating_ts)) AS last_rating
FROM ratings;

SELECT rating, COUNT(*) AS rating_count
FROM ratings
GROUP BY rating
ORDER BY rating;

SELECT COUNT(*) AS orphan_ratings
FROM ratings AS r
LEFT JOIN movies AS m ON r.movie_id = m.movie_id
WHERE m.movie_id IS NULL;

SELECT user_id, movie_id, COUNT(*) AS duplicate_count
FROM ratings
GROUP BY user_id, movie_id
HAVING COUNT(*) > 1
LIMIT 20;

SELECT
    COUNT(*) AS invalid_rows
FROM ratings
WHERE rating NOT BETWEEN 0.5 AND 5.0
   OR MOD(rating * 10, 5) <> 0;
```

### Ket qua ky vong

- Ratings gan 10,000,054 rows.
- Rating nam trong 0.5-5.0.
- Khong co orphan movie IDs.
- Neu co duplicate user-movie pairs, phai xac dinh do la rating update hay duplicate truoc khi loai.

### Bang chung can chup

- `SELECT COUNT(*)` cua ratings.
- Rating distribution.
- Khoang thoi gian dataset.
- Ket qua orphan/invalid checks.

---

## 11. Chia train, validation, test theo thoi gian

Khong random split vi muc tieu la du bao tuong lai tu lich su. Tao bang split theo thu tu timestamp.

Luu thanh `sql/04_create_splits.sql`.

```sql
USE movielens_strategy;

DROP TABLE IF EXISTS rating_split;

CREATE TABLE rating_split AS
SELECT
    rating_id,
    CASE
        WHEN time_bucket <= 14 THEN 'TRAIN'
        WHEN time_bucket <= 17 THEN 'VALID'
        ELSE 'TEST'
    END AS data_split
FROM (
    SELECT
        rating_id,
        NTILE(20) OVER (ORDER BY rating_ts, rating_id) AS time_bucket
    FROM ratings
) AS ranked_ratings;

ALTER TABLE rating_split
    MODIFY rating_id BIGINT UNSIGNED NOT NULL,
    MODIFY data_split VARCHAR(5) NOT NULL,
    ADD PRIMARY KEY (rating_id),
    ADD INDEX idx_rating_split_name (data_split);

SELECT
    s.data_split,
    COUNT(*) AS rows_in_split,
    MIN(FROM_UNIXTIME(r.rating_ts)) AS period_start,
    MAX(FROM_UNIXTIME(r.rating_ts)) AS period_end
FROM rating_split AS s
JOIN ratings AS r ON r.rating_id = s.rating_id
GROUP BY s.data_split
ORDER BY MIN(r.rating_ts);
```

Ty le xap xi:

- TRAIN: 70%
- VALID: 15%
- TEST: 15%

Khong dung TEST de chon K, chon threshold hoac chinh feature.

---

## 12. Tao feature tables tu TRAIN only

Tat ca profile phai duoc tao tu TRAIN de tranh nhin thay tuong lai.

Luu thanh `sql/05_feature_tables.sql`.

### 12.1 User statistics

```sql
DROP TABLE IF EXISTS train_user_stats;

CREATE TABLE train_user_stats AS
SELECT
    r.user_id,
    COUNT(*) AS rating_count,
    SUM(r.rating) AS rating_sum,
    AVG(r.rating) AS avg_rating,
    STDDEV_SAMP(r.rating) AS rating_stddev,
    SUM(CASE WHEN r.rating >= 4.0 THEN 1 ELSE 0 END) AS positive_count,
    AVG(CASE WHEN r.rating >= 4.0 THEN 1.0 ELSE 0.0 END) AS positive_rate,
    COUNT(DISTINCT r.movie_id) AS distinct_movies,
    MIN(r.rating_ts) AS first_rating_ts,
    MAX(r.rating_ts) AS last_rating_ts,
    DATEDIFF(
        FROM_UNIXTIME(MAX(r.rating_ts)),
        FROM_UNIXTIME(MIN(r.rating_ts))
    ) AS active_days
FROM ratings AS r
JOIN rating_split AS s ON s.rating_id = r.rating_id
WHERE s.data_split = 'TRAIN'
GROUP BY r.user_id;

ALTER TABLE train_user_stats
    ADD PRIMARY KEY (user_id);
```

### 12.2 Movie statistics

```sql
DROP TABLE IF EXISTS train_movie_stats;

CREATE TABLE train_movie_stats AS
SELECT
    r.movie_id,
    COUNT(*) AS rating_count,
    SUM(r.rating) AS rating_sum,
    AVG(r.rating) AS avg_rating,
    STDDEV_SAMP(r.rating) AS rating_stddev,
    SUM(CASE WHEN r.rating >= 4.0 THEN 1 ELSE 0 END) AS positive_count,
    AVG(CASE WHEN r.rating >= 4.0 THEN 1.0 ELSE 0.0 END) AS positive_rate,
    COUNT(DISTINCT r.user_id) AS distinct_users
FROM ratings AS r
JOIN rating_split AS s ON s.rating_id = r.rating_id
WHERE s.data_split = 'TRAIN'
GROUP BY r.movie_id;

ALTER TABLE train_movie_stats
    ADD PRIMARY KEY (movie_id);
```

### 12.3 User-genre statistics

```sql
DROP TABLE IF EXISTS train_user_genre_stats;

CREATE TABLE train_user_genre_stats AS
SELECT
    r.user_id,
    mg.genre,
    COUNT(*) AS genre_rating_count,
    AVG(r.rating) AS genre_avg_rating,
    AVG(CASE WHEN r.rating >= 4.0 THEN 1.0 ELSE 0.0 END) AS genre_positive_rate
FROM ratings AS r
JOIN rating_split AS s
    ON s.rating_id = r.rating_id
JOIN movie_genres AS mg
    ON mg.movie_id = r.movie_id
WHERE s.data_split = 'TRAIN'
GROUP BY r.user_id, mg.genre;

ALTER TABLE train_user_genre_stats
    ADD PRIMARY KEY (user_id, genre),
    ADD INDEX idx_user_genre_genre (genre);
```

### 12.4 KPI SQL queries cho rubric

```sql
-- Filtering
SELECT *
FROM ratings
WHERE rating >= 4.0
  AND rating_ts >= UNIX_TIMESTAMP('2005-01-01')
LIMIT 100;

-- Grouping/aggregation
SELECT
    rating,
    COUNT(*) AS rating_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS rating_percent
FROM ratings
GROUP BY rating
ORDER BY rating;

-- Join + KPI
SELECT
    mg.genre,
    COUNT(*) AS rating_count,
    AVG(r.rating) AS avg_rating,
    AVG(CASE WHEN r.rating >= 4 THEN 1.0 ELSE 0.0 END) AS positive_rate
FROM ratings AS r
JOIN movie_genres AS mg ON mg.movie_id = r.movie_id
GROUP BY mg.genre
ORDER BY rating_count DESC;

-- Movie popularity with minimum support
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

---

# PHASE B - KNIME MODEL 1: K-MEANS

## 13. Ket noi KNIME voi MySQL

### Thao tac

1. Mo KNIME Analytics Platform.
2. Tao workflow `movielens_audience_segmentation`.
3. Keo node **MySQL Connector** vao canvas.
4. Cau hinh:
   - hostname: `localhost`;
   - port: `3306`;
   - database: `movielens_strategy`;
   - username: tai khoan local;
   - password: nhap trong credential setting, khong ghi vao workflow annotation hoac GitHub.
5. Test connection va execute node.
6. Them workflow annotation ghi ro database, muc tieu va ngay chay.

### Bang chung

- Screenshot MySQL Connector mau xanh.
- Screenshot database tables trong Workbench.

---

## 14. Workflow K-Means chi tiet

### 14.1 Branch A - Base user features

```text
MySQL Connector
 -> DB Table Selector: train_user_stats
 -> DB Reader
 -> Column Filter
```

Giu:

- `user_id`
- `rating_count`
- `avg_rating`
- `rating_stddev`
- `positive_rate`
- `distinct_movies`
- `active_days`

Khong dung `rating_sum`, `positive_count`, timestamps truc tiep trong clustering vi trung lap y nghia hoac scale lon.

### 14.2 Branch B - Genre affinity

```text
MySQL Connector
 -> DB Table Selector: train_user_genre_stats
 -> DB Reader
 -> Pivoting
 -> Missing Value
```

**Pivoting settings:**

- Group column: `user_id`
- Pivot column: `genre`
- Aggregation column: `genre_avg_rating`
- Aggregation: First hoac Mean

Sau pivot, moi genre tro thanh mot cot.

**Missing Value settings:**

- Neu user chua rating genre do, thay bang `avg_rating` cua user sau khi join, hoac 0 neu cot se duoc chuyen thanh affinity.
- Uu tien affinity = `genre_avg_rating - user_avg_rating`.

### 14.3 Join va tao affinity

```text
Branch A
 + Branch B
 -> Joiner on user_id
 -> Column Expressions / Math Formula
```

Voi moi genre:

```text
genre_affinity = genre_avg_rating - user_avg_rating
```

Vi du:

```text
Action_affinity = Action - avg_rating
Comedy_affinity = Comedy - avg_rating
Drama_affinity = Drama - avg_rating
```

Neu user chua rating genre, affinity de 0 va co the them genre count de phan biet `neutral` voi `no evidence`.

### 14.4 Xu ly outliers va scale

```text
-> Numeric Outliers
-> Normalizer
```

De xuat:

- winsorize `rating_count`, `distinct_movies`, `active_days` tai 1st va 99th percentile;
- hoac log-transform cac bien count truoc khi normalize;
- Normalizer: Z-score;
- khong dua `user_id` vao model.

Ghi ro trong report vi K-Means nhay voi scale va outliers.

### 14.5 Chon K

Thu:

```text
K = 3, 4, 5, 6, 7, 8
```

Co hai cach:

1. Tao sau nhanh K-Means de de chup va so sanh.
2. Dung Parameter Optimization Loop neu da quen KNIME.

Voi moi K, luu:

- silhouette score;
- cluster size;
- centroid/profile;
- kha nang giai thich kinh doanh;
- do on dinh khi doi random seed.

Khong chon K chi vi silhouette cao nhat. Chon K co silhouette chap nhan duoc va tao segment de hanh dong.

### 14.6 Dat ten segment

Sau khi xem centroid, dat ten dua tren du lieu. Vi du co the xuat hien:

- Diverse Explorers;
- Mainstream Enthusiasts;
- Selective Critics;
- Genre Specialists;
- Casual Raters.

Khong dat ten truoc khi xem profile thuc te.

### 14.7 Workflow node naming

Dat ten node ro rang:

```text
01 Connect to MovieLens MySQL
02 Read TRAIN User Statistics
03 Read TRAIN Genre Statistics
04 Pivot Genres to User Level
05 Build Genre Affinity
06 Handle Outliers
07 Z-score Normalization
08 K-Means Candidate K
09 Evaluate Silhouette
10 Attach Business Segment Labels
11 Write User Segments to MySQL
```

Them annotation cho tung component: Input, Cleaning, Feature Engineering, Modeling, Evaluation, Write-back.

---

## 15. Ghi K-Means result ve MySQL

Ket qua can co:

```text
user_id
cluster_id
segment_name
distance_to_centroid (neu node cung cap)
model_version
model_run_date
```

Trong KNIME:

1. Join cluster assignment voi `user_id`.
2. Dung Rule Engine de gan `segment_name` sau khi da profile cluster.
3. Them constant columns `model_version` va `model_run_date`.
4. Noi lai MySQL Connector.
5. Dung **DB Writer**.
6. Output table: `user_segments`.
7. Chon replace table trong lan chay dau; cac lan sau co the dung versioned append.

Kiem tra trong Workbench:

```sql
SELECT * FROM user_segments LIMIT 20;

SELECT
    cluster_id,
    segment_name,
    COUNT(*) AS users
FROM user_segments
GROUP BY cluster_id, segment_name
ORDER BY cluster_id;
```

---

# PHASE C - KNIME MODEL 2: LOGISTIC REGRESSION

## 16. Tao logistic feature table

Muc tieu:

```text
liked = 1 neu rating >= 4.0
liked = 0 neu rating < 4.0
```

Feature chi duoc lay tu TRAIN history. Rieng TRAIN rows, dung leave-one-out cho cac aggregate lien quan den target de giam leakage.

Chay sau khi `user_segments` da duoc KNIME ghi ve MySQL. Luu thanh `sql/06_logistic_features.sql`.

```sql
USE movielens_strategy;

DROP VIEW IF EXISTS ml_rating_features;

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
        THEN (us.positive_count - CASE WHEN r.rating >= 4.0 THEN 1 ELSE 0 END)
             / (us.rating_count - 1)
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
        THEN (ms.positive_count - CASE WHEN r.rating >= 4.0 THEN 1 ELSE 0 END)
             / (ms.rating_count - 1)
        ELSE ms.positive_rate
    END AS movie_prior_positive_rate,

    ms.rating_count AS movie_popularity,
    ms.rating_stddev AS movie_rating_stddev,
    seg.cluster_id,

    CASE WHEN m.genres LIKE '%Action%' THEN 1 ELSE 0 END AS genre_action,
    CASE WHEN m.genres LIKE '%Adventure%' THEN 1 ELSE 0 END AS genre_adventure,
    CASE WHEN m.genres LIKE '%Animation%' THEN 1 ELSE 0 END AS genre_animation,
    CASE WHEN m.genres LIKE '%Children%' THEN 1 ELSE 0 END AS genre_children,
    CASE WHEN m.genres LIKE '%Comedy%' THEN 1 ELSE 0 END AS genre_comedy,
    CASE WHEN m.genres LIKE '%Crime%' THEN 1 ELSE 0 END AS genre_crime,
    CASE WHEN m.genres LIKE '%Documentary%' THEN 1 ELSE 0 END AS genre_documentary,
    CASE WHEN m.genres LIKE '%Drama%' THEN 1 ELSE 0 END AS genre_drama,
    CASE WHEN m.genres LIKE '%Fantasy%' THEN 1 ELSE 0 END AS genre_fantasy,
    CASE WHEN m.genres LIKE '%Film-Noir%' THEN 1 ELSE 0 END AS genre_film_noir,
    CASE WHEN m.genres LIKE '%Horror%' THEN 1 ELSE 0 END AS genre_horror,
    CASE WHEN m.genres LIKE '%Musical%' THEN 1 ELSE 0 END AS genre_musical,
    CASE WHEN m.genres LIKE '%Mystery%' THEN 1 ELSE 0 END AS genre_mystery,
    CASE WHEN m.genres LIKE '%Romance%' THEN 1 ELSE 0 END AS genre_romance,
    CASE WHEN m.genres LIKE '%Sci-Fi%' THEN 1 ELSE 0 END AS genre_scifi,
    CASE WHEN m.genres LIKE '%Thriller%' THEN 1 ELSE 0 END AS genre_thriller,
    CASE WHEN m.genres LIKE '%War%' THEN 1 ELSE 0 END AS genre_war,
    CASE WHEN m.genres LIKE '%Western%' THEN 1 ELSE 0 END AS genre_western

FROM ratings AS r
JOIN rating_split AS s
    ON s.rating_id = r.rating_id
JOIN movies AS m
    ON m.movie_id = r.movie_id
JOIN train_user_stats AS us
    ON us.user_id = r.user_id
JOIN train_movie_stats AS ms
    ON ms.movie_id = r.movie_id
JOIN user_segments AS seg
    ON seg.user_id = r.user_id
WHERE us.rating_count > 1
  AND ms.rating_count > 1;
```

### Ghi chu cold-start

View tren loai user/movie khong co du TRAIN history. Bao cao phai neu:

- model nay danh gia warm-start users va movies;
- cold-start recommendation nam ngoai scope;
- can thong ke bao nhieu VALID/TEST rows bi loai do cold-start.

Query:

```sql
SELECT data_split, COUNT(*) AS feature_rows
FROM ml_rating_features
GROUP BY data_split;
```

---

## 17. Workflow Logistic Regression chi tiet

Tao workflow `movielens_like_prediction`.

### 17.1 Doc training sample

Dung **DB Query Reader** voi query:

```sql
SELECT *
FROM ml_rating_features
WHERE data_split = 'TRAIN'
  AND MOD(rating_id, 5) = 0;
```

Day la deterministic 20% sample cua TRAIN, khoang 1.4M rows. Neu may yeu, doi `5` thanh `10`. Neu class imbalance lon, dung stratified sampling trong KNIME va ghi ro sampling ratio.

Khong dua `rating_id`, `user_id`, `movie_id`, `data_split` vao learner. Giu chung de join/write-back sau prediction.

### 17.2 Preprocessing nodes

```text
MySQL Connector
 -> DB Query Reader: TRAIN sample
 -> Missing Value
 -> Math Formula: log1p counts
 -> String Manipulation / Number to String: cluster_id
 -> One to Many: cluster_id
 -> Column Filter
 -> Normalizer
```

Numeric features can scale:

- `LOG(1 + user_activity)`
- `LOG(1 + movie_popularity)`
- `LOG(1 + user_active_days)`

Khong normalize binary genre flags.

### 17.3 Learner

```text
-> Logistic Regression Learner
```

Settings:

- Target column: `liked`
- Positive class: `1`
- Regularization: bat neu node ho tro;
- Maximum iterations: tang neu model chua converge;
- Luu coefficient table de interpret.

### 17.4 Validation

Branch doc validation:

```sql
SELECT *
FROM ml_rating_features
WHERE data_split = 'VALID';
```

Ap dung cung preprocessing settings tu TRAIN. Khong fit lai normalizer tren VALID.

Nodes:

```text
Validation DB Query Reader
 -> Apply trained preprocessing
 -> Logistic Regression Predictor
 -> Scorer
 -> ROC Curve
```

Dung VALID de:

- kiem tra overfitting;
- chon probability threshold;
- xem precision-recall trade-off;
- dieu chinh feature set;
- khong xem TEST trong giai doan nay.

### 17.5 Final test

Sau khi dong bang model va threshold:

```sql
SELECT *
FROM ml_rating_features
WHERE data_split = 'TEST';
```

Chay mot lan cuoi:

```text
Test DB Query Reader
 -> Apply trained preprocessing
 -> Logistic Regression Predictor
 -> Scorer
 -> ROC Curve
 -> DB Writer
```

### 17.6 Metrics phai bao cao

- Accuracy;
- Precision cho class liked;
- Recall cho class liked;
- F1-score;
- confusion matrix;
- ROC-AUC neu co;
- test row count;
- comparison voi majority-class baseline.

### 17.7 Interpretation

Tu coefficient table, tra loi:

- movie historical quality co anh huong manh khong;
- user rating tendency co lam thay doi probability khong;
- cluster nao co baseline propensity cao/thap;
- genre nao co association duong/am sau khi da kiem soat cac feature khac.

Khong dien giai coefficient thanh quan he nhan qua.

---

## 18. Ghi Logistic Regression results ve MySQL

Bang output can co:

```text
rating_id
user_id
movie_id
cluster_id
actual_liked
predicted_liked
probability_liked
data_split
model_version
model_run_date
```

Trong KNIME:

1. Chon cac cot tren sau Predictor.
2. Them `model_version`, vi du `logit_v1`.
3. Them ngay chay.
4. DB Writer -> table `rating_predictions`.
5. Ghi TEST results. Co the ghi VALID vao bang rieng neu can audit.

Kiem tra trong Workbench:

```sql
SELECT COUNT(*) FROM rating_predictions;

SELECT
    actual_liked,
    predicted_liked,
    COUNT(*) AS rows_count
FROM rating_predictions
GROUP BY actual_liked, predicted_liked;
```

Tao bang metric bang KNIME Table Creator hoac GroupBy output va ghi ve `model_metrics`:

```text
model_name
model_version
split_name
metric_name
metric_value
run_timestamp
```

---

# PHASE D - DASHBOARD MARTS VA POWER BI

## 19. Tao dashboard views trong MySQL

Luu thanh `sql/07_dashboard_views.sql`.

### 19.1 Overall KPI

```sql
CREATE OR REPLACE VIEW dashboard_kpis AS
SELECT
    (SELECT COUNT(*) FROM ratings) AS total_ratings,
    (SELECT COUNT(DISTINCT user_id) FROM ratings) AS total_users,
    (SELECT COUNT(*) FROM movies) AS total_movies,
    (SELECT COUNT(*) FROM tags) AS total_tags,
    (SELECT AVG(rating) FROM ratings) AS average_rating,
    (
        SELECT AVG(CASE WHEN rating >= 4.0 THEN 1.0 ELSE 0.0 END)
        FROM ratings
    ) AS positive_rating_rate;
```

### 19.2 Segment profiles

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
```

### 19.3 Segment-genre profile

```sql
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

### 19.4 Content opportunity view

```sql
CREATE OR REPLACE VIEW dashboard_content_opportunities AS
SELECT
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
JOIN (
    SELECT DISTINCT cluster_id, segment_name
    FROM user_segments
) AS seg ON seg.cluster_id = rp.cluster_id
GROUP BY
    rp.cluster_id,
    seg.segment_name,
    rp.movie_id,
    m.title,
    m.genres,
    ms.rating_count,
    ms.avg_rating;
```

Dashboard nen filter `test_support >= 30` hoac `>= 50`. Chon nguong cuoi dua tren phan phoi support, khong tuy tien.

### 19.5 Model metrics

Neu `model_metrics` da duoc KNIME ghi ve MySQL, Power BI doc truc tiep bang nay.

---

## 20. Ket noi Power BI voi MySQL

### Thao tac

1. Mo Power BI Desktop.
2. Home -> Get Data -> MySQL Database.
3. Server: `localhost:3306`.
4. Database: `movielens_strategy`.
5. Nhap credential local.
6. Chon **Import** cho cac view nho va summary marts.
7. Nap:
   - `dashboard_kpis`;
   - `dashboard_segment_profiles`;
   - `dashboard_segment_genres`;
   - `dashboard_content_opportunities`;
   - `model_metrics`;
   - `rating_predictions` neu can confusion matrix chi tiet.
8. Khong import raw `ratings` 10M rows vao Power BI neu khong can.
9. Trong Power Query, kiem tra data types.
10. Apply Changes.

### Moi quan he de xuat

- `dashboard_segment_profiles[cluster_id]` 1 -> many `dashboard_segment_genres[cluster_id]`.
- `dashboard_segment_profiles[cluster_id]` 1 -> many `dashboard_content_opportunities[cluster_id]`.
- Neu dung model metrics doc lap, khong can relationship.

---

## 21. DAX measures co ban

```DAX
Total Ratings =
MAX(dashboard_kpis[total_ratings])

Total Users =
MAX(dashboard_kpis[total_users])

Total Movies =
MAX(dashboard_kpis[total_movies])

Positive Rating Rate =
MAX(dashboard_kpis[positive_rating_rate])

Average Predicted Like Probability =
AVERAGE(dashboard_content_opportunities[predicted_like_probability])

Average Actual Positive Rate =
AVERAGE(dashboard_content_opportunities[actual_positive_rate])

Opportunity Gap =
[Average Predicted Like Probability] -
[Average Actual Positive Rate]

Supported Movies =
CALCULATE(
    DISTINCTCOUNT(dashboard_content_opportunities[movie_id]),
    dashboard_content_opportunities[test_support] >= 50
)
```

Khong nen tao mot `magic score` voi trong so tuy y neu khong co business justification.

---

## 22. Thiet ke dashboard

### Page 1 - Executive Overview

Muc tieu: mo ta quy mo va hanh vi tong quan.

Visuals:

- Cards: Total Ratings, Total Users, Total Movies, Positive Rating Rate.
- Rating distribution.
- Ratings over time neu co them time summary view.
- Top genres by rating count.
- Top supported movies.

Thong diep: du lieu du lon va co cau truc phu hop cho audience analysis.

### Page 2 - Audience Segments

Muc tieu: trinh bay K-Means.

Visuals:

- Segment size bar chart.
- Segment profile table.
- Genre affinity/positive-rate heatmap.
- Scatter: avg activity vs avg positive rate, color by segment.
- Slicer: segment, genre.
- Text box mo ta business meaning cua tung segment.

Thong diep: mot chien luoc top-movies cho tat ca user la khong phu hop.

### Page 3 - Positive Engagement Model

Muc tieu: trinh bay Logistic Regression.

Visuals:

- Accuracy, Precision, Recall, F1 cards.
- Confusion matrix.
- ROC/AUC neu da luu du lieu duong cong hoac screenshot tu KNIME.
- Actual vs predicted positive rate.
- Model coefficient chart cho top positive/negative features.

Thong diep: model co kha nang xep hang co hoi noi dung, nhung khong chung minh quan he nhan qua.

### Page 4 - Content Opportunity Matrix

Day la trang ra quyet dinh chinh.

Scatter chart:

- X: `train_popularity`
- Y: `predicted_like_probability`
- Bubble size: `test_support`
- Legend/color: genre hoac segment
- Details: movie title
- Slicer: segment, genre, minimum support

Bon vung dien giai:

| Popularity | Predicted like | Dien giai | Hanh dong |
|---|---|---|---|
| Cao | Cao | Proven hit | Maintain visibility |
| Thap | Cao | Hidden opportunity | Promote/curate |
| Cao | Thap | Overexposed for segment | Reduce segment targeting |
| Thap | Thap | Low priority | Do not prioritise |

Khong ket luan `promotion se tang doanh thu`. Ket luan dung la `day la ung vien de thu nghiem promotion`.

### Page 5 - Model Governance (khuyen nghi)

- Train/validation/test time periods.
- So rows tung split.
- Model version va run date.
- K-Means silhouette by K.
- Logistic metrics va baseline.
- Known limitations.

Trang nay giup bai co tinh hoc thuat va reproducibility.

---

# PHASE E - INSIGHTS VA DECISIONS

## 23. Cach viet insight

Moi insight dung cau truc:

```text
Observation -> Evidence -> Meaning -> Decision implication
```

Vi du template:

> Segment [name] chiem [x%] users, co [genre] positive rate [y%] va predicted like probability [z%] cho nhom phim [type]. Dieu nay cho thay mot chien luoc quang ba rieng co the phu hop hon bang xep hang toan nen tang.

Khong dien so gia. Chi dien sau khi pipeline va dashboard co ket qua that.

---

## 24. Ba recommendations bat buoc

### Recommendation 1 - Segment-specific promotion

```text
Target segment:
Evidence:
Recommended content/genre:
Action:
Success KPI:
Limitation:
```

### Recommendation 2 - Hidden-content discovery

Chon phim co:

- predicted like cao;
- popularity thap hoac trung binh;
- support du lon;
- actual positive rate chap nhan duoc.

De xuat dua vao curated collection cho dung segment.

### Recommendation 3 - Reduce broad promotion

Chon phim pho bien toan he thong nhung affinity thap trong mot segment cu the. De xuat giam uu tien cho segment do, khong xoa phim khoi catalog.

### Recommendation 4 - Controlled experiment (bonus)

De xuat A/B test ngoai pham vi dataset:

- control: popularity-based list;
- treatment: segment-based content list;
- KPI: click-through, play-start, completion hoac explicit rating rate.

Day la de xuat thu nghiem tuong lai, khong duoc tuyen bo MovieLens da chung minh uplift.

---

# PHASE F - REPORT, GITHUB VA DEMO

## 25. Cau truc final report

### Cover page

- Project title.
- Course.
- Team members va student IDs.
- Academic integrity statement/signatures neu duoc yeu cau.

### 1. Executive Summary

- Business problem.
- Dataset size.
- Two models.
- Main findings.
- Three decisions.

### 2. Business Context and Decision Questions

- Stakeholder.
- Why the decision matters.
- Constraints.
- Problem statement.
- Four decision questions.

### 3. Dataset

- Source and citation.
- Rows, users, movies, tags.
- Variables.
- License.
- Suitability.
- Limitations.

### 4. MySQL Architecture and SQL Analysis

- ER diagram.
- Table structures and keys.
- Import process.
- Quality checks.
- Filtering, aggregation, joins, KPI queries.
- Evidence of 10M rows.

### 5. KNIME Data Preparation

- MySQL connection.
- Feature engineering.
- Time split.
- Missing values/outliers.
- Normalization.
- Workflow screenshot with readable node names.

### 6. K-Means Audience Segmentation

- Features and reasons.
- K candidates.
- Silhouette.
- Cluster profiles.
- Segment naming and interpretation.
- Limitations.

### 7. Logistic Regression

- Target definition.
- Features.
- Leave-one-out/history design.
- Train/validation/test.
- Baseline.
- Metrics.
- Coefficient interpretation.
- Limitations.

### 8. MySQL Write-back and Reproducibility

- `user_segments`.
- `rating_predictions`.
- `model_metrics`.
- Row counts and model versions.

### 9. Dashboard and Insights

- Screenshot tung page.
- Decision question ma page tra loi.
- Cac insight co so lieu.

### 10. Recommendations

- It nhat 3 recommendations.
- Evidence -> action -> KPI.

### 11. Limitations and Future Work

- Dataset age.
- Selection/exposure bias.
- No revenue/watch data.
- Warm-start scope.
- No causal claims.
- Future A/B testing.

### 12. Conclusion

### References

- GroupLens dataset.
- MovieLens paper.
- KNIME/MySQL/Power BI documentation khi su dung.
- AI-use statement.

---

## 26. README bat buoc

README phai co:

1. Project overview.
2. Business decision.
3. Dataset source va license note.
4. Prerequisites.
5. Folder structure.
6. MySQL setup.
7. Thu tu chay SQL scripts.
8. Cach cau hinh KNIME credential.
9. Thu tu chay hai workflows.
10. Bang nao duoc write-back.
11. Cach refresh Power BI.
12. Expected outputs.
13. Known limitations.
14. Team contributions.
15. AI-use disclosure.

Thu tu tai tao:

```text
01_create_schema.sql
 -> 02_load_data.sql
 -> 03_quality_checks.sql
 -> 04_create_splits.sql
 -> 05_feature_tables.sql
 -> run K-Means KNIME workflow
 -> verify user_segments
 -> 06_logistic_features.sql
 -> run Logistic KNIME workflow
 -> verify rating_predictions/model_metrics
 -> 07_dashboard_views.sql
 -> refresh Power BI
```

---

## 27. AI-use declaration template

Chinh sua theo quy dinh cua VNUK va phan viec thuc te:

```text
Generative AI was used to support project planning, explain technical concepts,
review SQL/workflow structure, and improve the clarity of documentation. All
dataset choices, SQL execution, KNIME workflow construction, model evaluation,
dashboard development, interpretations, and final recommendations were verified
and completed by the project team. AI-generated suggestions were not treated as
evidence and were checked against the dataset and official documentation.
```

Khong khai sai pham vi AI da ho tro.

---

## 28. Kich ban demo 8-10 phut

### 0:00-1:00 - Business problem

- Stakeholder.
- Decision.
- Four questions.
- Vi sao MovieLens 10M phu hop.

### 1:00-2:30 - MySQL

- Show row count 10,000,054.
- Show schema va joins.
- Show train/validation/test periods.
- Show feature tables.

### 2:30-4:30 - KNIME K-Means

- Execute connection/read nodes.
- Giai thich user profile va genre affinity.
- Show K comparison/silhouette.
- Show cluster profiles.
- Show write-back `user_segments`.

### 4:30-6:30 - KNIME Logistic Regression

- Show target va features.
- Giai thich time split va leakage control.
- Show metrics/confusion matrix.
- Show coefficient interpretation.
- Show write-back `rating_predictions` va `model_metrics`.

### 6:30-9:00 - Power BI

- Audience overview.
- Segment profiles.
- Prediction performance.
- Content Opportunity Matrix.
- Three recommendations with numbers.

### 9:00-10:00 - Limitations and close

- No watch/revenue/exposure data.
- Dataset age.
- A/B test as future validation.

---

## 29. Delivery checklist

### File bat buoc

- [ ] Final report PDF.
- [ ] Dataset official source/reference; khong can nop raw data neu license/size khong phu hop.
- [ ] `01_create_schema.sql`.
- [ ] `02_load_data.sql`.
- [ ] `03_quality_checks.sql`.
- [ ] `04_create_splits.sql`.
- [ ] `05_feature_tables.sql`.
- [ ] `06_logistic_features.sql`.
- [ ] `07_dashboard_views.sql`.
- [ ] Exported KNIME K-Means workflow.
- [ ] Exported KNIME Logistic Regression workflow.
- [ ] Power BI `.pbix`.
- [ ] README.
- [ ] GitHub/workspace link.
- [ ] Live demo hoac recorded video.
- [ ] Source citations.
- [ ] AI-use disclosure.

### Bang chung rubric

- [ ] Row count cho thay 10M ratings.
- [ ] MySQL schema, keys va indexes.
- [ ] SQL filter, aggregate, join va KPI.
- [ ] KNIME doc truc tiep MySQL.
- [ ] Node names va annotations ro rang.
- [ ] K-Means silhouette va cluster interpretation.
- [ ] Logistic accuracy, precision, recall, F1 va confusion matrix.
- [ ] Time-based split va data leakage explanation.
- [ ] `user_segments` da ghi ve MySQL.
- [ ] `rating_predictions` da ghi ve MySQL.
- [ ] Dashboard doc data tu MySQL.
- [ ] ML outputs xuat hien tren dashboard.
- [ ] It nhat 3 recommendations co so lieu.
- [ ] Limitations khong bi che giau.

---

## 30. Ke hoach thuc hien theo buoi

| Buoi | Cong viec | Dau ra |
|---:|---|---|
| 1 | Chot problem, stakeholder, questions, dataset | Project charter 1 trang |
| 2 | Tai data, tao database, import | Raw tables + row counts |
| 3 | Quality checks, genres, indexes | SQL evidence |
| 4 | Time split va feature tables | Reproducible SQL |
| 5 | KNIME K-Means preparation | User profile workflow |
| 6 | Chon K, profile, write-back | `user_segments` |
| 7 | Logistic feature view va training workflow | Candidate model |
| 8 | Validation, threshold, final test | Final metrics |
| 9 | Write-back va dashboard marts | MySQL result layer |
| 10 | Power BI pages | Working dashboard |
| 11 | Insights, recommendations, report | Draft report |
| 12 | Re-run clean pipeline, record demo | Submission package |

Neu lam nhom:

- Person A: MySQL/import/SQL.
- Person B: K-Means/EDA.
- Person C: Logistic Regression/evaluation.
- Person D: Power BI/report/demo integration.

Moi thanh vien van phai hieu toan bo pipeline de demo.

---

## 31. Definition of Done

Project chi duoc xem la hoan thanh khi mot nguoi khac co the:

1. Tai MovieLens 10M tu link chinh thuc.
2. Chay cac SQL scripts theo dung thu tu.
3. Mo KNIME, nhap credential va execute hai workflows.
4. Nhin thay `user_segments`, `rating_predictions`, `model_metrics` trong MySQL.
5. Refresh Power BI tu MySQL.
6. Tai tao cac KPI, model metrics va recommendations trong report.

Neu chi co screenshot ma khong tai chay duoc pipeline, project chua dat muc tieu reproducibility cua de bai.

---

## 32. Cac loi de mat diem

- Goi day la du bao luot xem trong khi target chi la rating.
- Random split du lieu co timestamp.
- Tao user/movie averages tu toan bo dataset, lam ro ri TEST vao TRAIN.
- Dua `user_id` va `movie_id` truc tiep vao Logistic Regression nhu bien so lien tuc.
- Chon K chi vi hinh cluster dep.
- Dashboard chi co top movies va average rating, khong co output ML.
- Khuyen nghi khong kem so lieu.
- Dua raw CSV truc tiep vao Power BI.
- Khong ghi result tro lai MySQL.
- Commit dataset hoac database password len GitHub.
- Tuyen bo tang doanh thu/churn ma khong co du lieu tai chinh/subscription.
- Khong ghi dataset age, exposure bias va warm-start limitation.

---

## 33. Tieu chi de bai noi bat

Neu cac muc bat buoc da hoan thanh, uu tien cac nang cap sau:

1. Co model version va run timestamp trong moi result table.
2. Co baseline cho Logistic Regression.
3. Co comparison K va silhouette table.
4. Co chronological split va leakage explanation ro rang.
5. Co minimum-support filter tren Content Opportunity Matrix.
6. Co Model Governance dashboard page.
7. Moi recommendation co evidence, action va success KPI.
8. Co pipeline tai chay duoc tu README.
9. Co phan biet ro observed evidence, prediction va future experiment.
10. Demo duoc MySQL -> KNIME -> MySQL -> Power BI ma khong can sua tay du lieu.

