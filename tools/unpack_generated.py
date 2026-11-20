"""Extract the generated ZIP variants into browseable datapack source directories."""
from pathlib import Path
from zipfile import ZipFile
import shutil

root = Path(__file__).resolve().parent.parent
for label, filename in [
    ("addon", "The_Tarot_Club_22_Arcana_1.18.2.zip"),
    ("only", "The_Tarot_Club_22_Arcana_Only_1.18.2.zip"),
]:
    archive = root / "output" / filename
    dest = root / "datapacks" / label
    if not archive.is_file():
        raise SystemExit(f"Missing {archive}; run python3 generate.py first")
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    with ZipFile(archive) as z:
        z.extractall(dest)
    print(f"Extracted {archive.name} -> {dest}")
