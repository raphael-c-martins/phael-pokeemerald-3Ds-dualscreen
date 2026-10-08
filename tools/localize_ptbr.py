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
            # Source differs from pinned tree; skip safely
            continue
            
        previous_end = 0
        valid_edits = []
        for start, end, offset, size, kind in sorted(file["edits"]):
            if previous_end <= start < end <= len(text) and 0 <= offset < offset + size <= len(source):
                valid_edits.append((start, end, offset, size, kind))
                previous_end = end

        # Apply from back to front to preserve string indices
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

        writes[path] = text.encode("utf-8")
        applied_files += 1

    # Write all modified source files
    for path, data in writes.items():
        path.write_bytes(data)

    (tree / ".emerald3ds-locale").write_text("PTBR experimental\n")
    print(f"PT-BR staging complete! {applied_edits} edits applied across {applied_files} source files.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--rom", type=Path, required=True)
    args = parser.parse_args()
    stage(args.tree.resolve(), args.rom)


if __name__ == "__main__":
    main()
