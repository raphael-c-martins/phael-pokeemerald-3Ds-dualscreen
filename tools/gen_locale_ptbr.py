#!/usr/bin/env python3
"""
gen_locale_ptbr.py
Gera o manifesto seguro tools/locales/ptbr.json.gz com mapeamento das tabelas
de dados (golpes, itens, descrições, espécies, habilidades e pokédex) da ROM PT-BR,
com validação estrita de limites de buffers para evitar qualquer overflow de memória.
"""
from __future__ import annotations

import gzip
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
tree = ROOT / "build/upstream"
rom_usa_path = ROOT / "# TEMPORARIO/Pokemon - Emerald Version (USA, Europe)/Pokemon - Emerald Version (USA, Europe).gba"
rom_br_path = ROOT / "# TEMPORARIO/Pokémon Emerald (PT-BR)/Pokémon Emerald (PT-BR).gba"

manifest_es = json.loads(gzip.decompress((ROOT / "tools/locales/spanish.json.gz").read_bytes()))
rom_usa = rom_usa_path.read_bytes()
rom_br = rom_br_path.read_bytes()

# 1. Carregar charmap
CHARMAP = {}
charmap_file = tree / "charmap.txt"
for line in charmap_file.read_text(encoding="utf-8", errors="replace").splitlines():
    line = line.strip()
    if not line or line.startswith("//"):
        continue
    m = re.match(r"^'([^']*)'\s*=\s*([0-9a-fA-F]+)", line)
    if m:
        CHARMAP[m.group(1)] = int(m.group(2), 16)


def encode_charmap(s: str) -> bytes | None:
    res = bytearray()
    i = 0
    while i < len(s):
        if i + 1 < len(s) and s[i:i + 2] in CHARMAP:
            res.append(CHARMAP[s[i:i + 2]])
            i += 2
        elif s[i] in CHARMAP:
            res.append(CHARMAP[s[i]])
            i += 1
        elif s[i] == ' ':
            res.append(0x00)
            i += 1
        elif s[i] == '\n':
            res.append(0xFE)
            i += 1
        elif s[i] == '\\' and i + 1 < len(s) and s[i + 1] == 'n':
            res.append(0xFE)
            i += 2
        else:
            return None
    return bytes(res)


# Tabelas estruturadas com limites de buffer bem definidos
TABLES = [
    'src/data/text/move_names.h',
    'src/data/text/move_descriptions.h',
    'src/data/text/item_descriptions.h',
    'src/data/items.h',
    'src/data/text/species_names.h',
    'src/data/text/abilities.h',
    'src/data/pokemon/pokedex_text.h',
    'src/data/text/trainer_class_names.h',
    'src/data/text/nature_names.h',
]

LIMITS = {
    'src/data/text/move_names.h': 13,
    'src/data/text/species_names.h': 11,
    'src/data/items.h': 15,
    'src/data/text/abilities.h': 13,
    'src/data/text/nature_names.h': 8,
    'src/data/text/trainer_class_names.h': 14,
}

print("Iniciando geração do manifesto estável PT-BR (v2)...")
ptbr_files: dict[str, dict] = {}
total_mapped = 0

for table in TABLES:
    if table not in manifest_es["files"]:
        continue
    file_info = manifest_es["files"][table]
    src_file = tree / table
    if not src_file.exists():
        continue
    src_text = src_file.read_text(encoding="utf-8")
    
    edits_for_file = []
    limit = LIMITS.get(table, 500)
    
    for start, end, es_off, es_sz, kind in file_info["edits"]:
        snip = src_text[start:end]
        m = re.search(r'"([^"]*)"', snip)
        if not m:
            continue
        eng = m.group(1)
        if not eng:
            continue
            
        enc = encode_charmap(eng)
        if not enc and len(eng) >= 12:
            enc = encode_charmap(eng[:12])
        if not enc:
            continue
            
        if table in ('src/data/text/species_names.h', 'src/data/text/move_names.h'):
            pos = rom_usa.find(enc + b'\xff')
        else:
            pos = rom_usa.find(enc)
        if pos == -1:
            continue
            
        end_ff = rom_br.find(b'\xff', pos, pos + 300)
        if end_ff == -1:
            continue
            
        sz = end_ff - pos + 1
        br_bytes = rom_br[pos:end_ff + 1]
        
        # Validação estrita: não pode ultrapassar o buffer e nem ser lixo
        if sz < 2 or sz > limit or br_bytes.count(b'\xff') > 2:
            continue
            
        edits_for_file.append([start, end, pos, sz, kind])
        total_mapped += 1
        
    if edits_for_file:
        ptbr_files[table] = {
            "sha256": file_info["sha256"],
            "edits": edits_for_file
        }
        print(f"  -> {table}: {len(edits_for_file)} itens mapeados")

ptbr_manifest = {
    "version": 2,
    "rom_sha1": "18a2b0acdba046c71b8677bb58c9ee7d36f7a91f",
    "status": "stable-tables-v2",
    "files": ptbr_files,
    "graphics": [],
    "credits": 0,
    "floors": []
}

out_path = ROOT / "tools/locales/ptbr.json.gz"
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_bytes(gzip.compress(json.dumps(ptbr_manifest, separators=(",", ":")).encode("utf-8")))
print(f"\nManifesto v2 gerado com sucesso: {out_path} ({total_mapped} entradas, {out_path.stat().st_size} bytes).")
