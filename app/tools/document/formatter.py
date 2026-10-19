import re


def _text(document, value, style=None):
    paragraph = document.add_paragraph(style=style)
    for part in re.split(r"(\*\*[^*]+\*\*)", value):
        run = paragraph.add_run(part.strip("*") if part.startswith("**") else part)
        run.bold = part.startswith("**") and part.endswith("**")


def _table(document, lines):
    rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines]
    if len(rows) < 2:
        return
    if all(re.fullmatch(r":?-+:?", cell) for cell in rows[1]):
        rows.pop(1)
    table = document.add_table(rows=1, cols=len(rows[0]))
    table.style = "Table Grid"
    for values, row in [(rows[0], table.rows[0])] + [
        (values, table.add_row()) for values in rows[1:]
    ]:
        for cell, value in zip(row.cells, values):
            cell.text = value


def write_research_document(document, content):
    tables, title_page_complete = [], False
    for line in content.splitlines() + [""]:
        value = line.strip()
        if value.startswith("|") and value.endswith("|"):
            tables.append(value)
            continue
        if tables:
            _table(document, tables)
            tables = []
        if not value or value == "---":
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", value)
        if heading:
            title = heading.group(2).strip("# ").strip()
            if title.upper() == "ABSTRACT" and not title_page_complete:
                document.add_page_break()
                title_page_complete = True
            document.add_heading(title, level=min(len(heading.group(1)), 4))
        elif re.match(r"^\d+\.\s+", value):
            _text(document, re.sub(r"^\d+\.\s+", "", value), "List Number")
        elif re.match(r"^[-*]\s+", value):
            _text(document, re.sub(r"^[-*]\s+", "", value), "List Bullet")
        else:
            _text(document, value)
