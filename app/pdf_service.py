# """
# Универсальная генерация PDF.
# - На Linux (production): использует WeasyPrint.
# - На Windows (development): использует pdfkit/wkhtmltopdf.
# - Можно принудительно задать движок через переменную окружения PDF_ENGINE=weasyprint|pdfkit
# """
# import os
# import platform
# import subprocess

# _engine = None


# def _try_weasyprint():
#     try:
#         from weasyprint import HTML  # noqa
#         return "weasyprint"
#     except Exception:
#         return None


# def _try_pdfkit():
#     try:
#         import pdfkit  # noqa
#         return "pdfkit"
#     except Exception:
#         return None


# def _detect_engine():
#     forced = os.getenv("PDF_ENGINE", "").strip().lower()
#     if forced in ("weasyprint", "pdfkit"):
#         return forced

#     system = platform.system()
#     if system == "Windows":
#         # На Windows WeasyPrint требует GTK, поэтому предпочитаем pdfkit
#         if _try_pdfkit():
#             return "pdfkit"
#         if _try_weasyprint():
#             return "weasyprint"
#     else:
#         # На Linux/macOS WeasyPrint предпочтительнее
#         if _try_weasyprint():
#             return "weasyprint"
#         if _try_pdfkit():
#             return "pdfkit"

#     raise RuntimeError(
#         "Не удалось найти движок генерации PDF. "
#         "Установите weasyprint (Linux) или pdfkit+wkhtmltopdf (Windows)."
#     )


# def get_engine():
#     global _engine
#     if _engine is None:
#         _engine = _detect_engine()
#     return _engine


# def _wkhtmltopdf_path():
#     """Ищем wkhtmltopdf: сначала в PATH, потом в типовых местах Windows."""
#     # 1. Явно указанный путь
#     env_path = os.getenv("WKHTMLTOPDF_PATH")
#     if env_path and os.path.isfile(env_path):
#         return env_path

#     # 2. В PATH
#     from shutil import which
#     found = which("wkhtmltopdf") or which("wkhtmltopdf.exe")
#     if found:
#         return found

#     # 3. Типовые места установки на Windows
#     if platform.system() == "Windows":
#         candidates = [
#             r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
#             r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
#         ]
#         for c in candidates:
#             if os.path.isfile(c):
#                 return c
#     return None


# def html_to_pdf(html_content: str, output_path: str) -> str:
#     """
#     Генерирует PDF из HTML-строки.
#     Возвращает путь к созданному файлу.
#     """
#     engine = get_engine()

#     if engine == "weasyprint":
#         from weasyprint import HTML
#         HTML(string=html_content).write_pdf(output_path)
#         return output_path

#     if engine == "pdfkit":
#         import pdfkit
#         wk = _wkhtmltopdf_path()
#         options = {
#             "encoding": "UTF-8",
#             "enable-local-file-access": None,
#             "quiet": "",
#         }
#         if wk:
#             config = pdfkit.configuration(wkhtmltopdf=wk)
#             pdfkit.from_string(html_content, output_path, options=options, configuration=config)
#         else:
#             pdfkit.from_string(html_content, output_path, options=options)
#         return output_path

#     raise RuntimeError(f"Неизвестный движок PDF: {engine}")

"""
Генерация PDF через pdfkit + wkhtmltopdf.
Автопоиск wkhtmltopdf:
  1. Переменная окружения WKHTMLTOPDF_PATH
  2. PATH
  3. Типовые места установки (Windows)
"""
import os
import platform
import shutil


def _find_wkhtmltopdf() -> str | None:
    # 1. Переменная окружения
    env_path = os.getenv("WKHTMLTOPDF_PATH", "").strip()
    if env_path and os.path.isfile(env_path):
        return env_path

    # 2. В PATH
    for name in ("wkhtmltopdf", "wkhtmltopdf.exe"):
        found = shutil.which(name)
        if found:
            return found

    # 3. Типовые места установки
    candidates = []
    if platform.system() == "Windows":
        candidates = [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
        ]
    else:
        candidates = [
            "/usr/bin/wkhtmltopdf",
            "/usr/local/bin/wkhtmltopdf",
            "/opt/wkhtmltopdf/bin/wkhtmltopdf",
        ]
    for c in candidates:
        if os.path.isfile(c):
            return c

    return None


def html_to_pdf(html_content: str, output_path: str) -> str:
    """Генерирует PDF из HTML-строки. Возвращает путь к файлу."""
    import pdfkit

    wk = _find_wkhtmltopdf()
    if not wk:
        raise RuntimeError(
            "Не найден wkhtmltopdf.\n"
            "Windows: скачайте и установите "
            "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltopdf-0.12.6-1.msw64.exe "
            "в C:\\Program Files\\wkhtmltopdf\\\n"
            "Linux: sudo apt install -y wkhtmltopdf\n"
            "Либо укажите путь в переменной окружения WKHTMLTOPDF_PATH"
        )

    options = {
        "encoding": "UTF-8",
        "enable-local-file-access": None,
        "quiet": "",
        "print-media-type": None,
        "margin-top": "15mm",
        "margin-bottom": "15mm",
        "margin-left": "12mm",
        "margin-right": "12mm",
    }

    config = pdfkit.configuration(wkhtmltopdf=wk)
    pdfkit.from_string(html_content, output_path, options=options, configuration=config)
    return output_path
