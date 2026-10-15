"""Generate the Power BI project (PBIP) for the MovieLens content strategy dashboard.

Output (next to this script):
  movielens_content_strategy.pbip
  movielens_content_strategy.SemanticModel/   model.bim (import from MySQL views)
  movielens_content_strategy.Report/          PBIR report, 5 pages

Open the .pbip in Power BI Desktop, refresh, then File > Save As > .pbix.
Regenerate after changing views or measures:  py dashboard/build_pbip.py
"""
from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAME = "movielens_content_strategy"
NS = uuid.UUID("6f1c2a52-6d3b-4c55-9a51-0e9c2d1f7a10")
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric"
S_VISUAL = f"{SCHEMA}/item/report/definition/visualContainer/1.4.0/schema.json"
S_PAGE = f"{SCHEMA}/item/report/definition/page/1.3.0/schema.json"


def tag(*parts: str) -> str:
    """Stable lineage tags, so regenerating does not churn every file."""
    return str(uuid.uuid5(NS, "/".join(parts)))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- model
M_TYPES = {"int64": "Int64.Type", "double": "type number", "string": "type text", "dateTime": "type datetime"}
FMT = {"int64": "#,0", "double": "#,0.0000", "dateTime": "yyyy-mm-dd hh:nn"}

# table -> [(column, dataType)], straight from the MySQL views in sql/07_dashboard_views.sql
SOURCE_TABLES = {
    "dashboard_kpis": [("total_ratings", "int64"), ("total_users", "int64"), ("total_movies", "int64"),
                       ("total_tags", "int64"), ("average_rating", "double"), ("positive_rating_rate", "double")],
    "dashboard_rating_distribution": [("rating", "double"), ("rating_count", "int64"), ("rating_share", "double")],
    "dashboard_genre_kpis": [("genre", "string"), ("rating_count", "int64"), ("avg_rating", "double"),
                             ("positive_rate", "double")],
    "dashboard_movie_popularity": [("movie_id", "int64"), ("title", "string"), ("genres", "string"),
                                   ("rating_count", "int64"), ("avg_rating", "double"), ("positive_rate", "double")],
    "dashboard_split_summary": [("data_split", "string"), ("rows_in_split", "int64"),
                                ("period_start", "dateTime"), ("period_end", "dateTime")],
    "dashboard_segment_profiles": [("cluster_id", "int64"), ("segment_name", "string"), ("user_count", "int64"),
                                   ("avg_user_ratings", "double"), ("avg_rating", "double"),
                                   ("avg_positive_rate", "double"), ("avg_rating_stddev", "double"),
                                   ("avg_active_days", "double")],
    "dashboard_segment_genres": [("cluster_id", "int64"), ("segment_name", "string"), ("genre", "string"),
                                 ("users_with_genre", "int64"), ("genre_rating_count", "int64"),
                                 ("avg_genre_rating", "double"), ("avg_genre_positive_rate", "double")],
    "dashboard_content_opportunities": [("model_version", "string"), ("cluster_id", "int64"),
                                        ("segment_name", "string"), ("movie_id", "int64"), ("title", "string"),
                                        ("genres", "string"), ("test_support", "int64"),
                                        ("predicted_like_probability", "double"), ("actual_positive_rate", "double"),
                                        ("train_popularity", "int64"), ("train_avg_rating", "double")],
    "dashboard_confusion_matrix": [("model_version", "string"), ("data_split", "string"), ("actual_liked", "int64"),
                                   ("predicted_liked", "int64"), ("row_count", "int64")],
    "dashboard_model_metrics": [("model_name", "string"), ("model_version", "string"), ("split_name", "string"),
                                ("metric_name", "string"), ("metric_value", "double"), ("run_timestamp", "dateTime")],
    "movie_genres": [("movie_id", "int64"), ("genre", "string")],
}
PERCENT = {"positive_rating_rate", "rating_share", "positive_rate", "avg_positive_rate", "avg_genre_positive_rate",
           "predicted_like_probability", "actual_positive_rate"}
# Keys and categories that must never be summed by a visual.
NO_SUM = {"cluster_id", "movie_id", "rating", "actual_liked", "predicted_liked"}
# View joins 10M rows and only changes when sql/04 reruns.
EXCLUDED_FROM_REFRESH = {"dashboard_split_summary"}


def m_partition(table: str, cols) -> list[str]:
    types = ", ".join(f'{{"{c}", {M_TYPES[t]}}}' for c, t in cols)
    return [
        "let",
        "    Source = MySQL.Database(MySQLServer, MySQLDatabase, [ReturnSingleDatabase = true]),",
        f'    Data = Source{{[Schema = MySQLDatabase, Item = "{table}"]}}[Data],',
        f"    Typed = Table.TransformColumnTypes(Data, {{{types}}})",
        "in",
        "    Typed",
    ]


def column(table: str, name: str, dtype: str, calculated: bool = False) -> dict:
    c = {"name": name, "dataType": dtype, "lineageTag": tag(table, name)}
    if calculated:
        c.update(type="calculatedTableColumn", isNameInferred=True, isDataTypeInferred=True, sourceColumn=f"[{name}]")
    else:
        c["sourceColumn"] = name
    if name in PERCENT:
        c["formatString"] = "0.0%"
    elif dtype in FMT:
        c["formatString"] = FMT[dtype]
    c["summarizeBy"] = "none" if (dtype in ("string", "dateTime") or name in NO_SUM) else "sum"
    return c


tables = []
for t, cols in SOURCE_TABLES.items():
    tbl = {
        "name": t,
        "lineageTag": tag(t),
        "columns": [column(t, c, d) for c, d in cols],
        "partitions": [{"name": t, "mode": "import", "source": {"type": "m", "expression": m_partition(t, cols)}}],
    }
    if t in EXCLUDED_FROM_REFRESH:
        tbl["excludeFromModelRefresh"] = True
    tables.append(tbl)


def calc_table(name, dax, cols, hidden=False):
    tbl = {
        "name": name,
        "lineageTag": tag(name),
        "columns": [column(name, c, d, calculated=True) for c, d in cols],
        "partitions": [{"name": name, "mode": "import", "source": {"type": "calculated", "expression": dax}}],
    }
    if hidden:
        tbl["isHidden"] = True
        for c in tbl["columns"]:
            c["isHidden"] = True
    return tbl


tables += [
    calc_table("Model Versions", """DISTINCT (
    UNION (
        SELECTCOLUMNS ( dashboard_content_opportunities, "model_version", dashboard_content_opportunities[model_version] ),
        SELECTCOLUMNS ( dashboard_confusion_matrix, "model_version", dashboard_confusion_matrix[model_version] ),
        SELECTCOLUMNS ( dashboard_model_metrics, "model_version", dashboard_model_metrics[model_version] )
    )
)""", [("model_version", "string")]),
    calc_table("Genres", """DISTINCT (
    UNION (
        SELECTCOLUMNS ( movie_genres, "genre", movie_genres[genre] ),
        SELECTCOLUMNS ( dashboard_segment_genres, "genre", dashboard_segment_genres[genre] )
    )
)""", [("genre", "string")]),
    calc_table("Min Support", 'SELECTCOLUMNS ( GENERATESERIES ( 0, 500, 10 ), "Min Support", [Value] )',
               [("Min Support", "int64")]),
    calc_table("Top Movies", """SELECTCOLUMNS (
    TOPN ( 20, dashboard_movie_popularity, dashboard_movie_popularity[avg_rating], DESC,
           dashboard_movie_popularity[rating_count], DESC ),
    "title", dashboard_movie_popularity[title],
    "rating_count", dashboard_movie_popularity[rating_count],
    "avg_rating", dashboard_movie_popularity[avg_rating],
    "positive_rate", dashboard_movie_popularity[positive_rate]
)""", [("title", "string"), ("rating_count", "int64"), ("avg_rating", "double"), ("positive_rate", "double")]),
]
for c in tables[-1]["columns"]:            # Top Movies: show values, never sum them
    c["summarizeBy"] = "none"
for c in next(t for t in tables if t["name"] == "Min Support")["columns"]:
    c["summarizeBy"] = "none"

MEASURES = [
    # Page 1
    ("Total Ratings", "MAX ( dashboard_kpis[total_ratings] )", "#,0"),
    ("Total Users", "MAX ( dashboard_kpis[total_users] )", "#,0"),
    ("Total Movies", "MAX ( dashboard_kpis[total_movies] )", "#,0"),
    ("Total Tags", "MAX ( dashboard_kpis[total_tags] )", "#,0"),
    ("Average Rating", "MAX ( dashboard_kpis[average_rating] )", "0.000"),
    ("Positive Rating Rate", "MAX ( dashboard_kpis[positive_rating_rate] )", "0.0%"),
    # Page 4 - weighted by test_support, so a movie with 1 TEST rating does not weigh as much as one with 5,000
    ("Test Support", "SUM ( dashboard_content_opportunities[test_support] )", "#,0"),
    ("Predicted Like Probability", """DIVIDE (
    SUMX ( dashboard_content_opportunities,
        dashboard_content_opportunities[predicted_like_probability] * dashboard_content_opportunities[test_support] ),
    [Test Support]
)""", "0.0%"),
    ("Actual Positive Rate", """DIVIDE (
    SUMX ( dashboard_content_opportunities,
        dashboard_content_opportunities[actual_positive_rate] * dashboard_content_opportunities[test_support] ),
    [Test Support]
)""", "0.0%"),
    ("Calibration Gap", "[Predicted Like Probability] - [Actual Positive Rate]", "+0.0%;-0.0%;0.0%"),
    ("Train Popularity", "MAX ( dashboard_content_opportunities[train_popularity] )", "#,0"),
    ("Min Support Value", "SELECTEDVALUE ( 'Min Support'[Min Support], 50 )", "#,0"),
    ("Passes Min Support", "IF ( [Test Support] >= [Min Support Value], 1, 0 )", "0"),
    ("Predicted Like (Supported)", "IF ( [Test Support] >= [Min Support Value], [Predicted Like Probability] )", "0.0%"),
    ("Test Support (Supported)", "IF ( [Test Support] >= [Min Support Value], [Test Support] )", "#,0"),
    ("Train Popularity (Supported)", "IF ( [Test Support] >= [Min Support Value], [Train Popularity] )", "#,0"),
    ("Supported Movies", """COUNTROWS (
    FILTER ( VALUES ( dashboard_content_opportunities[movie_id] ), [Test Support] >= [Min Support Value] )
)""", "#,0"),
    # Pages 3 and 5 - metrics written by sql/knime_logit_metrics.sql and KNIME
    ("Test Metric", """CALCULATE (
    MAX ( dashboard_model_metrics[metric_value] ),
    dashboard_model_metrics[split_name] = "TEST",
    dashboard_model_metrics[model_name] = "logistic_regression"
)""", "0.0%"),
    ("Test Accuracy", 'CALCULATE ( [Test Metric], dashboard_model_metrics[metric_name] = "accuracy" )', "0.0%"),
    ("Test Precision", 'CALCULATE ( [Test Metric], dashboard_model_metrics[metric_name] = "precision" )', "0.0%"),
    ("Test Recall", 'CALCULATE ( [Test Metric], dashboard_model_metrics[metric_name] = "recall" )', "0.0%"),
    ("Test F1", 'CALCULATE ( [Test Metric], dashboard_model_metrics[metric_name] = "f1" )', "0.0%"),
    ("Test AUC", 'CALCULATE ( [Test Metric], dashboard_model_metrics[metric_name] = "auc" )', "0.000"),
    ("Baseline Accuracy", 'CALCULATE ( [Test Metric], dashboard_model_metrics[metric_name] = "baseline_accuracy" )', "0.0%"),
    ("Lift vs Baseline", "[Test Accuracy] - [Baseline Accuracy]", "+0.0%;-0.0%;0.0%"),
    ("TEST Rows", 'CALCULATE ( [Test Metric], dashboard_model_metrics[metric_name] = "test_rows" )', "#,0"),
    ("Prediction Rows (TEST)", """CALCULATE (
    SUM ( dashboard_confusion_matrix[row_count] ),
    dashboard_confusion_matrix[data_split] = "TEST"
)""", "#,0"),
    ("Coefficient", """IF (
    LEFT ( SELECTEDVALUE ( dashboard_model_metrics[metric_name] ), 5 ) = "coef_",
    CALCULATE (
        MAX ( dashboard_model_metrics[metric_value] ),
        dashboard_model_metrics[split_name] = "TRAIN",
        dashboard_model_metrics[model_name] = "logistic_regression"
    )
)""", "0.000"),
    ("Silhouette", """IF (
    LEFT ( SELECTEDVALUE ( dashboard_model_metrics[metric_name] ), 12 ) = "silhouette_k",
    CALCULATE ( MAX ( dashboard_model_metrics[metric_value] ), dashboard_model_metrics[model_name] = "kmeans" )
)""", "0.000"),
]
measures_table = calc_table("_Measures", 'ROW ( "_", 0 )', [("_", "int64")])
measures_table["columns"][0]["isHidden"] = True
measures_table["measures"] = [
    {"name": n, "expression": e, "formatString": f, "lineageTag": tag("_Measures", n)} for n, e, f in MEASURES
]
tables.insert(0, measures_table)


def rel(frm_t, frm_c, to_t, to_c, many_to_many=False):
    r = {"name": tag("rel", frm_t, frm_c, to_t, to_c), "fromTable": frm_t, "fromColumn": frm_c,
         "toTable": to_t, "toColumn": to_c}
    if many_to_many:
        # oneDirection: the "to" table (movie_genres) filters the "from" table
        r.update(fromCardinality="many", toCardinality="many", crossFilteringBehavior="oneDirection")
    return r


relationships = [
    rel("dashboard_content_opportunities", "model_version", "Model Versions", "model_version"),
    rel("dashboard_confusion_matrix", "model_version", "Model Versions", "model_version"),
    rel("dashboard_model_metrics", "model_version", "Model Versions", "model_version"),
    rel("dashboard_segment_genres", "cluster_id", "dashboard_segment_profiles", "cluster_id"),
    rel("dashboard_content_opportunities", "cluster_id", "dashboard_segment_profiles", "cluster_id"),
    rel("dashboard_segment_genres", "genre", "Genres", "genre"),
    rel("movie_genres", "genre", "Genres", "genre"),
    # A genre slicer cannot filter the 'Action|Comedy' text column directly.
    rel("dashboard_content_opportunities", "movie_id", "movie_genres", "movie_id", many_to_many=True),
]


def m_parameter(name, value):
    return {
        "name": name,
        "kind": "m",
        "expression": f'"{value}" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]',
        "lineageTag": tag("param", name),
        "annotations": [{"name": "PBI_ResultType", "value": "Text"}],
    }


model_bim = {
    "name": NAME,
    "compatibilityLevel": 1600,
    "model": {
        "culture": "en-US",
        "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
        "defaultPowerBIDataSourceVersion": "powerBI_V3",
        "sourceQueryCulture": "en-US",
        "tables": tables,
        "relationships": relationships,
        "expressions": [m_parameter("MySQLServer", "localhost:3306"),
                        m_parameter("MySQLDatabase", "movielens_strategy")],
        "annotations": [
            {"name": "PBI_QueryOrder", "value": json.dumps(["MySQLServer", "MySQLDatabase", *SOURCE_TABLES])},
            {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"},
        ],
    },
}

# --------------------------------------------------------------------------- report
def src(entity):
    return {"SourceRef": {"Entity": entity}}


def C(t, c, display=None):
    p = {"field": {"Column": {"Expression": src(t), "Property": c}}, "queryRef": f"{t}.{c}", "nativeQueryRef": c}
    if display:
        p["displayName"] = display
    return p


def M(m, display=None, t="_Measures"):
    p = {"field": {"Measure": {"Expression": src(t), "Property": m}}, "queryRef": f"{t}.{m}", "nativeQueryRef": m}
    if display:
        p["displayName"] = display
    return p


AGG = {"Sum": 0, "Avg": 1, "Count": 2, "Min": 3, "Max": 4}


def A(fn, t, c, display=None):
    p = {"field": {"Aggregation": {"Expression": {"Column": {"Expression": src(t), "Property": c}},
                                   "Function": AGG[fn]}},
         "queryRef": f"{fn}({t}.{c})", "nativeQueryRef": f"{fn} of {c}"}
    if display:
        p["displayName"] = display
    return p


def lit(v):
    if isinstance(v, bool):
        return {"expr": {"Literal": {"Value": "true" if v else "false"}}}
    if isinstance(v, (int, float)):
        return {"expr": {"Literal": {"Value": f"{v}D"}}}
    return {"expr": {"Literal": {"Value": "'" + str(v).replace("'", "''") + "'"}}}


def title(text):
    return {"title": [{"properties": {"show": lit(True), "text": lit(text)}}]}


class Page:
    def __init__(self, name, display):
        self.name, self.display, self.visuals = name, display, []

    def add(self, vname, vtype, x, y, w, h, roles=None, title_text=None, objects=None, sort=None, sync=None):
        visual = {"visualType": vtype}
        if roles:
            visual["query"] = {"queryState": {role: {"projections": proj} for role, proj in roles.items()}}
            if sort:
                field, direction = sort
                visual["query"]["sortDefinition"] = {
                    "sort": [{"field": field["field"], "direction": direction}], "isDefaultSort": False}
        if objects:
            visual["objects"] = objects
        if title_text:
            visual["visualContainerObjects"] = title(title_text)
        if sync:
            visual["syncGroup"] = {"groupName": sync, "fieldChanges": True, "filterChanges": True}
        self.visuals.append({
            "$schema": S_VISUAL,
            "name": vname,
            "position": {"x": x, "y": y, "z": len(self.visuals) * 1000, "width": w, "height": h,
                         "tabOrder": len(self.visuals) * 1000},
            "visual": visual,
        })


def textbox(page, vname, x, y, w, h, lines):
    paragraphs = []
    for i, line in enumerate(lines):
        run = {"value": line}
        if i == 0:
            run["textStyle"] = {"fontWeight": "bold", "fontSize": "14pt"}
        paragraphs.append({"textRuns": [run]})
    page.add(vname, "textbox", x, y, w, h, objects={"general": [{"properties": {"paragraphs": paragraphs}}]})


def slicer(page, vname, x, y, w, h, field, label, single=False, sync=None):
    objects = {"data": [{"properties": {"mode": lit("Dropdown")}}]}
    if single:
        objects["selection"] = [{"properties": {"singleSelect": lit(True)}}]
    page.add(vname, "slicer", x, y, w, h, roles={"Values": [field]}, title_text=label, objects=objects, sync=sync)


def card(page, vname, x, y, w, h, measure, label):
    page.add(vname, "card", x, y, w, h, roles={"Values": [M(measure)]}, title_text=label)


pages = []

# Page 1 - Executive Overview
p = Page("p1_executive_overview", "1. Executive Overview")
for i, (m, label) in enumerate([("Total Ratings", "Ratings"), ("Total Users", "Users with ratings"),
                                ("Total Movies", "Movies"), ("Total Tags", "Tags"),
                                ("Average Rating", "Average rating"), ("Positive Rating Rate", "Rating >= 4.0")]):
    card(p, f"p1_card_{i}", 20 + 207 * i, 20, 197, 100, m, label)
p.add("p1_rating_distribution", "clusteredColumnChart", 20, 140, 610, 270,
      roles={"Category": [C("dashboard_rating_distribution", "rating", "Rating")],
             "Y": [A("Sum", "dashboard_rating_distribution", "rating_count", "Ratings")],
             "Tooltips": [A("Sum", "dashboard_rating_distribution", "rating_share", "Share")]},
      title_text="Rating distribution (all 10M ratings)")
p.add("p1_genre_kpis", "clusteredBarChart", 650, 140, 610, 270,
      roles={"Category": [C("dashboard_genre_kpis", "genre", "Genre")],
             "Y": [A("Sum", "dashboard_genre_kpis", "rating_count", "Ratings")],
             "Tooltips": [A("Avg", "dashboard_genre_kpis", "avg_rating", "Average rating"),
                          A("Avg", "dashboard_genre_kpis", "positive_rate", "Positive rate")]},
      title_text="Ratings by genre",
      sort=(A("Sum", "dashboard_genre_kpis", "rating_count"), "Descending"))
p.add("p1_top_movies", "tableEx", 20, 430, 1240, 270,
      roles={"Values": [C("Top Movies", "title", "Movie"), C("Top Movies", "rating_count", "TRAIN ratings"),
                        C("Top Movies", "avg_rating", "Average rating"), C("Top Movies", "positive_rate", "Positive rate")]},
      title_text="Top 20 movies in TRAIN (minimum 100 ratings)",
      sort=(C("Top Movies", "avg_rating"), "Descending"))
pages.append(p)

# Page 2 - Audience Segments
p = Page("p2_audience_segments", "2. Audience Segments")
slicer(p, "p2_slicer_segment", 20, 20, 300, 70, C("dashboard_segment_profiles", "segment_name"), "Segment")
slicer(p, "p2_slicer_genre", 340, 20, 300, 70, C("Genres", "genre"), "Genre")
p.add("p2_segment_size", "clusteredBarChart", 20, 110, 420, 290,
      roles={"Category": [C("dashboard_segment_profiles", "segment_name", "Segment")],
             "Y": [A("Sum", "dashboard_segment_profiles", "user_count", "Users")]},
      title_text="Users per segment")
p.add("p2_activity_vs_positive", "scatterChart", 460, 110, 400, 290,
      roles={"Category": [C("dashboard_segment_profiles", "segment_name", "Segment")],
             "X": [A("Avg", "dashboard_segment_profiles", "avg_user_ratings", "Avg TRAIN ratings per user")],
             "Y": [A("Avg", "dashboard_segment_profiles", "avg_positive_rate", "Avg positive rate")],
             "Size": [A("Sum", "dashboard_segment_profiles", "user_count", "Users")]},
      title_text="Activity vs positive rate")
textbox(p, "p2_segment_notes", 880, 110, 380, 290, [
    "What each segment means",
    "Replace this text with the business meaning of each segment, based on the cluster profile",
    "table below (KNIME node 14 Profile Clusters). Example: Selective Critics rate many movies",
    "but give fewer 4+ ratings, so broad promotion works worse for them.",
])
p.add("p2_segment_profile", "tableEx", 20, 420, 620, 280,
      roles={"Values": [C("dashboard_segment_profiles", "segment_name", "Segment"),
                        A("Sum", "dashboard_segment_profiles", "user_count", "Users"),
                        A("Avg", "dashboard_segment_profiles", "avg_user_ratings", "Ratings / user"),
                        A("Avg", "dashboard_segment_profiles", "avg_rating", "Avg rating"),
                        A("Avg", "dashboard_segment_profiles", "avg_positive_rate", "Positive rate"),
                        A("Avg", "dashboard_segment_profiles", "avg_rating_stddev", "Rating stddev"),
                        A("Avg", "dashboard_segment_profiles", "avg_active_days", "Active days")]},
      title_text="Segment profile (TRAIN)")
p.add("p2_genre_heatmap", "pivotTable", 660, 420, 600, 280,
      roles={"Rows": [C("dashboard_segment_profiles", "segment_name", "Segment")],
             "Columns": [C("Genres", "genre", "Genre")],
             "Values": [A("Avg", "dashboard_segment_genres", "avg_genre_positive_rate", "Positive rate")]},
      title_text="Positive rate by segment x genre")
pages.append(p)

# Page 3 - Positive Engagement Model
p = Page("p3_engagement_model", "3. Positive Engagement Model")
slicer(p, "p3_slicer_version", 20, 20, 250, 90, C("Model Versions", "model_version"), "Model version",
       single=True, sync="ModelVersion")
for i, (m, label) in enumerate([("Test Accuracy", "Accuracy (TEST)"), ("Test Precision", "Precision"),
                                ("Test Recall", "Recall"), ("Test F1", "F1"), ("Test AUC", "ROC-AUC"),
                                ("Baseline Accuracy", "Majority baseline")]):
    card(p, f"p3_card_{i}", 290 + 165 * i, 20, 155, 90, m, label)
p.add("p3_confusion_matrix", "pivotTable", 20, 130, 500, 260,
      roles={"Rows": [C("dashboard_confusion_matrix", "actual_liked", "Actual liked")],
             "Columns": [C("dashboard_confusion_matrix", "predicted_liked", "Predicted liked")],
             "Values": [M("Prediction Rows (TEST)", "Rows")]},
      title_text="Confusion matrix (TEST)")
p.add("p3_coefficients", "clusteredBarChart", 540, 130, 720, 570,
      roles={"Category": [C("dashboard_model_metrics", "metric_name", "Feature")],
             "Y": [M("Coefficient")]},
      title_text="Logistic Regression coefficients (z-scored features)",
      sort=(M("Coefficient"), "Descending"))
textbox(p, "p3_model_notes", 20, 410, 500, 290, [
    "How to read this page",
    "Target: rating >= 4.0 (liked). Features use TRAIN history only; TRAIN rows use leave-one-out.",
    "Compare Accuracy with the majority baseline: the model is only useful if it beats it.",
    "Coefficients show association after controlling for the other features, not causation.",
    "ROC curve: paste the screenshot from KNIME here (Insert > Image).",
])
pages.append(p)

# Page 4 - Content Opportunity Matrix
p = Page("p4_content_opportunity", "4. Content Opportunity Matrix")
slicer(p, "p4_slicer_version", 20, 20, 240, 70, C("Model Versions", "model_version"), "Model version",
       single=True, sync="ModelVersion")
slicer(p, "p4_slicer_segment", 270, 20, 240, 70, C("dashboard_segment_profiles", "segment_name"), "Segment")
slicer(p, "p4_slicer_genre", 520, 20, 240, 70, C("Genres", "genre"), "Genre")
slicer(p, "p4_slicer_support", 770, 20, 240, 70, C("Min Support", "Min Support"), "Minimum TEST support",
       single=True)
p.add("p4_opportunity_matrix", "scatterChart", 20, 110, 800, 590,
      roles={"Category": [C("dashboard_content_opportunities", "title", "Movie")],
             "X": [M("Train Popularity", "TRAIN popularity (ratings)")],
             "Y": [M("Predicted Like (Supported)", "Predicted like probability")],
             "Size": [M("Test Support", "TEST support")],
             "Tooltips": [M("Actual Positive Rate"), M("Calibration Gap")]},
      title_text="Content Opportunity Matrix: low popularity + high predicted like = hidden opportunity",
      objects={"categoryAxis": [{"properties": {"axisScale": lit("log")}}]})
p.add("p4_candidates", "tableEx", 840, 110, 420, 590,
      roles={"Values": [C("dashboard_content_opportunities", "segment_name", "Segment"),
                        C("dashboard_content_opportunities", "title", "Movie"),
                        M("Predicted Like (Supported)", "Predicted like"),
                        M("Test Support (Supported)", "TEST support"),
                        M("Train Popularity (Supported)", "TRAIN popularity")]},
      title_text="Candidates (above minimum support)",
      sort=(M("Predicted Like (Supported)"), "Descending"))
pages.append(p)

# Page 5 - Model Governance
p = Page("p5_model_governance", "5. Model Governance")
p.add("p5_splits", "tableEx", 20, 20, 620, 200,
      roles={"Values": [C("dashboard_split_summary", "data_split", "Split"),
                        A("Sum", "dashboard_split_summary", "rows_in_split", "Rows"),
                        C("dashboard_split_summary", "period_start", "From"),
                        C("dashboard_split_summary", "period_end", "To")]},
      title_text="Chronological split (70 / 15 / 15)")
p.add("p5_versions", "tableEx", 660, 20, 600, 200,
      roles={"Values": [C("dashboard_model_metrics", "model_name", "Model"),
                        C("dashboard_model_metrics", "model_version", "Version"),
                        A("Max", "dashboard_model_metrics", "run_timestamp", "Last run")]},
      title_text="Model versions written back to MySQL")
p.add("p5_silhouette", "lineChart", 20, 240, 620, 300,
      roles={"Category": [C("dashboard_model_metrics", "metric_name", "K")], "Y": [M("Silhouette")]},
      title_text="K-Means silhouette by K")
for i, (m, label) in enumerate([("Test Accuracy", "Logistic accuracy (TEST)"),
                                ("Baseline Accuracy", "Majority baseline"), ("Lift vs Baseline", "Lift"),
                                ("TEST Rows", "TEST rows scored")]):
    card(p, f"p5_card_{i}", 660 + 150 * i, 240, 140, 120, m, label)
textbox(p, "p5_limitations", 20, 560, 1240, 140, [
    "Known limitations",
    "MovieLens 10M (2009) has no views, exposure, revenue or demographics; positive engagement = rating >= 4.0.",
    "Warm-start only: users and movies without TRAIN history are excluded (see 06 cold-start query).",
    "Recommendations are candidates for an A/B test, not proven uplift.",
])
pages.append(p)

# --------------------------------------------------------------------------- write files
model_dir = HERE / f"{NAME}.SemanticModel"
report_dir = HERE / f"{NAME}.Report"
for d in (model_dir, report_dir):
    if d.exists():
        shutil.rmtree(d)

write_json(HERE / f"{NAME}.pbip", {
    "$schema": f"{SCHEMA}/pbip/pbipProperties/1.0.0/schema.json",
    "version": "1.0",
    "artifacts": [{"report": {"path": f"{NAME}.Report"}}],
    "settings": {"enableAutoRecovery": True},
})
write_json(model_dir / "definition.pbism", {
    "$schema": f"{SCHEMA}/item/semanticModel/definitionProperties/1.0.0/schema.json",
    "version": "4.2",
    "settings": {},
})
write_json(model_dir / "model.bim", model_bim)
write_json(report_dir / "definition.pbir", {
    "$schema": f"{SCHEMA}/item/report/definitionProperties/2.0.0/schema.json",
    "version": "4.0",
    "datasetReference": {"byPath": {"path": f"../{NAME}.SemanticModel"}},
})
defn = report_dir / "definition"
write_json(defn / "version.json", {
    "$schema": f"{SCHEMA}/item/report/definition/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
write_json(defn / "report.json", {
    "$schema": f"{SCHEMA}/item/report/definition/report/1.2.0/schema.json",
    "themeCollection": {"baseTheme": {"name": "CY24SU10", "reportVersionAtImport": "5.61", "type": "SharedResources"}},
    "layoutOptimization": "None",
})
write_json(defn / "pages" / "pages.json", {
    "$schema": f"{SCHEMA}/item/report/definition/pagesMetadata/1.0.0/schema.json",
    "pageOrder": [pg.name for pg in pages],
    "activePageName": pages[0].name,
})
for pg in pages:
    write_json(defn / "pages" / pg.name / "page.json", {
        "$schema": S_PAGE, "name": pg.name, "displayName": pg.display,
        "displayOption": "FitToPage", "height": 720, "width": 1280,
    })
    for v in pg.visuals:
        write_json(defn / "pages" / pg.name / "visuals" / v["name"] / "visual.json", v)

print(f"{len(tables)} tables, {sum(len(t.get('measures', [])) for t in tables)} measures, "
      f"{len(relationships)} relationships, {len(pages)} pages, {sum(len(p.visuals) for p in pages)} visuals")
