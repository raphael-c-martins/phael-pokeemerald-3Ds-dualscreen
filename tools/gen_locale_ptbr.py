#!/usr/bin/env python3
"""
gen_locale_ptbr.py
Gera o manifesto tools/locales/ptbr.json.gz mapeando textos da ROM PT-BR.
Usa o layout estrutural de spanish.json.gz como gabarito de posições no código.
"""
from __future__ import annotations

import gzip
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(r"D:\Projetos\pokeemerald-3Ds-dualscreen")
tree = ROOT / "build/upstream"
rom_usa_path = ROOT / "# TEMPORARIO/Pokemon - Emerald Version (USA, Europe)/Pokemon - Emerald Version (USA, Europe).gba"
rom_br_path = ROOT / "# TEMPORARIO/Pokémon Emerald (PT-BR)/Pokémon Emerald (PT-BR).gba"

manifest_es = json.loads(gzip.decompress((ROOT / "tools/locales/spanish.json.gz").read_bytes()))
rom_usa = rom_usa_path.read_bytes()
rom_br = rom_br_path.read_bytes()

# 1. Carregar charmap completo do pokeemerald
CHARMAP = {}
REV_CHARMAP = {}
for line in (tree / "charmap.txt").read_text(encoding="utf-8", errors="replace").splitlines():
    line = line.strip()
    if not line or line.startswith("//"): continue
    m = re.match(r"^'([^']*)'\s*=\s*([0-9a-fA-F]+)", line)
    if m:
        c, v = m.group(1), int(m.group(2), 16)
        CHARMAP[c] = v
        REV_CHARMAP[v] = c

# Extensões comuns de escape
ESCAPE_MAP = {
    r"\n": 0xFE, r"\l": 0xFA, r"\p": 0xFB,
    "{PLAYER}": 0x01, "{RIVAL}": 0x06, "{KUN}": 0x08,
}

def encode_charmap(s: str) -> bytes | None:
    res = bytearray()
    i = 0
    while i < len(s):
        # Escapes especiais
        matched_esc = False
        for esc, val in ESCAPE_MAP.items():
            if s.startswith(esc, i):
                res.append(val)
                i += len(esc)
                matched_esc = True
                break
        if matched_esc:
            continue

        # 2-char tokens
        if i + 1 < len(s) and s[i:i+2] in CHARMAP:
            res.append(CHARMAP[s[i:i+2]])
            i += 2
        elif s[i] in CHARMAP:
            res.append(CHARMAP[s[i]])
            i += 1
        elif s[i] == ' ':
            res.append(0x00)
            i += 1
        else:
            return None
    return bytes(res)

print("Iniciando mapeamento dos 449 arquivos estruturais...")
ptbr_files = {}
total_edits = 0
mapped_edits = 0

for relative, file_info in manifest_es["files"].items():
    src_file = tree / relative
    if not src_file.exists():
        continue
    src_text = src_file.read_text(encoding="utf-8")
    
    edits_for_file = []
    
    for start, end, es_off, es_sz, kind in file_info["edits"]:
        total_edits += 1
        snippet = src_text[start:end]
        
        # Extrair texto entre aspas
        m = re.search(r'"([^"]*)"', snippet)
        if not m:
            continue
        eng_raw = m.group(1)
        if not eng_raw:
            continue
            
        enc = encode_charmap(eng_raw)
        if not enc or len(enc) < 2:
            # Tentar substring de 10 caracteres se for muito longo
            if len(eng_raw) >= 10:
                enc = encode_charmap(eng_raw[:10])
        if not enc:
            continue
            
        # Buscar na ROM USA
        pos_usa = rom_usa.find(enc)
        if pos_usa == -1:
            continue
            
        # Verificar o que há na ROM PT-BR nessa posição
        # Na ROM PT-BR, o texto termina com 0xFF
        end_ff = rom_br.find(b"\xff", pos_usa, pos_usa + 350)
        if end_ff == -1:
            continue
            
        sz_br = end_ff - pos_usa + 1
        br_bytes = rom_br[pos_usa:end_ff + 1]
        
        # Validar integridade básica dos bytes (não pode ser lixo 0x00 ou 0xFF puro)
        if sz_br < 2 or br_bytes.count(b"\xff") > 2:
            continue
            
        # Adicionar edit válido
        edits_for_file.append([start, end, pos_usa, sz_br, kind])
        mapped_edits += 1

    if edits_for_file:
        ptbr_files[relative] = {
            "sha256": file_info["sha256"],
            "edits": edits_for_file
        }

print(f"Mapeamento concluído: {mapped_edits} / {total_edits} edits mapeados ({len(ptbr_files)} arquivos).")

ptbr_manifest = {
    "version": 1,
    "rom_sha1": "18a2b0acdba046c71b8677bb58c9ee7d36f7a91f",
    "status": "experimental-ptbr",
    "unmapped_source_texts": total_edits - mapped_edits,
    "files": ptbr_files,
    "graphics": [],
    "credits": 0,
    "floors": []
}

out_path = ROOT / "tools/locales/ptbr.json.gz"
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_bytes(gzip.compress(json.dumps(ptbr_manifest, separators=(",", ":")).encode("utf-8")))
print(f"Manifesto salvo com sucesso em: {out_path} ({out_path.stat().st_size} bytes)")
