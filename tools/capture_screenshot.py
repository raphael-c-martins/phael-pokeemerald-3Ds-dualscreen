#!/usr/bin/env python3
"""Utilitário de captura de tela de alta precisão para QA do Citra."""
import sys
import ctypes
from pathlib import Path
from PIL import ImageGrab

def main():
    if len(sys.argv) < 6:
        print("Uso: capture_screenshot.py <left> <top> <right> <bottom> <dest_path> [description]")
        return 1

    left = int(sys.argv[1])
    top = int(sys.argv[2])
    right = int(sys.argv[3])
    bottom = int(sys.argv[4])
    dest = Path(sys.argv[5])
    desc = sys.argv[6] if len(sys.argv) > 6 else ""

    # Anexa à sessão interativa de desktop
    hwinsta = ctypes.windll.user32.OpenWindowStationW('WinSta0', False, 0x037F)
    if hwinsta:
        ctypes.windll.user32.SetProcessWindowStation(hwinsta)
    hdesk = ctypes.windll.user32.OpenDesktopW('Default', 0, False, 0x01FF)
    if hdesk:
        ctypes.windll.user32.SetThreadDesktop(hdesk)

    dest.parent.mkdir(parents=True, exist_ok=True)
    bbox = (max(0, left), max(0, top), max(left + 100, right), max(top + 100, bottom))

    try:
        img = ImageGrab.grab(bbox=bbox)
        img.save(dest)
        print(f"  [QA SCREENSHOT] {dest.name} -> {desc}")
        return 0
    except Exception as e:
        print(f"  [AVISO] Falha ao capturar screenshot: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
