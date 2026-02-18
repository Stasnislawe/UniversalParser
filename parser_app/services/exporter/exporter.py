import json
import pandas as pd
from typing import List, Dict, Any
import uuid
from pathlib import Path

# Папка для временных файлов экспорта (создаётся автоматически)
EXPORT_DIR = Path("./exports")
EXPORT_DIR.mkdir(exist_ok=True)

class Exporter:
    @staticmethod
    def to_json(data: List[Dict[str, Any]]) -> str:
        """Сохраняет данные в JSON-файл и возвращает путь к файлу."""
        filename = f"export_{uuid.uuid4().hex}.json"
        filepath = EXPORT_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return str(filepath)

    @staticmethod
    def to_excel(data: List[Dict[str, Any]]) -> str:
        """Сохраняет данные в Excel-файл и возвращает путь к файлу."""
        filename = f"export_{uuid.uuid4().hex}.xlsx"
        filepath = EXPORT_DIR / filename
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
        return str(filepath)