from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path(r"C:\Users\doubl\Documents\movielens-content-strategy")
TMP = ROOT / "tmp" / "report"
FIG = TMP / "figures_vi"
OUT = ROOT / "output"
FIG.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
OUTPUT = OUT / "Bao_cao_MovieLens_Tieng_Viet.docx"

sys.path.insert(0, str(TMP))
import build_final_report as existing_figures  # noqa: E402


BLACK = "000000"
INK = "20252B"
MUTED = "66707A"
TEAL = "0F5C5E"
PALE = "EDF6F5"
PALE_2 = "F6F8F8"
BORDER = "D9DEDF"
GREEN = "2E7D5B"
ORANGE = "B8652A"


def pil_font(size: int, bold: bool = False):
    candidates = [
        Path(r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def draw_centered(draw, box, text, font, fill, spacing=6):
    x0, y0, x1, y1 = box
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    draw.multiline_text(
        ((x0 + x1 - width) / 2, (y0 + y1 - height) / 2),
        text,
        font=font,
        fill=fill,
        spacing=spacing,
        align="center",
    )


def make_pipeline_figure(path: Path):
    image = Image.new("RGB", (1800, 760), "white")
    draw = ImageDraw.Draw(image)
    f_title = pil_font(38, True)
    f_head = pil_font(24, True)
    f_body = pil_font(18)
    draw.text((70, 40), "Từ dữ liệu thô đến quyết định nội dung", font=f_title, fill="#111111")
    cards = [
        ("MovieLens 10M", "ratings\nmovies\ntags"),
        ("MySQL", "nạp dữ liệu\nkiểm tra chất lượng\nchia theo thời gian"),
        ("KNIME", "tạo đặc trưng\nK Means\nLogistic Regression"),
        ("MySQL", "lưu phân khúc\nxác suất dự đoán\nchỉ số mô hình"),
        ("Power BI", "dashboard\nbộ lọc\ncơ hội nội dung"),
        ("Quyết định", "quảng bá\nduy trì\nthử nghiệm"),
    ]
    colors = ["#F2F4F4", "#E8F3F2", "#EAF4EE", "#E8F3F2", "#F7F2EA", "#F1EDF5"]
    x, y, w, h = 55, 205, 250, 285
    for index, ((title, body), color) in enumerate(zip(cards, colors)):
        draw.rounded_rectangle((x, y, x + w, y + h), radius=22, fill=color, outline="#98A2A6", width=3)
        draw_centered(draw, (x + 12, y + 28, x + w - 12, y + 100), title, f_head, "#172126")
        draw_centered(draw, (x + 18, y + 105, x + w - 18, y + h - 22), body, f_body, "#3B464C")
        if index < len(cards) - 1:
            ax0, ax1, ay = x + w + 10, x + w + 48, y + h // 2
            draw.line((ax0, ay, ax1, ay), fill="#0F5C5E", width=8)
            draw.polygon([(ax1, ay), (ax1 - 17, ay - 12), (ax1 - 17, ay + 12)], fill="#0F5C5E")
        x += 295
    draw.text((70, 575), "Nguyên tắc kiểm soát", font=f_head, fill="#172126")
    controls = ["SQL chạy lại được", "TRAIN chỉ dùng quá khứ", "không dùng ID làm đặc trưng", "ghi phiên bản mô hình", "lọc theo độ tin cậy"]
    x = 70
    for text in controls:
        width = draw.textbbox((0, 0), text, font=f_body)[2] + 42
        draw.rounded_rectangle((x, 630, x + width, 686), radius=13, fill="#F5F7F7", outline="#C7CFD1", width=2)
        draw.text((x + 21, 646), text, font=f_body, fill="#3B464C")
        x += width + 24
    image.save(path, dpi=(220, 220))


def make_ml_explainer(path: Path):
    image = Image.new("RGB", (1800, 950), "white")
    draw = ImageDraw.Draw(image)
    f_title = pil_font(38, True)
    f_head = pil_font(26, True)
    f_body = pil_font(19)
    draw.text((70, 40), "Hai mô hình giải quyết hai câu hỏi khác nhau", font=f_title, fill="#111111")
    panels = [
        (70, 155, 850, 820, "K Means", "Không cần nhãn có sẵn", [
            "1  Biến mỗi người dùng thành một hồ sơ số",
            "2  Chọn K tâm nhóm ban đầu",
            "3  Gán mỗi người vào tâm gần nhất",
            "4  Tính lại tâm và lặp đến khi ổn định",
            "Đầu ra  Nhóm khán giả có hành vi tương tự",
        ], "#EAF4EE"),
        (950, 155, 1730, 820, "Logistic Regression", "Cần nhãn thích hoặc không thích", [
            "1  Đọc các đặc trưng lịch sử",
            "2  Nhân mỗi đặc trưng với một trọng số",
            "3  Đổi tổng điểm thành xác suất từ 0 đến 1",
            "4  Dùng ngưỡng 0.5 để phân loại",
            "Đầu ra  Xác suất rating từ 4 sao trở lên",
        ], "#E8F3F2"),
    ]
    for x0, y0, x1, y1, title, subtitle, steps, color in panels:
        draw.rounded_rectangle((x0, y0, x1, y1), radius=28, fill=color, outline="#AAB4B6", width=3)
        draw.text((x0 + 40, y0 + 35), title, font=f_head, fill="#172126")
        draw.text((x0 + 40, y0 + 85), subtitle, font=f_body, fill="#58636A")
        y = y0 + 165
        for i, step in enumerate(steps):
            is_last = i == len(steps) - 1
            draw.rounded_rectangle((x0 + 40, y, x1 - 40, y + 82), radius=15, fill="#FFFFFF", outline="#CED5D7", width=2)
            draw.text((x0 + 63, y + 26), step, font=f_body, fill="#172126" if is_last else "#3B464C")
            y += 98
    draw.text((70, 875), "Điểm chung  mô hình học từ quá khứ và phải được kiểm tra trên dữ liệu xảy ra sau đó", font=f_body, fill="#58636A")
    image.save(path, dpi=(220, 220))


def make_rating_figure(path: Path):
    labels = ["0,5", "1,0", "1,5", "2,0", "2,5", "3,0", "3,5", "4,0", "4,5", "5,0"]
    values = [94988, 384180, 118278, 790306, 370178, 2356676, 880516, 2875850, 585022, 1544817]
    image = Image.new("RGB", (1400, 760), "white")
    draw = ImageDraw.Draw(image)
    title = pil_font(38, True)
    body = pil_font(19)
    bold = pil_font(20, True)
    draw.text((70, 35), "Phân bố điểm rating", font=title, fill="#111111")
    left, top, right, bottom = 105, 135, 1330, 650
    draw.line((left, bottom, right, bottom), fill="#596268", width=3)
    draw.line((left, top, left, bottom), fill="#596268", width=3)
    max_value = max(values)
    slot = (right - left) / len(values)
    bar_width = slot * 0.62
    for index, (label, value) in enumerate(zip(labels, values)):
        x0 = left + index * slot + (slot - bar_width) / 2
        x1 = x0 + bar_width
        y0 = bottom - (value / max_value) * (bottom - top - 45)
        draw.rounded_rectangle((x0, y0, x1, bottom), radius=7, fill="#0F7475")
        draw.text((x0 + 10, bottom + 16), label, font=body, fill="#3B464C")
        value_text = f"{value / 1_000_000:.2f}M"
        width = draw.textbbox((0, 0), value_text, font=body)[2]
        draw.text((x0 + (bar_width - width) / 2, y0 - 29), value_text, font=body, fill="#3B464C")
    draw.text((610, 705), "Điểm rating", font=bold, fill="#172126")
    image.save(path, dpi=(220, 220))


def make_cluster_figure(path: Path):
    ks = [3, 4, 5, 6, 7]
    silhouettes = [0.060209, 0.068639, 0.069188, 0.064601, 0.065112]
    segments = [
        ("Diverse Explorers", 12182, "51,4 phần trăm"),
        ("Selective Critics", 10888, "50,9 phần trăm"),
        ("Mainstream Enthusiasts", 14457, "42,1 phần trăm"),
        ("Genre Specialists", 17346, "71,4 phần trăm"),
    ]
    image = Image.new("RGB", (1700, 820), "white")
    draw = ImageDraw.Draw(image)
    title = pil_font(36, True)
    head = pil_font(23, True)
    body = pil_font(18)
    draw.text((65, 35), "Lựa chọn K và bốn phân khúc khán giả", font=title, fill="#111111")
    draw.text((90, 120), "Silhouette trung bình theo K", font=head, fill="#172126")
    left, top, right, bottom = 100, 190, 770, 620
    draw.line((left, bottom, right, bottom), fill="#596268", width=3)
    draw.line((left, top, left, bottom), fill="#596268", width=3)
    ymin, ymax = 0.055, 0.072
    points = []
    for index, (k, value) in enumerate(zip(ks, silhouettes)):
        x = left + 75 + index * 125
        y = bottom - (value - ymin) / (ymax - ymin) * (bottom - top - 20)
        points.append((x, y))
        draw.ellipse((x - 10, y - 10, x + 10, y + 10), fill="#0F7475")
        draw.text((x - 7, bottom + 15), str(k), font=body, fill="#3B464C")
        draw.text((x - 34, y - 35), f"{value:.3f}", font=body, fill="#3B464C")
    draw.line(points, fill="#0F7475", width=5)
    sx, sy = points[1]
    draw.ellipse((sx - 18, sy - 18, sx + 18, sy + 18), outline="#B8652A", width=5)
    draw.text((105, 690), "K bằng 4 được chọn vì dễ diễn giải; K bằng 5 chỉ cao hơn khoảng 0,00055", font=body, fill="#58636A")
    draw.text((900, 120), "Quy mô và tỷ lệ rating tích cực", font=head, fill="#172126")
    max_users = max(item[1] for item in segments)
    colors = ["#448FA3", "#84939B", "#C97941", "#4F8D6B"]
    for index, (name, users, rate) in enumerate(segments):
        y = 190 + index * 120
        draw.text((900, y), name, font=head, fill="#172126")
        width = 420 * users / max_users
        draw.rounded_rectangle((900, y + 42, 900 + width, y + 80), radius=8, fill=colors[index])
        draw.text((900 + width + 15, y + 49), f"{users:,} người", font=body, fill="#3B464C")
        draw.text((1415, y + 16), rate, font=body, fill="#3B464C")
    image.save(path, dpi=(220, 220))


def make_model_figure(path: Path):
    metrics = [("Accuracy", 0.6926), ("Precision", 0.6058), ("Recall", 0.6994), ("F1", 0.6492), ("ROC AUC", 0.7583), ("Baseline", 0.5932)]
    matrix = [[31273, 14189], [9369, 21802]]
    image = Image.new("RGB", (1700, 820), "white")
    draw = ImageDraw.Draw(image)
    title = pil_font(36, True)
    head = pil_font(23, True)
    body = pil_font(19)
    draw.text((65, 35), "Đánh giá Logistic Regression trên TEST", font=title, fill="#111111")
    draw.text((95, 115), "Các chỉ số chính", font=head, fill="#172126")
    for index, (name, value) in enumerate(metrics):
        y = 180 + index * 82
        draw.text((105, y + 7), name, font=head, fill="#172126")
        x0, x1 = 285, 760
        draw.rounded_rectangle((x0, y, x1, y + 42), radius=10, fill="#E7ECEC")
        color = "#4F8D6B" if name != "Baseline" else "#8C989E"
        draw.rounded_rectangle((x0, y, x0 + (x1 - x0) * value, y + 42), radius=10, fill=color)
        draw.text((x1 + 18, y + 7), f"{value:.1%}", font=head, fill="#3B464C")
    draw.text((1060, 115), "Ma trận nhầm lẫn", font=head, fill="#172126")
    ox, oy, cell = 1025, 220, 230
    draw.text((ox + 80, oy - 48), "Dự đoán 0", font=body, fill="#3B464C")
    draw.text((ox + cell + 80, oy - 48), "Dự đoán 1", font=body, fill="#3B464C")
    draw.text((ox - 105, oy + 95), "Thực tế 0", font=body, fill="#3B464C")
    draw.text((ox - 105, oy + cell + 95), "Thực tế 1", font=body, fill="#3B464C")
    maximum = max(max(row) for row in matrix)
    for row in range(2):
        for col in range(2):
            value = matrix[row][col]
            shade = int(245 - 120 * value / maximum)
            fill = f"#{shade:02x}{min(250, shade + 16):02x}{min(255, shade + 32):02x}"
            x0, y0 = ox + col * cell, oy + row * cell
            draw.rectangle((x0, y0, x0 + cell, y0 + cell), fill=fill, outline="#B6C0C3", width=3)
            text_value = f"{value:,}"
            bbox = draw.textbbox((0, 0), text_value, font=head)
            draw.text((x0 + (cell - (bbox[2] - bbox[0])) / 2, y0 + 96), text_value, font=head, fill="#172126")
    draw.text((1030, 730), "76.633 dòng TEST đủ điều kiện  |  coverage 5,11 phần trăm", font=body, fill="#58636A")
    image.save(path, dpi=(220, 220))


def set_run(run, size=10.6, bold=False, italic=False, color=INK, font="Arial"):
    run.font.name = font
    rpr = run._element.get_or_add_rPr()
    rpr.rFonts.set(qn("w:ascii"), font)
    rpr.rFonts.set(qn("w:hAnsi"), font)
    rpr.rFonts.set(qn("w:eastAsia"), font)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


def set_repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    node = OxmlElement("w:tblHeader")
    node.set(qn("w:val"), "true")
    tr_pr.append(node)


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=95, start=115, bottom=95, end=115):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_borders(table):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = borders.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            borders.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), "6")
        node.set(qn("w:color"), BORDER)


def setup_document(doc: Document):
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.72)
    section.bottom_margin = Inches(0.72)
    section.left_margin = Inches(0.78)
    section.right_margin = Inches(0.78)
    section.header_distance = Inches(0.3)
    section.footer_distance = Inches(0.32)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    normal.font.size = Pt(10.6)
    normal.font.color.rgb = RGBColor.from_string(INK)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.line_spacing = 1.12
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.widow_control = True

    title = doc.styles["Title"]
    title.font.name = "Arial"
    title._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    title._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    title._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    title.font.size = Pt(24)
    title.font.bold = True
    title.font.color.rgb = RGBColor.from_string(BLACK)
    title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(10)
    ppr = title._element.get_or_add_pPr()
    pborder = ppr.find(qn("w:pBdr"))
    if pborder is not None:
        ppr.remove(pborder)

    for name, size, before, after in (
        ("Heading 1", 16.2, 7, 8),
        ("Heading 2", 12.4, 9, 5),
        ("Heading 3", 10.8, 7, 4),
    ):
        style = doc.styles[name]
        style.font.name = "Arial"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(BLACK)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True

    caption = doc.styles["Caption"]
    caption.font.name = "Arial"
    caption._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    caption._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    caption._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    caption.font.size = Pt(8.7)
    caption.font.color.rgb = RGBColor.from_string(MUTED)
    caption.font.italic = False
    caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption.paragraph_format.space_before = Pt(2)
    caption.paragraph_format.space_after = Pt(7)

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run(header.add_run("MOVIELENS 10M  |  BÁO CÁO PHÂN TÍCH"), size=8.0, bold=True, color=MUTED)
    add_page_number(section.footer.paragraphs[0])


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, text, end])
    set_run(run, size=8.0, color=MUTED)


def add_body(doc, text, lead=None, keep=False):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.keep_together = keep
    if lead:
        set_run(paragraph.add_run(lead), size=10.6, bold=True)
    set_run(paragraph.add_run(text), size=10.6)
    return paragraph


def add_bullet(doc, text, level=0):
    paragraph = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    paragraph.paragraph_format.space_after = Pt(3)
    paragraph.paragraph_format.line_spacing = 1.06
    run = paragraph.add_run(text) if not paragraph.runs else paragraph.runs[0]
    if paragraph.runs:
        paragraph.runs[0].text = text
        run = paragraph.runs[0]
    set_run(run, size=10.1)
    return paragraph


def add_number(doc, text):
    paragraph = doc.add_paragraph(style="List Number")
    paragraph.paragraph_format.space_after = Pt(3.5)
    paragraph.paragraph_format.line_spacing = 1.06
    run = paragraph.add_run(text) if not paragraph.runs else paragraph.runs[0]
    if paragraph.runs:
        paragraph.runs[0].text = text
        run = paragraph.runs[0]
    set_run(run, size=10.1)
    return paragraph


def add_table(doc, headers, rows, widths, font_size=8.8, numeric_cols=()):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_borders(table)
    header = table.rows[0]
    set_repeat_header(header)
    for i, value in enumerate(headers):
        cell = header.cells[i]
        cell.width = widths[i]
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_shading(cell, TEAL)
        set_cell_margins(cell)
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_after = Pt(0)
        set_run(paragraph.add_run(str(value)), size=font_size, bold=True, color="FFFFFF")
    for row_index, values in enumerate(rows):
        row = table.add_row()
        for i, value in enumerate(values):
            cell = row.cells[i]
            cell.width = widths[i]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell)
            if row_index % 2:
                set_cell_shading(cell, PALE)
            paragraph = cell.paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT if i in numeric_cols else WD_ALIGN_PARAGRAPH.LEFT
            paragraph.paragraph_format.space_after = Pt(0)
            paragraph.paragraph_format.line_spacing = 1.02
            set_run(paragraph.add_run(str(value)), size=font_size)
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(1)
    return table


def add_figure(doc, path: Path, caption: str, width: float):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(1)
    shape = paragraph.add_run().add_picture(str(path), width=Inches(width))
    shape._inline.docPr.set("descr", caption)
    shape._inline.docPr.set("title", caption)
    doc.add_paragraph(caption, style="Caption")


def page(doc, title):
    doc.add_page_break()
    doc.add_heading(title, level=1)


def add_reference(doc, number, text):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.left_indent = Cm(0.65)
    paragraph.paragraph_format.first_line_indent = Cm(-0.65)
    paragraph.paragraph_format.space_after = Pt(4)
    set_run(paragraph.add_run(f"[{number}] {text}"), size=9.0)


def build():
    existing = existing_figures.make_figures()
    pipeline = FIG / "pipeline_tieng_viet.png"
    ml_explainer = FIG / "hai_mo_hinh.png"
    rating_figure = FIG / "phan_bo_rating.png"
    cluster_figure = FIG / "phan_khuc_kmeans.png"
    model_figure = FIG / "danh_gia_logistic.png"
    make_pipeline_figure(pipeline)
    make_ml_explainer(ml_explainer)
    make_rating_figure(rating_figure)
    make_cluster_figure(cluster_figure)
    make_model_figure(model_figure)

    doc = Document()
    setup_document(doc)

    title = doc.add_paragraph(style="Title")
    title.add_run("Báo cáo phân tích dữ liệu và Machine Learning MovieLens 10M")
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.space_after = Pt(20)
    set_run(subtitle.add_run("Từ dữ liệu đánh giá phim đến chiến lược nội dung theo nhóm khán giả"), size=13.5, bold=True, color=TEAL)
    add_table(doc, ["Thông tin", "Nội dung"], [
        ("Bộ dữ liệu", "MovieLens 10M của GroupLens Research"),
        ("Quy mô", "10.000.054 lượt đánh giá  |  10.681 phim  |  69.878 người dùng có rating"),
        ("Công cụ", "MySQL 8.0  |  KNIME Analytics Platform  |  Power BI"),
        ("Mô hình", "K Means để phân khúc khán giả  |  Logistic Regression để dự đoán khả năng thích phim"),
        ("Ngày hoàn thiện", "25 tháng 10 năm 2026"),
    ], [Cm(4.0), Cm(12.1)], font_size=9.3)
    doc.add_heading("Tóm tắt dành cho người mới", level=2)
    add_body(doc, "Dự án này trả lời một câu hỏi thực tế: nền tảng phim nên giới thiệu nội dung nào cho từng kiểu khán giả. Dữ liệu không chứa thông tin cá nhân hay lịch sử xem; dữ liệu chỉ cho biết ai đã chấm phim nào, chấm bao nhiêu sao và vào thời điểm nào. Vì vậy, kết quả được hiểu là mức độ phù hợp về sở thích rating, không phải xác suất xem phim, mua gói hay tạo doanh thu.")
    add_body(doc, "Quy trình giữ nguyên toàn bộ 10.000.054 dòng rating hợp lệ, chuẩn hóa cấu trúc dữ liệu, chia quá khứ và tương lai theo thời gian, tạo đặc trưng chỉ từ phần quá khứ rồi áp dụng hai mô hình dễ giải thích. K Means tạo bốn nhóm hành vi; Logistic Regression ước lượng xác suất một rating đạt từ 4 sao trở lên. Trên 76.633 dòng TEST đủ điều kiện, mô hình đạt Accuracy 69,26 phần trăm và ROC AUC 75,83 phần trăm. Phạm vi bao phủ chỉ 5,11 phần trăm của TEST nên kết quả phù hợp nhất cho người dùng và phim đã có lịch sử trong TRAIN.")
    keywords = doc.add_paragraph()
    set_run(keywords.add_run("Từ khóa  "), size=9.2, bold=True)
    set_run(keywords.add_run("MovieLens, làm sạch dữ liệu, phân khúc khán giả, K Means, Logistic Regression, MySQL, KNIME, Power BI"), size=9.2, italic=True, color=MUTED)

    page(doc, "1 Bài toán và kết luận chính")
    add_body(doc, "Nếu chỉ quảng bá phim theo bảng xếp hạng phổ biến, mọi người dùng sẽ thấy gần như cùng một danh sách. Cách làm đó bỏ qua khác biệt về mức độ hoạt động, thể loại yêu thích và xu hướng chấm điểm. Dự án xây dựng một hệ thống hỗ trợ quyết định để Content Programming and Personalization Manager có thể lựa chọn phim cần quảng bá, duy trì, giảm ưu tiên hoặc đưa vào thử nghiệm.")
    add_body(doc, "Positive engagement được định nghĩa là rating lớn hơn hoặc bằng 4,0. Đây là một quy ước đo sở thích. Một dòng có rating 4 hoặc 5 được gắn nhãn thích; các mức còn lại được gắn nhãn không thích. Cách định nghĩa đơn giản này cho phép xây dựng bài toán phân loại nhị phân và giải thích kết quả bằng xác suất.")
    doc.add_heading("Các câu hỏi ra quyết định", level=2)
    add_table(doc, ["Câu hỏi", "Dữ liệu trả lời", "Kết quả sử dụng"], [
        ("Người dùng khác nhau như thế nào", "Mức độ hoạt động, điểm trung bình, tỷ lệ rating tích cực và sở thích thể loại", "Hồ sơ bốn phân khúc"),
        ("Có thể gom người dùng thành nhóm nào", "Khoảng cách giữa các hồ sơ hành vi đã chuẩn hóa", "K Means và chỉ số silhouette"),
        ("Một người có khả năng thích một phim hay không", "Lịch sử người dùng, lịch sử phim, phân khúc và thể loại", "Xác suất từ Logistic Regression"),
        ("Nội dung nào nên được thử nghiệm quảng bá", "Xác suất dự đoán, tỷ lệ thực tế, độ phổ biến và số quan sát", "Content Opportunity Matrix"),
    ], [Cm(5.2), Cm(6.3), Cm(4.6)], font_size=8.6)
    add_body(doc, "Kết luận quan trọng nhất là mô hình có ích như một bộ lọc ưu tiên thử nghiệm, không phải cơ chế tự động quyết định cho toàn bộ nền tảng. Khả năng bao phủ còn thấp và dữ liệu đã cũ, nên mọi đề xuất quảng bá cần được kiểm chứng bằng A B test với dữ liệu xem thực tế.")

    page(doc, "2 Bộ dữ liệu MovieLens 10M")
    add_body(doc, "MovieLens 10M là bộ dữ liệu nghiên cứu công khai do GroupLens phát hành vào tháng 1 năm 2009. Người dùng được ẩn danh. Bộ dữ liệu không có tên, email, tuổi, giới tính hay vị trí địa lý. Mỗi người dùng xuất hiện trong bảng ratings có ít nhất 20 lượt đánh giá, vì vậy mẫu nghiêng về người dùng hoạt động tương đối tích cực.")
    add_table(doc, ["Thành phần", "Số dòng", "Trường chính", "Ý nghĩa"], [
        ("ratings", "10.000.054", "user id, movie id, rating, timestamp", "Sự kiện một người dùng chấm một phim từ 0,5 đến 5 sao"),
        ("movies", "10.681", "movie id, title, genres", "Danh mục phim và danh sách thể loại phân tách bằng dấu gạch đứng"),
        ("tags", "95.580", "user id, movie id, tag, timestamp", "Từ khóa tự do do người dùng gắn cho phim"),
        ("movie genres", "21.564", "movie id, genre", "Bảng đã chuẩn hóa để một phim có thể liên kết với nhiều thể loại"),
        ("rating users", "69.878", "user id", "Số người dùng thực sự có ít nhất một rating"),
    ], [Cm(2.3), Cm(2.0), Cm(5.2), Cm(6.6)], font_size=8.4, numeric_cols=(1,))
    add_body(doc, "Tài liệu gốc ghi 71.567 người dùng vì con số đó bao gồm cả người dùng chỉ xuất hiện trong tệp tags. Báo cáo sử dụng 69.878 khi nói về người dùng rating. Các timestamp trải từ ngày 9 tháng 1 năm 1995 đến ngày 5 tháng 1 năm 2009.")
    add_figure(doc, rating_figure, "Hình 1  Phân bố 10.000.054 lượt đánh giá trong MovieLens 10M", 5.8)
    add_body(doc, "Điểm 4,0 xuất hiện nhiều nhất với 2.875.850 lượt. Điểm trung bình toàn bộ dữ liệu là 3,512 và 50,06 phần trăm rating đạt từ 4,0 trở lên. Tỷ lệ hai lớp khá cân bằng ở toàn bộ dữ liệu, nhưng tỷ lệ này thay đổi sau khi chỉ giữ các dòng đủ lịch sử TRAIN.")

    page(doc, "3 Hiểu đúng về làm sạch dữ liệu")
    add_body(doc, "Làm sạch dữ liệu không đồng nghĩa với xóa thật nhiều dòng. Mục tiêu là bảo đảm mỗi trường có ý nghĩa rõ ràng, mỗi khóa liên kết đúng, giá trị nằm trong phạm vi hợp lệ và mọi biến dùng cho mô hình được tạo theo một quy trình có thể chạy lại. Trong dự án này, dữ liệu gốc có chất lượng cấu trúc tốt nên không cần xóa hay điền thay bất kỳ dòng rating nào.")
    add_table(doc, ["Kiểm tra", "Trước xử lý", "Sau xử lý", "Cách xử lý và ý nghĩa"], [
        ("Tổng số rating", "10.000.054", "10.000.054", "Giữ nguyên vì mọi dòng đều hợp lệ"),
        ("Rating hoặc tag thiếu phim tham chiếu", "0", "0", "Khóa liên kết không có bản ghi mồ côi"),
        ("Rating hoặc timestamp không hợp lệ", "0", "0", "Giá trị nằm trong thang điểm và thời gian cho phép"),
        ("Cặp người dùng và phim bị trùng", "0", "0", "Không cần loại bỏ bản ghi trùng"),
        ("Người dùng dưới 20 rating", "0", "0", "Phù hợp điều kiện tối thiểu của dataset"),
        ("Phim có ít nhất một rating", "10.677 trên 10.681", "10.677 trên 10.681", "Giữ bốn phim chưa có rating như bản ghi danh mục hợp lệ"),
    ], [Cm(4.0), Cm(2.5), Cm(2.5), Cm(7.1)], font_size=8.2, numeric_cols=(1, 2))
    doc.add_heading("Các bước làm sạch và chuẩn hóa", level=2)
    steps = [
        "Nạp ba tệp gốc vào MySQL với kiểu dữ liệu rõ ràng cho ID, rating và timestamp.",
        "Thiết lập khóa chính và index để ngăn lỗi định danh và tăng tốc truy vấn trên 10 triệu dòng.",
        "Kiểm tra giá trị thiếu, bản ghi mồ côi, rating ngoài thang 0,5 đến 5, timestamp không hợp lệ và cặp user movie trùng.",
        "Tách chuỗi genres thành bảng movie genres, giúp một phim có nhiều thể loại mà vẫn truy vấn đúng.",
        "Sắp xếp theo thời gian và chia TRAIN VALID TEST theo tỷ lệ 70 15 15.",
        "Tạo thống kê người dùng, phim và thể loại chỉ từ TRAIN; với dòng TRAIN dùng leave one out để rating hiện tại không tự giải thích chính nó.",
        "Trong KNIME, xử lý giá trị thiếu của đặc trưng, hạn chế ảnh hưởng của ngoại lệ và chuẩn hóa thang đo trước khi huấn luyện.",
        "Ghi phân khúc, dự đoán, metric, phiên bản mô hình và thời gian chạy trở lại MySQL.",
    ]
    for item in steps:
        add_number(doc, item)

    page(doc, "4 Pipeline dữ liệu từ đầu đến cuối")
    add_figure(doc, pipeline, "Hình 2  Kiến trúc dữ liệu và luồng xử lý của dự án", 7.1)
    add_body(doc, "MySQL là nơi lưu trữ có kiểm soát cho dữ liệu gốc, bảng đặc trưng và kết quả mô hình. KNIME đọc trực tiếp từ MySQL, thực hiện tiền xử lý và machine learning, sau đó ghi kết quả trở lại các bảng user segments, rating predictions và model metrics. Power BI chỉ đọc các view đã tổng hợp thay vì tải toàn bộ 10 triệu dòng, giúp dashboard nhẹ và giữ được nguồn gốc dữ liệu.")
    add_table(doc, ["Tầng", "Ví dụ", "Vai trò"], [
        ("Dữ liệu gốc", "ratings, movies, tags", "Bảo toàn dữ liệu được phát hành"),
        ("Dữ liệu chuẩn hóa", "movie genres, rating split", "Tách thể loại và định nghĩa các khoảng thời gian"),
        ("Đặc trưng", "train user stats, train movie stats, ml rating features", "Biến lịch sử thành các cột số mà mô hình có thể sử dụng"),
        ("Kết quả mô hình", "user segments, rating predictions, model metrics", "Lưu nhóm, xác suất, nhãn và chỉ số đánh giá"),
        ("Báo cáo", "dashboard views", "Cung cấp dữ liệu nhỏ gọn cho Power BI"),
    ], [Cm(3.0), Cm(6.2), Cm(7.0)], font_size=8.6)
    add_body(doc, "Điểm mạnh của kiến trúc này là khả năng truy vết. Một con số trên dashboard có thể lần ngược về view MySQL, bảng kết quả KNIME và cuối cùng là dữ liệu gốc. Model version ngăn việc trộn kết quả từ nhiều lần chạy khác nhau.")

    page(doc, "5 Vì sao phải chia TRAIN VALID và TEST")
    add_body(doc, "Machine learning cần được kiểm tra bằng dữ liệu mà mô hình chưa nhìn thấy. Có thể hình dung TRAIN là bộ bài tập dùng để học, VALID là bài thi thử để điều chỉnh và TEST là bài thi cuối cùng. Nếu đưa đáp án TEST vào quá trình học, kết quả sẽ đẹp giả tạo và không phản ánh khả năng dự đoán tương lai.")
    add_table(doc, ["Phần", "Số dòng", "Khoảng thời gian", "Mục đích"], [
        ("TRAIN", "7.000.042", "09 01 1995 đến 02 04 2005", "Tạo lịch sử và huấn luyện mô hình"),
        ("VALID", "1.500.006", "02 04 2005 đến 28 12 2006", "Kiểm tra lựa chọn mô hình và ngưỡng"),
        ("TEST", "1.500.006", "28 12 2006 đến 05 01 2009", "Đánh giá cuối cùng trên giai đoạn tương lai"),
    ], [Cm(2.4), Cm(2.8), Cm(5.4), Cm(5.8)], font_size=8.8, numeric_cols=(1,))
    doc.add_heading("Bốn biện pháp chống rò rỉ dữ liệu", level=2)
    add_bullet(doc, "Chia theo thời gian thay vì xáo trộn ngẫu nhiên để mô phỏng việc dự đoán tương lai từ quá khứ.")
    add_bullet(doc, "Mọi thống kê lịch sử của người dùng, phim và thể loại chỉ được tính từ TRAIN.")
    add_bullet(doc, "Đối với dòng TRAIN, leave one out loại rating hiện tại khỏi giá trị trung bình dùng làm đặc trưng.")
    add_bullet(doc, "Quy tắc điền thiếu và chuẩn hóa được học trên TRAIN rồi giữ nguyên khi áp dụng cho VALID và TEST.")
    add_body(doc, "user id và movie id chỉ là mã định danh nên không được dùng như các con số có thứ tự. Nếu cho mô hình học trực tiếp rằng user 100 lớn hơn user 20, mô hình sẽ tạo ra quan hệ giả không có ý nghĩa kinh doanh.")
    doc.add_heading("Warm start và phạm vi bao phủ", level=2)
    add_body(doc, "Một dòng chỉ đủ điều kiện dự đoán khi cả người dùng và phim đã có lịch sử trong TRAIN. Đây gọi là warm start. Quy tắc này bảo vệ ý nghĩa của đặc trưng nhưng làm số dòng TEST đủ điều kiện giảm còn 76.633 trên 1.500.006, tương đương 5,11 phần trăm. Với người dùng hoặc phim mới hoàn toàn, hệ thống cần fallback như danh sách phổ biến, biên tập viên hoặc mô hình cold start khác.")

    page(doc, "6 Machine Learning cho người mới bắt đầu")
    add_body(doc, "Machine learning là cách để máy tính học một quy luật từ nhiều ví dụ thay vì con người viết sẵn từng điều kiện. Mỗi hàng dữ liệu là một ví dụ. Các cột mô tả ví dụ được gọi là đặc trưng. Kết quả cần dự đoán được gọi là mục tiêu hoặc nhãn. Mô hình là công thức được điều chỉnh trong quá trình học để biến đặc trưng thành đầu ra.")
    add_table(doc, ["Khái niệm", "Trong dự án", "Cách hiểu đơn giản"], [
        ("Quan sát", "Một người dùng chấm một phim tại một thời điểm", "Một ví dụ để mô hình học hoặc kiểm tra"),
        ("Đặc trưng", "Điểm trung bình quá khứ, mức độ hoạt động, lịch sử phim, phân khúc, thể loại", "Các tín hiệu có trước thời điểm dự đoán"),
        ("Nhãn", "1 nếu rating từ 4 sao trở lên, ngược lại là 0", "Đáp án đúng của bài toán phân loại"),
        ("Mô hình", "K Means và Logistic Regression", "Quy tắc được học từ dữ liệu"),
        ("Dự đoán", "Xác suất thích phim và nhãn thích không thích", "Đầu ra dùng để xếp hạng hoặc lọc"),
    ], [Cm(3.0), Cm(7.5), Cm(5.7)], font_size=8.6)
    add_figure(doc, ml_explainer, "Hình 3  Vai trò khác nhau của K Means và Logistic Regression", 7.1)
    add_body(doc, "Hai mô hình được chọn vì dễ giải thích, chạy tốt trong KNIME, phù hợp với dữ liệu dạng bảng và cho phép kiểm tra rõ từng bước. Một mô hình phức tạp hơn không tự động tốt hơn nếu khó truy vết, không cải thiện trên TEST hoặc không phù hợp với mức độ bao phủ hiện tại.")

    page(doc, "7 K Means dùng để phân khúc khán giả")
    add_body(doc, "K Means là mô hình học không giám sát. Không có sẵn cột cho biết ai thuộc nhóm nào. Mô hình nhìn vào hồ sơ số của từng người dùng, đo khoảng cách và tìm các cụm sao cho người trong cùng cụm giống nhau hơn người ở cụm khác. Trước khi đo khoảng cách, các cột phải được chuẩn hóa; nếu không, cột có giá trị số lớn sẽ lấn át các cột còn lại.")
    add_body(doc, "Đặc trưng phân khúc gồm mức độ hoạt động, tuổi đời lịch sử rating, điểm trung bình, tỷ lệ rating tích cực và mức yêu thích tương đối theo thể loại. Mức yêu thích tương đối so sánh điểm của một thể loại với mức chấm điểm chung của chính người dùng, giúp phân biệt một người vốn chấm cao với một người thực sự thiên về thể loại đó.")
    add_table(doc, ["K", "Silhouette trung bình", "Diễn giải"], [
        ("3", "0,060209", "Ít nhóm hơn nhưng độ tách thấp"),
        ("4", "0,068639", "Được chọn vì cân bằng giữa khả năng giải thích và độ tách"),
        ("5", "0,069188", "Chỉ cao hơn K bằng 4 khoảng 0,00055"),
        ("6", "0,064601", "Kém hơn lựa chọn 4 nhóm"),
        ("7", "0,065112", "Kém hơn lựa chọn 4 nhóm"),
    ], [Cm(2.0), Cm(4.0), Cm(10.2)], font_size=8.8, numeric_cols=(0, 1))
    add_figure(doc, cluster_figure, "Hình 4  So sánh K và quy mô bốn phân khúc cuối cùng", 5.8)
    add_table(doc, ["Phân khúc", "Người dùng", "Tỷ lệ tích cực", "Cách hiểu hành vi"], [
        ("Diverse Explorers", "12.182", "51,38 phần trăm", "Thiên tương đối về thriller, action và mystery"),
        ("Selective Critics", "10.888", "50,88 phần trăm", "Hoạt động nhiều nhất và có lịch sử dài nhất"),
        ("Mainstream Enthusiasts", "14.457", "42,06 phần trăm", "Thiên tương đối về family và animation"),
        ("Genre Specialists", "17.346", "71,43 phần trăm", "Nhóm lớn nhất và có xu hướng chấm tích cực cao nhất"),
    ], [Cm(4.0), Cm(2.3), Cm(3.0), Cm(6.9)], font_size=7.9, numeric_cols=(1, 2))
    add_body(doc, "Silhouette tuyệt đối còn thấp, nghĩa là ranh giới giữa các nhóm bị chồng lấn. Do đó, tên nhóm là nhãn diễn giải hành vi, không phải phân loại con người cố định và càng không phải thông tin nhân khẩu học.")

    page(doc, "8 Logistic Regression dự đoán khả năng thích phim")
    add_body(doc, "Logistic Regression là mô hình phân loại có giám sát. Mô hình học từ các ví dụ có đáp án thích hoặc không thích. Mỗi đặc trưng nhận một trọng số. Các tín hiệu được cộng lại thành một điểm, sau đó hàm logistic chuyển điểm này thành xác suất từ 0 đến 1. Ví dụ, xác suất 0,72 được hiểu là mô hình đánh giá tín hiệu tích cực mạnh hơn mức trung bình; nó không bảo đảm 72 phần trăm người dùng sẽ xem phim.")
    doc.add_heading("Những tín hiệu mô hình sử dụng", level=2)
    add_bullet(doc, "Lịch sử người dùng như điểm trung bình, tỷ lệ rating tích cực và số rating trong TRAIN.")
    add_bullet(doc, "Lịch sử phim như điểm trung bình, tỷ lệ tích cực và mức độ phổ biến trong TRAIN.")
    add_bullet(doc, "Phân khúc K Means của người dùng và ngữ cảnh thể loại của phim.")
    add_bullet(doc, "Các biến đã xử lý thiếu và chuẩn hóa bằng tham số học từ TRAIN.")
    doc.add_heading("Vì sao chọn Logistic Regression", level=2)
    add_body(doc, "Bài toán có hai lớp rõ ràng, dữ liệu là bảng số, stakeholder cần xác suất và cần hiểu hướng tác động của đặc trưng. Logistic Regression đáp ứng cả bốn yêu cầu, có baseline minh bạch và triển khai ổn định trong KNIME. Mô hình cũng phù hợp làm mốc chuẩn trước khi thử các thuật toán phức tạp hơn.")
    add_table(doc, ["Bước", "Điều xảy ra", "Ý nghĩa"], [
        ("Huấn luyện", "Tìm bộ trọng số giúp xác suất khớp nhãn TRAIN", "Mô hình học quy luật từ quá khứ"),
        ("VALID", "Kiểm tra mô hình và ngưỡng 0,5", "Hạn chế điều chỉnh trực tiếp trên TEST"),
        ("TEST", "Áp dụng nguyên quy trình lên giai đoạn sau", "Đo khả năng tổng quát ngoài thời gian huấn luyện"),
        ("Write back", "Lưu actual, predicted, probability, split và version", "Cho phép SQL và Power BI kiểm tra lại kết quả"),
    ], [Cm(3.0), Cm(7.0), Cm(6.2)], font_size=8.6)

    page(doc, "9 Đánh giá mô hình và cách đọc chỉ số")
    add_figure(doc, model_figure, "Hình 5  Kết quả Logistic Regression trên tập TEST đủ điều kiện", 6.7)
    add_table(doc, ["Chỉ số", "Kết quả", "Giải thích cho người mới"], [
        ("Accuracy", "69,26 phần trăm", "Trong 100 dự đoán, khoảng 69 dự đoán đúng"),
        ("Majority baseline", "59,32 phần trăm", "Nếu luôn đoán lớp phổ biến nhất thì đúng khoảng 59 lần"),
        ("Precision", "60,58 phần trăm", "Trong các trường hợp mô hình dự đoán thích, khoảng 61 phần trăm thực sự thích"),
        ("Recall", "69,94 phần trăm", "Trong các trường hợp thực sự thích, mô hình tìm được khoảng 70 phần trăm"),
        ("F1", "64,92 phần trăm", "Điểm cân bằng giữa precision và recall"),
        ("ROC AUC", "75,83 phần trăm", "Khả năng xếp một trường hợp tích cực cao hơn một trường hợp tiêu cực"),
    ], [Cm(3.2), Cm(3.0), Cm(10.0)], font_size=8.5, numeric_cols=(1,))
    add_body(doc, "Confusion matrix gồm 31.273 true negative, 14.189 false positive, 9.369 false negative và 21.802 true positive. False positive là trường hợp mô hình dự đoán thích nhưng người dùng thực tế không cho rating tích cực; trong bài toán quảng bá, đây là rủi ro làm lãng phí vị trí hiển thị. False negative là nội dung người dùng có thể thích nhưng mô hình bỏ sót; đây là rủi ro mất cơ hội khám phá.")
    add_body(doc, "Accuracy cao hơn baseline 9,93 điểm phần trăm và ROC AUC cho thấy khả năng xếp hạng hữu ích. Tuy nhiên, các chỉ số chỉ mô tả 76.633 dòng TEST warm start chứ không đại diện cho toàn bộ 1.500.006 dòng TEST. Vì vậy, khi trình bày hiệu quả mô hình luôn phải đặt metric cạnh coverage 5,11 phần trăm.")

    page(doc, "10 Từ kết quả mô hình đến quyết định nội dung")
    add_body(doc, "Power BI kết hợp bốn loại bằng chứng: xác suất dự đoán, tỷ lệ rating tích cực quan sát được, độ phổ biến trong TRAIN và support trong TEST. Xác suất cao nhưng support thấp chưa đủ để hành động. Tương tự, một phim phổ biến không nhất thiết phù hợp với mọi phân khúc.")
    add_table(doc, ["Hành động đề xuất", "Bằng chứng", "Cách triển khai an toàn"], [
        ("Thử nghiệm Hotel Rwanda và My Neighbor Totoro cho Selective Critics", "Hotel Rwanda support 108, dự đoán 76,72 phần trăm, thực tế 77,78 phần trăm. My Neighbor Totoro support 58, dự đoán 74,87 phần trăm, thực tế 74,14 phần trăm.", "Đưa vào một discovery row thử nghiệm và so sánh với trải nghiệm hiện tại"),
        ("Bổ sung City of God và Oldboy vào nhóm ứng viên", "City of God support 60, dự đoán 71,66 phần trăm. Oldboy support 52, dự đoán 69,94 phần trăm.", "Giới hạn ở người dùng warm start và theo dõi theo từng phim"),
        ("Giảm ưu tiên mặc định một số phim phổ biến trong Selective Critics", "Home Alone, Star Wars Episode I, Twister và The Mask có support trên 50 nhưng tỷ lệ tích cực thực tế thấp", "Không gỡ khỏi danh mục; chỉ giảm vị trí trong trải nghiệm của phân khúc này"),
        ("Dùng fallback khi không đủ lịch sử", "Coverage TEST của classifier chỉ 5,11 phần trăm", "Dùng danh sách phổ biến hoặc biên tập cho cold start và theo dõi coverage như KPI"),
    ], [Cm(4.7), Cm(6.7), Cm(4.8)], font_size=8.0)
    doc.add_heading("Thiết kế kiểm chứng tiếp theo", level=2)
    add_body(doc, "Người dùng đủ điều kiện nên được chia ngẫu nhiên vào nhóm trải nghiệm hiện tại và nhóm nhận danh sách theo phân khúc. Hai nhóm cần có cùng vị trí hiển thị, thời gian thử nghiệm và số lượt tiếp xúc. Khi có dữ liệu hiện đại hơn, các chỉ số chính nên gồm click through, play start, completion, rating sau khi xem và doanh thu hoặc chi phí bản quyền nếu phù hợp.")
    add_body(doc, "The Incredibles nên được dùng như một trường hợp chẩn đoán. Mô hình dự đoán 74,45 phần trăm nhưng tỷ lệ thực tế chỉ 60,75 phần trăm trên 107 quan sát. Khoảng lệch này có thể phản ánh calibration chưa tốt, bối cảnh phim hoặc thay đổi theo thời gian.")

    page(doc, "11 Hạn chế và nguyên tắc sử dụng có trách nhiệm")
    limitations = [
        "Dữ liệu kết thúc vào tháng 1 năm 2009 nên không phản ánh đầy đủ catalog và hành vi streaming hiện nay.",
        "Rating chỉ xuất hiện sau khi người dùng chủ động chấm. Không rating không đồng nghĩa với không thích.",
        "Không có impression, lượt xem, watch time, click, completion, subscription, doanh thu hay chi phí bản quyền.",
        "Mọi rating user có ít nhất 20 rating nên mẫu thiên về người dùng hoạt động tích cực.",
        "Coverage của classifier thấp; kết quả không nên áp dụng trực tiếp cho cold start.",
        "Silhouette thấp cho thấy phân khúc chồng lấn; tên nhóm chỉ là mô tả hành vi tương đối.",
        "Title level support đủ mạnh chủ yếu tập trung ở Selective Critics; các phân khúc khác cần thêm dữ liệu.",
        "Mô hình chưa được kiểm tra calibration và chưa chứng minh tác động nhân quả của chiến dịch quảng bá.",
    ]
    for item in limitations:
        add_bullet(doc, item)
    doc.add_heading("Nguyên tắc sử dụng", level=2)
    add_table(doc, ["Nên làm", "Không nên làm"], [
        ("Dùng xác suất để ưu tiên danh sách thử nghiệm", "Coi xác suất là bảo đảm người dùng sẽ xem"),
        ("Luôn hiển thị metric cùng coverage và support", "Chỉ trình bày Accuracy mà bỏ qua phạm vi áp dụng"),
        ("Giữ fallback cho người dùng và phim mới", "Ép mô hình dự đoán khi không có lịch sử"),
        ("Theo dõi phiên bản, thời gian chạy và biến đổi dữ liệu", "Trộn kết quả từ nhiều model version"),
        ("Đánh giá bằng A B test trước khi mở rộng", "Suy luận trực tiếp thành doanh thu hoặc tác động nhân quả"),
    ], [Cm(8.0), Cm(8.0)], font_size=8.7)
    add_body(doc, "Hướng cải tiến hợp lý gồm thêm đặc trưng cold start, kiểm tra calibration, đánh giá theo ranking metrics, rolling temporal validation và dữ liệu exposure. Khi có dữ liệu vận hành, mục tiêu nên chuyển từ rating proxy sang hành vi phù hợp hơn với quyết định kinh doanh.")

    page(doc, "12 Kết luận")
    add_body(doc, "Dự án đã triển khai đầy đủ chuỗi Dataset đến MySQL đến KNIME đến MySQL write back đến Power BI và quyết định nội dung. Dữ liệu được kiểm tra chất lượng, giữ nguyên các tương tác hợp lệ, chuẩn hóa thể loại và chia theo thời gian trước khi tạo đặc trưng. Hai mô hình được chọn vì phù hợp với hai câu hỏi khác nhau và có thể giải thích cho stakeholder không chuyên.")
    add_body(doc, "K Means tạo bốn lăng kính hành vi để so sánh người dùng, nhưng không tạo ra các nhóm tách biệt tuyệt đối. Logistic Regression cải thiện Accuracy 9,93 điểm phần trăm so với majority baseline và đạt ROC AUC 75,83 phần trăm trên phần TEST đủ điều kiện. Giá trị thực tế của hệ thống nằm ở khả năng tạo danh sách ứng viên minh bạch cho controlled experiment, không nằm ở việc tự động hóa hoàn toàn quyết định quảng bá.")
    add_body(doc, "Quyết định phù hợp nhất ở thời điểm hiện tại là thử nghiệm có kiểm soát với nhóm Selective Critics, theo dõi kết quả trên dữ liệu xem hiện đại và giữ cơ chế fallback cho phần lớn trường hợp chưa đủ lịch sử. Cách tiếp cận này tận dụng được tín hiệu từ mô hình mà vẫn tôn trọng giới hạn của dataset và phạm vi bằng chứng.")
    doc.add_heading("Thuật ngữ ngắn", level=2)
    add_table(doc, ["Thuật ngữ", "Giải thích"], [
        ("Feature", "Cột thông tin đầu vào mà mô hình sử dụng"),
        ("Target hoặc label", "Kết quả đúng mà mô hình cần học"),
        ("Training", "Quá trình điều chỉnh mô hình bằng dữ liệu TRAIN"),
        ("Inference", "Dùng mô hình đã học để tạo dự đoán mới"),
        ("Leakage", "Vô tình để thông tin tương lai hoặc đáp án lọt vào dữ liệu học"),
        ("Coverage", "Tỷ lệ dữ liệu mà mô hình có đủ thông tin để dự đoán"),
        ("Support", "Số quan sát đứng sau một tỷ lệ hoặc một kết luận"),
        ("Warm start", "Người dùng và phim đã có lịch sử trước thời điểm dự đoán"),
    ], [Cm(4.0), Cm(12.0)], font_size=8.7)

    page(doc, "Tài liệu tham khảo")
    add_reference(doc, 1, "GroupLens Research. MovieLens 10M Dataset and README. 2009. https://grouplens.org/datasets/movielens/10m/ và https://files.grouplens.org/datasets/movielens/ml-10m-README.html")
    add_reference(doc, 2, "F. M. Harper và J. A. Konstan. The MovieLens Datasets History and Context. ACM Transactions on Interactive Intelligent Systems, 2015. doi 10.1145/2827872")
    add_reference(doc, 3, "S. P. Lloyd. Least Squares Quantization in PCM. IEEE Transactions on Information Theory, 1982. doi 10.1109/TIT.1982.1056489")
    add_reference(doc, 4, "D. W. Hosmer, S. Lemeshow và R. X. Sturdivant. Applied Logistic Regression. Wiley, 2013")
    add_reference(doc, 5, "T. Fawcett. An Introduction to ROC Analysis. Pattern Recognition Letters, 2006. doi 10.1016/j.patrec.2005.10.010")
    add_reference(doc, 6, "G. James, D. Witten, T. Hastie và R. Tibshirani. An Introduction to Statistical Learning. Springer, 2021")
    doc.add_heading("Tái tạo kết quả", level=2)
    for item in [
        "Tải MovieLens 10M từ GroupLens và kiểm tra ba tệp movies, ratings và tags.",
        "Chạy các script 01 đến 05 trong python sql scripts để tạo schema, nạp dữ liệu, kiểm tra chất lượng, chia tập và tạo feature TRAIN.",
        "Mở workflow KNIME audience segmentation, giữ K bằng 4 và ghi user segments về MySQL.",
        "Chạy bước 06 để tạo ml rating features, sau đó chạy workflow Logistic Regression và ghi predictions cùng metrics.",
        "Chạy bước 07 và refresh Power BI để kiểm tra dashboard views, model version, split dates và metric.",
    ]:
        add_number(doc, item)

    doc.core_properties.title = "Báo cáo phân tích dữ liệu và Machine Learning MovieLens 10M"
    doc.core_properties.subject = "Quy trình làm sạch dữ liệu, phân khúc khán giả và dự đoán positive engagement"
    doc.core_properties.author = "MovieLens Content Strategy Project"
    doc.core_properties.keywords = "MovieLens, data cleaning, K Means, Logistic Regression, KNIME, MySQL, Power BI"
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
