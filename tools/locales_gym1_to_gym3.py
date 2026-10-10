#!/usr/bin/env python3
"""
locales_gym1_to_gym3.py
Mapeamento e localização PT-BR dos diálogos de NPCs, eventos de história e treinadores
desde a Rota 104 até o 3º Ginásio (Mauville City).
"""
from __future__ import annotations
import json
import re
from pathlib import Path

def apply_gym1_to_gym3_strings(tree: Path) -> None:
    json_path = Path(__file__).parent / "locales_gym1_to_gym3.json"
    if not json_path.exists():
        print(f"[locales_gym1_to_gym3] Arquivo {json_path} nao encontrado!")
        return

    items = json.loads(json_path.read_text(encoding="utf-8"))
    print("\n--- Aplicando Localizações de Mapas até o 3º Ginásio (v5) ---")

    by_file: dict[str, list[dict]] = {}
    for it in items:
        by_file.setdefault(it["file"], []).append(it)

    total_applied = 0
    total_entries = len(items)

    for file_rel, file_items in by_file.items():
        target_file = tree / file_rel
        if not target_file.exists():
            continue
        text = target_file.read_text(encoding="utf-8")
        applied = 0
        for it in file_items:
            label = it["label"]
            new_block = it["block"]
            pattern = re.compile(rf'({re.escape(label)}:\s*\n(?:\t\.string\s+"[^"]*"\s*\n?)+)')
            if pattern.search(text):
                text = pattern.sub(lambda _: new_block, text, count=1)
                applied += 1
                total_applied += 1
            else:
                first_str = new_block.split('"')[1] if '"' in new_block else ""
                if label in text and first_str in text:
                    applied += 1
                    total_applied += 1
                else:
                    print(f"[{file_rel}] AVISO: Label {label} nao encontrado!")

        target_file.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
        print(f"[{file_rel}]: {applied}/{len(file_items)} blocos traduzidos.")

    print(f"--- Total Mapas Gym1->Gym3: {total_applied}/{total_entries} aplicados com sucesso! ---\n")

if __name__ == "__main__":
    apply_gym1_to_gym3_strings(Path("build/upstream"))
