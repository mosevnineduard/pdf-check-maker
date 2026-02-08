# -*- coding: utf-8 -*-
"""
PDF★Генератор — pdfkit + wkhtmltopdf (Windows).
Запуск (из корня проекта):  python generate_pdf.py
Результат: output/check_1.pdf, output/check_2.pdf, ...
"""
from __future__ import annotations

import csv
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pdfkit

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_CSV = PROJECT_ROOT / "data" / "sample_products_EXCEL_RU.csv"
TEMPLATE_HTML = PROJECT_ROOT / "templates" / "simple_check.html"
OUTPUT_DIR = PROJECT_ROOT / "output"

WKHTMLTOPDF_DEFAULT = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

CSV_ENCODING = "utf-8-sig"
CSV_DELIMITER = ";"

# Пути с Unicode (•, ★ и т.д.) могут ломать QPainter на Windows — рендерим из TEMP (ASCII).
USE_TEMP_FOR_RENDER = os.name == "nt"

PDFKIT_OPTIONS = {
    "encoding": "UTF-8",
    "enable-local-file-access": "",
    "disable-smart-shrinking": "",
    "load-error-handling": "ignore",
    "load-media-error-handling": "ignore",
    "quiet": "",
}


def get_config():
    """Возвращает pdfkit.configuration(wkhtmltopdf=...) если файл существует, иначе None (PATH)."""
    if os.name == "nt" and Path(WKHTMLTOPDF_DEFAULT).exists():
        return pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_DEFAULT)
    return None


def die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def main() -> None:
    if not TEMPLATE_HTML.exists():
        die(f"ОШИБКА: не найден шаблон: {TEMPLATE_HTML}")
    if not DATA_CSV.exists():
        die(f"ОШИБКА: не найден CSV: {DATA_CSV}")

    config = get_config()
    template = TEMPLATE_HTML.read_text(encoding="utf-8")

    with DATA_CSV.open("r", encoding=CSV_ENCODING, newline="") as f:
        reader = csv.DictReader(f, delimiter=CSV_DELIMITER)
        if not reader.fieldnames:
            die("ОШИБКА: CSV без заголовка.")
        required = {"product", "price", "qty"}
        missing = required - set(reader.fieldnames)
        if missing:
            die(f"ОШИБКА: в CSV нет колонок: {sorted(missing)}. Найдено: {reader.fieldnames}")

        rows = list(reader)
        if not rows:
            die("ОШИБКА: в CSV нет строк данных.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    created = []

    for i, row in enumerate(rows, start=1):
        html = template.replace("{{ product }}", (row.get("product") or "").strip())
        html = html.replace("{{ price }}", (row.get("price") or "").strip())
        html = html.replace("{{ qty }}", (row.get("qty") or "").strip())

        debug_html = OUTPUT_DIR / f"debug_{i}.html"
        debug_html.write_text(html, encoding="utf-8")

        out_pdf = OUTPUT_DIR / f"check_{i}.pdf"

        try:
            if USE_TEMP_FOR_RENDER:
                # Рендер из TEMP (ASCII-путь) — обход QPainter на путях с Unicode (•, ★).
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".html", delete=False, encoding="utf-8"
                ) as fh:
                    fh.write(html)
                    tmp_html = fh.name
                tmp_pdf = tmp_html.replace(".html", ".pdf")
                try:
                    pdfkit.from_file(tmp_html, tmp_pdf, options=PDFKIT_OPTIONS, configuration=config)
                    shutil.move(tmp_pdf, out_pdf)
                finally:
                    try:
                        os.unlink(tmp_html)
                    except OSError:
                        pass
                    try:
                        if Path(tmp_pdf).exists():
                            os.unlink(tmp_pdf)
                    except OSError:
                        pass
            else:
                pdfkit.from_string(html, str(out_pdf), options=PDFKIT_OPTIONS, configuration=config)
        except OSError as e:
            err_msg = str(e)
            if "wkhtmltopdf reported an error" in err_msg or "Exit with code" in err_msg:
                die(f"ОШИБКА: wkhtmltopdf найден, но ошибка рендера: {e}")
            die(
                f"ОШИБКА: не найден wkhtmltopdf. Установите его (см. README). Детали: {e}"
            )

        created.append(out_pdf)

    print("Созданы PDF:")
    for p in created:
        print(p)

    try:
        if os.name == "nt" and created:
            os.startfile(str(created[0]))  # type: ignore[attr-defined]
    except Exception:
        pass


if __name__ == "__main__":
    main()
