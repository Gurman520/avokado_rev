import os
from fastapi.templating import Jinja2Templates
from num2words import num2words


def _num2words_ru(value):
    if value is None:
        return ""
    try:
        return num2words(float(value), lang="ru")
    except Exception:
        return str(value)

templates = Jinja2Templates(directory="app/templates")
templates.env.filters["num2words"] = _num2words_ru

