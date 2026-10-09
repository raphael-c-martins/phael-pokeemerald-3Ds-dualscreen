#!/usr/bin/env python3
"""Stage the PT-BR localization from a user's clean PT-BR ROM.

The checked-in manifest contains source positions and ROM offsets, never game
text or graphics. Run after bootstrap applies the pinned source patches.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "builder"))
from emerald3ds_builder.rom import load_rom

PTBR_SHA1 = "18a2b0acdba046c71b8677bb58c9ee7d36f7a91f"


def encoded(data: bytes) -> str:
    return ",".join("0x%02X" % byte for byte in data)


def ensure_charmap(tree: Path) -> None:
    charmap_path = tree / "charmap.txt"
    if not charmap_path.exists():
        return
    raw = charmap_path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    additions = []
    if b"'\xc3\xa3'" not in raw:
        additions.append(b"'\xc3\xa3'         = F4")
    if b"'\xc3\x83'" not in raw:
        additions.append(b"'\xc3\x83'         = F1")
    if b"'\xc3\xb5'" not in raw:
        additions.append(b"'\xc3\xb5'         = F5")
    if b"'\xc3\x95'" not in raw:
        additions.append(b"'\xc3\x95'         = F2")
    if additions:
        raw = raw + b"\n" + b"\n".join(additions) + b"\n"
    charmap_path.write_bytes(raw)
    print("Mapeamentos PT-BR ('ã', 'Ã', 'õ', 'Õ') garantidos em charmap.txt com LF.")


def apply_system_strings(tree: Path) -> None:
    strings_c = tree / "src/strings.c"
    if not strings_c.exists():
        return
    text = strings_c.read_text(encoding="utf-8")

    replacements = {
        'const u8 gText_MainMenuNewGame[] = _("NEW GAME");': 'const u8 gText_MainMenuNewGame[] = _("NOVO JOGO");',
        'const u8 gText_MainMenuContinue[] = _("CONTINUE");': 'const u8 gText_MainMenuContinue[] = _("CONTINUAR");',
        'const u8 gText_MainMenuOption[] = _("OPTION");': 'const u8 gText_MainMenuOption[] = _("OPÇÕES");',
        'const u8 gText_ContinueMenuPlayer[] = _("PLAYER");': 'const u8 gText_ContinueMenuPlayer[] = _("JOGADOR");',
        'const u8 gText_ContinueMenuTime[] = _("TIME");': 'const u8 gText_ContinueMenuTime[] = _("TEMPO");',
        'const u8 gText_ContinueMenuPokedex[] = _("POKéDEX");': 'const u8 gText_ContinueMenuPokedex[] = _("POKéDEX");',
        'const u8 gText_ContinueMenuBadges[] = _("BADGES");': 'const u8 gText_ContinueMenuBadges[] = _("INSÍGNIAS");',
        'const u8 gText_MenuPokedex[] = _("POKéDEX");': 'const u8 gText_MenuPokedex[] = _("POKéDEX");',
        'const u8 gText_MenuPokemon[] = _("POKéMON");': 'const u8 gText_MenuPokemon[] = _("POKéMON");',
        'const u8 gText_MenuBag[] = _("BAG");': 'const u8 gText_MenuBag[] = _("MOCHILA");',
        'const u8 gText_MenuSave[] = _("SAVE");': 'const u8 gText_MenuSave[] = _("SALVAR");',
        'const u8 gText_MenuOption[] = _("OPTION");': 'const u8 gText_MenuOption[] = _("OPÇÃO");',
        'const u8 gText_MenuExit[] = _("EXIT");': 'const u8 gText_MenuExit[] = _("SAIR");',
        'const u8 gText_OptionMenuCancel[] = _("CANCEL");': 'const u8 gText_OptionMenuCancel[] = _("CANCELAR");',
    }

    applied = 0
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            applied += 1

    strings_c.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
    print(f"Strings de sistema e menus: {applied}/{len(replacements)} traduzidas com sucesso em src/strings.c.")


def apply_map_strings(tree: Path) -> None:
    littleroot = tree / "data/maps/LittlerootTown/scripts.inc"
    if not littleroot.exists():
        return
    text = littleroot.read_text(encoding="utf-8")

    replacements = {
        ('LittlerootTown_Text_OurNewHomeLetsGoInside:\n'
         '\t.string "MOM: {PLAYER}, we\'re here, honey!\\p"\n'
         '\t.string "It must be tiring riding with our things\\n"\n'
         '\t.string "in the moving truck.\\p"\n'
         '\t.string "Well, this is LITTLEROOT TOWN.\\p"\n'
         '\t.string "How do you like it?\\n"\n'
         '\t.string "This is our new home!\\p"\n'
         '\t.string "It has a quaint feel, but it seems to be\\n"\n'
         '\t.string "an easy place to live, don\'t you think?\\p"\n'
         '\t.string "And, you get your own room, {PLAYER}!\\n"\n'
         '\t.string "Let\'s go inside.$"'):
        ('LittlerootTown_Text_OurNewHomeLetsGoInside:\n'
         '\t.string "MÃE: {PLAYER}, nós já chegamos!\\p"\n'
         '\t.string "Deve ser cansativo viajar no caminhão\\n"\n'
         '\t.string "de mudança com todos os móveis…\\p"\n'
         '\t.string "Bem, esta é a bela VILA RAIZ.\\p"\n'
         '\t.string "O quê? Você gostou?\\n"\n'
         '\t.string "Este é o lugar onde vamos morar.\\p"\n'
         '\t.string "É um lugar pitoresco, mas eu acho que\\n"\n'
         '\t.string "você pode viver muito bem aqui.\\p"\n'
         '\t.string "{PLAYER}, você terá o seu próprio quarto.\\n"\n'
         '\t.string "Vamos logo entrar em casa.$"'),

        ('LittlerootTown_Text_TownSign:\n'
         '\t.string "LITTLEROOT TOWN\\n"\n'
         '\t.string "“A town that can\'t be shaded any hue.”$"'):
        ('LittlerootTown_Text_TownSign:\n'
         '\t.string "VILA RAIZ\\n"\n'
         '\t.string "“Uma vila que não se prende a cores.”$"'),

        ('LittlerootTown_Text_ProfBirchsLab:\n'
         '\t.string "PROF. BIRCH\'S POKéMON LAB$"'):
        ('LittlerootTown_Text_ProfBirchsLab:\n'
         '\t.string "LABORATÓRIO DO PROF. BIRCH$"'),

        ('LittlerootTown_Text_PlayersHouse:\n'
         '\t.string "{PLAYER}\'s HOUSE$"'):
        ('LittlerootTown_Text_PlayersHouse:\n'
         '\t.string "CASA DE {PLAYER}$"'),
    }

    applied = 0
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            applied += 1

    littleroot.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
    print(f"Diálogos de Littleroot Town: {applied}/{len(replacements)} traduzidos em scripts.inc.")


def stage(tree: Path, rom_path: Path) -> None:
    manifest_path = ROOT / "tools/locales/ptbr.json.gz"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    manifest = json.loads(gzip.decompress(manifest_path.read_bytes()))
    rom = load_rom(rom_path, supported=(PTBR_SHA1,))
    source = rom.data

    writes: dict[Path, bytes] = {}
    print(f"Applying PT-BR text localizations to {len(manifest['files'])} files...")

    applied_files = 0
    applied_edits = 0

    for relative, file in manifest["files"].items():
        path = tree / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if hashlib.sha256(text.encode()).hexdigest() != file["sha256"]:
            continue

        previous_end = 0
        valid_edits = []
        for start, end, offset, size, kind in sorted(file["edits"]):
            if previous_end <= start < end <= len(text) and 0 <= offset < offset + size <= len(source):
                valid_edits.append((start, end, offset, size, kind))
                previous_end = end

        for start, end, offset, size, kind in sorted(valid_edits, reverse=True):
            data = source[offset:offset + size]
            if kind == "c":
                replacement = "{" + encoded(data) + "}"
            elif kind == "asm":
                replacement = "\n\t.byte " + encoded(data) + "\n"
            elif kind == "u32":
                replacement = str(struct.unpack("<I", data)[0])
            elif kind == "u16s":
                replacement = ",".join("0x%04X" % n for n in struct.unpack("<6H", data))
            elif kind == "u16array":
                replacement = ",".join("0x%04X" % n for n in struct.unpack("<%dH" % (size // 2), data))
            else:
                replacement = "{" + encoded(data) + "}"

            text = text[:start] + replacement + text[end:]
            applied_edits += 1

        writes[path] = text.replace("\r\n", "\n").encode("utf-8")
        applied_files += 1

    for path, data in writes.items():
        path.write_bytes(data)

    ensure_charmap(tree)
    apply_system_strings(tree)
    apply_map_strings(tree)

    (tree / ".emerald3ds-locale").write_bytes(b"PTBR stable v2\n")
    print(f"PT-BR staging complete! {applied_edits} edits applied across {applied_files} source files.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--rom", type=Path, required=True)
    args = parser.parse_args()
    stage(args.tree.resolve(), args.rom)


if __name__ == "__main__":
    main()
