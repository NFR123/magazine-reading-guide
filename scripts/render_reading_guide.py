#!/usr/bin/env python3
"""Render structured full-issue guide data as a polished Chinese PDF."""

import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle

INK = colors.HexColor("#14231C")
MUTED = colors.HexColor("#66736D")
GREEN = colors.HexColor("#198754")
LIGHT = colors.HexColor("#EAF5EF")
RED = colors.HexColor("#E3120B")
CREAM = colors.HexColor("#F7F4EC")
LINE = colors.HexColor("#D8E0DC")


def register_fonts():
    candidates = [
        (Path(r"C:\Windows\Fonts\msyh.ttc"), Path(r"C:\Windows\Fonts\msyhbd.ttc"), 0),
        (Path("/System/Library/Fonts/PingFang.ttc"), Path("/System/Library/Fonts/PingFang.ttc"), 0),
        (Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"), Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"), 0),
    ]
    for regular, bold, subfont in candidates:
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont("GuideSans", str(regular), subfontIndex=subfont))
            pdfmetrics.registerFont(TTFont("GuideSans-Bold", str(bold), subfontIndex=subfont))
            return "GuideSans", "GuideSans-Bold"
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    return "STSong-Light", "STSong-Light"


REGULAR, BOLD = register_fonts()


class GuideDoc(BaseDocTemplate):
    def __init__(self, filename, publication, issue_date):
        super().__init__(filename, pagesize=A4, leftMargin=17*mm, rightMargin=17*mm,
                         topMargin=18*mm, bottomMargin=17*mm,
                         title=f"{publication} {issue_date} 阅读导览", author="Codex")
        self.publication = publication
        self.issue_date = issue_date
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates(PageTemplate(id="normal", frames=[frame], onPage=self.decorate))

    def decorate(self, canvas, doc):
        if doc.page == 1:
            return
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.line(17*mm, A4[1]-12*mm, A4[0]-17*mm, A4[1]-12*mm)
        canvas.setFont(REGULAR, 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(17*mm, A4[1]-9.5*mm, f"{self.publication.upper()} · {self.issue_date} · 阅读导览")
        canvas.drawRightString(A4[0]-17*mm, 9*mm, str(doc.page))
        canvas.restoreState()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cover", type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    articles = data.get("articles") or []
    if not data.get("publication") or not data.get("issue_date") or not articles:
        raise SystemExit("publication, issue_date and non-empty articles are required")
    expected = list(range(1, len(articles) + 1))
    if [int(a.get("number", 0)) for a in articles] != expected:
        raise SystemExit("article numbers must be continuous and start at 1")

    styles = {
        "kicker": ParagraphStyle("kicker", fontName=BOLD, fontSize=10, leading=14, textColor=RED),
        "cover": ParagraphStyle("cover", fontName=BOLD, fontSize=24, leading=31, textColor=INK),
        "sub": ParagraphStyle("sub", fontName=REGULAR, fontSize=10, leading=16, textColor=MUTED),
        "h1": ParagraphStyle("h1", fontName=BOLD, fontSize=19, leading=25, textColor=INK, spaceAfter=4*mm),
        "h2": ParagraphStyle("h2", fontName=BOLD, fontSize=13.5, leading=19, textColor=GREEN, spaceBefore=3*mm, spaceAfter=3*mm),
        "body": ParagraphStyle("body", fontName=REGULAR, fontSize=9, leading=14.5, textColor=INK),
        "title": ParagraphStyle("title", fontName=BOLD, fontSize=10.1, leading=14, textColor=INK),
        "summary": ParagraphStyle("summary", fontName=REGULAR, fontSize=8.5, leading=13.2, textColor=INK),
        "meta": ParagraphStyle("meta", fontName=REGULAR, fontSize=7.3, leading=10, textColor=MUTED),
        "badge": ParagraphStyle("badge", fontName=BOLD, fontSize=7.5, leading=10, textColor=colors.white, alignment=TA_CENTER),
    }

    def p(value, style):
        return Paragraph(escape(str(value)).replace("\n", "<br/>"), styles[style])

    def card(article):
        badge = Table([[p(f"{article['number']:02d}", "badge")]], colWidths=[10*mm], rowHeights=[8*mm])
        badge.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), GREEN), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                   ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        details = [article.get("difficulty", ""), f"约 {article.get('minutes', 1)} 分钟"]
        if article.get("word_count") is not None:
            details.append(f"{int(article['word_count']):,} 词")
        if article.get("page_start") is not None:
            end = article.get("page_end", article["page_start"])
            details.append(f"原刊 p.{article['page_start']}-{end}")
        content = [p(article["title"], "title"), Spacer(1, 1*mm), p(article["summary"], "summary"),
                   Spacer(1, 1.2*mm), p(" · ".join(details), "meta")]
        table = Table([[badge, content]], colWidths=[13*mm, 145*mm], hAlign="LEFT")
        table.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("TOPPADDING", (0, 0), (-1, -1), 3*mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 3*mm),
                                   ("LEFTPADDING", (0, 0), (0, 0), 2.5*mm), ("RIGHTPADDING", (0, 0), (0, 0), 0),
                                   ("LEFTPADDING", (1, 0), (1, 0), 1.5*mm), ("RIGHTPADDING", (1, 0), (1, 0), 4*mm)]))
        return KeepTogether([table, Spacer(1, 2.2*mm)])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    doc = GuideDoc(str(args.output), data["publication"], data["issue_date"])
    story = [Spacer(1, 8*mm)]
    if args.cover and args.cover.exists():
        image_width, image_height = ImageReader(str(args.cover)).getSize()
        ratio = image_width / image_height
        height = 102*mm
        width = min(80*mm, height * ratio)
        story += [Image(str(args.cover), width=width, height=height, hAlign="LEFT"), Spacer(1, 8*mm)]
    story += [p("FULL-ISSUE READING GUIDE", "kicker"), Spacer(1, 3*mm),
              p(f"{data['publication']}\n{data['issue_date']} 阅读导览", "cover"), Spacer(1, 4*mm),
              p(f"{len(articles)} 个条目 · 全栏目覆盖 · 中文内容预览 · CEFR 难度 · 学习者阅读时长", "sub"), Spacer(1, 9*mm)]
    theme = data.get("editorial_overview", "完整浏览本期文章，并根据兴趣与难度选择阅读路线。")
    theme_table = Table([[p("本期主线", "title"), p(theme, "body")]], colWidths=[25*mm, 133*mm])
    theme_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), CREAM), ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                                     ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 4*mm),
                                     ("RIGHTPADDING", (0, 0), (-1, -1), 4*mm), ("TOPPADDING", (0, 0), (-1, -1), 4*mm),
                                     ("BOTTOMPADDING", (0, 0), (-1, -1), 4*mm)]))
    story += [theme_table, PageBreak(), p("如何使用这份导览", "h1")]
    total = sum(int(a.get("minutes", 1)) for a in articles)
    page_phrase = f"，源刊 {data['source_pages']} 页" if data.get("source_pages") else ""
    story += [p(f"本导览覆盖 {len(articles)} 个目录条目{page_phrase}。默认按每分钟约 {data.get('speed_wpm', 130)} 个英文词估算；整期纯阅读约 {total//60} 小时 {total%60} 分钟，查词与笔记另计。", "body"), Spacer(1, 4*mm)]
    routes = data.get("reading_routes") or []
    if routes:
        rows = [[p(r.get("name", "阅读路线"), "title"), p(r.get("items", ""), "body")] for r in routes]
        rt = Table(rows, colWidths=[31*mm, 127*mm])
        rt.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("GRID", (0, 0), (-1, -1), 0.4, colors.white),
                                ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 4*mm),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 4*mm), ("TOPPADDING", (0, 0), (-1, -1), 3*mm),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 3*mm)]))
        story += [rt, Spacer(1, 5*mm)]
    story += [p("难度标尺", "h2"), p("入门 B1-B2：叙事清楚、背景门槛较低。　进阶 B2-C1：观点与政策信息密集。　高阶 C1+：长篇、抽象论证或专业词汇较多。", "body"), PageBreak(), p("全刊文章导览", "h1")]

    current_section = None
    for article in articles:
        section = article.get("section", "Articles / 文章")
        if section != current_section:
            story.append(p(section, "h2"))
            current_section = section
        story.append(card(article))
    story += [Spacer(1, 3*mm), p("说明", "h2"), p("阅读时间为估算值；难度综合句法、篇幅、背景知识和专业词汇判断，不等同于官方 CEFR 测试结果。", "meta")]
    doc.build(story)
    print(args.output.resolve())


if __name__ == "__main__":
    main()
