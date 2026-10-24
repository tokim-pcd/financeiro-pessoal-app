from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "Financeiro Pessoal"
APP_DIR = Path.home() / "FinanceiroPessoal"
DB_PATH = APP_DIR / "financeiro_pessoal.db"

os.makedirs(APP_DIR, exist_ok=True)
