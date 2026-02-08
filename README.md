# PDF★Генератор (pdfkit + wkhtmltopdf, Windows)

## Требования

Нужно установить **wkhtmltopdf** (отдельно от Python).

- Скачать: https://wkhtmltopdf.org/downloads.html
- Путь установки по умолчанию на Windows:
  `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe`

## Установка и запуск

После установки wkhtmltopdf:

```bash
pip install -r requirements.txt
python generate_pdf.py
```

## Выход

Файлы PDF создаются в папке `output/`: `check_1.pdf`, `check_2.pdf`, … `check_N.pdf`.
