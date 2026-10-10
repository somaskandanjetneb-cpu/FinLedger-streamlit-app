from pathlib import Path
import sys

def app_base():
    # Works both from source and from a PyInstaller/EXE bundle.
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

BASE_DIR = app_base()
DATA_DIR = BASE_DIR / "data"
REPORT_DIR = BASE_DIR / "reports"
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = BASE_DIR / "fonts"
DB_PATH = DATA_DIR / "income_expense.db"

for p in (DATA_DIR, REPORT_DIR, ASSETS_DIR, FONTS_DIR):
    p.mkdir(parents=True, exist_ok=True)

APP_TITLE = "Professional Income & Expense Manager"
CURRENCY = "₹"

def money(value):
    try:
        return f"₹ {float(value):,.2f}"
    except (TypeError, ValueError):
        return "₹ 0.00"
