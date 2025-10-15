import json
from pathlib import Path
import shutil

def load_json(file_path: Path):
    if file_path.exists():
        return json.loads(file_path.read_text(encoding="utf-8").strip())
    return {}

def save_json(file_path: Path, data: dict):
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def copy_template(template_path: Path, target_path: Path):
    if template_path.exists():
        shutil.copy(template_path, target_path)

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)
