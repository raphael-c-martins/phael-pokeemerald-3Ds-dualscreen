#!/usr/bin/env python3
"""Citra Runner & QA Telemetry Automation for Pokémon Emerald 3DS.

Permite lançar o Citra diretamente pela linha de comando, injetar saves de
teste, ativar o modo sentinela (debug.txt) e auditar logs e capturas de tela.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CITRA_DIR = Path(r"E:\# Video-games, Jogos e Emuladores\# Emuladores\Citra")
APPDATA_CITRA = Path(os.path.expandvars(r"%APPDATA%\Citra"))
SDMC_EMERALD = APPDATA_CITRA / "sdmc/3ds/emerald3ds"


def find_citra_binaries() -> tuple[Path | None, Path | None]:
    candidates = [
        DEFAULT_CITRA_DIR,
        Path(os.path.expandvars(r"%LOCALAPPDATA%\citra")),
        Path(os.path.expandvars(r"%APPDATA%\citra")),
    ]
    cli_exe = None
    gui_exe = None

    for d in candidates:
        if (d / "citra.exe").exists() and not cli_exe:
            cli_exe = d / "citra.exe"
        if (d / "citra-qt.exe").exists() and not gui_exe:
            gui_exe = d / "citra-qt.exe"

    return cli_exe, gui_exe


def setup_sdmc(enable_debug: bool = True, save_path: Path | None = None) -> None:
    SDMC_EMERALD.mkdir(parents=True, exist_ok=True)
    if enable_debug:
        (SDMC_EMERALD / "debug.txt").write_text("debug\n", encoding="utf-8")
        print(f"[Citra Runner] Sentinela debug.txt ativado em: {SDMC_EMERALD}")

    if save_path and save_path.exists():
        dest = SDMC_EMERALD / "emerald3ds.sav"
        shutil.copy2(save_path, dest)
        print(f"[Citra Runner] Save injetado com sucesso: {dest}")


def get_latest_3dsx() -> Path | None:
    candidates = [
        ROOT / "dist_3ds/emerald3ds.3dsx",
        ROOT / "dist_3ds/emerald3ds_v4.3dsx",
        ROOT / "build/upstream/3ds_port/emerald3ds.3dsx",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def run_citra(target_3dsx: Path, use_gui: bool = True, wait_seconds: int = 0) -> int:
    cli_exe, gui_exe = find_citra_binaries()
    exe = gui_exe if use_gui else (cli_exe or gui_exe)
    if not exe or not exe.exists():
        print("[ERRO] Executável do Citra não encontrado!")
        return 1

    print(f"[Citra Runner] Iniciando: {exe.name}")
    print(f"[Citra Runner] Alvo: {target_3dsx}")

    setup_sdmc(enable_debug=True)

    cmd = [str(exe), str(target_3dsx)]
    if wait_seconds > 0:
        proc = subprocess.Popen(cmd)
        print(f"[Citra Runner] Executando por {wait_seconds} segundos...")
        time.sleep(wait_seconds)
        proc.terminate()
        return 0
    else:
        return subprocess.run(cmd).returncode


def inspect_telemetry() -> None:
    port_log = SDMC_EMERALD / "port.log"
    citra_log = APPDATA_CITRA / "log/citra_log.txt"

    print("\n=== TELEMETRIA DO CITRA / EMERALD3DS ===")
    if port_log.exists():
        lines = port_log.read_text(encoding="utf-8", errors="replace").splitlines()
        print(f"[port.log] Encontrado ({len(lines)} linhas). Últimas entradas:")
        for line in lines[-15:]:
            print(f"  {line}")
    else:
        print("[port.log] Ainda não gerado pelo jogo nesta sessão.")

    if citra_log.exists():
        lines = citra_log.read_text(encoding="utf-8", errors="replace").splitlines()
        print(f"\n[citra_log.txt] Encontrado ({len(lines)} linhas). Avisos e erros recentes:")
        errors = [l for l in lines if any(k in l for k in ["<Error>", "<Critical>", "Panic", "Abort"])]
        if errors:
            for err in errors[-10:]:
                print(f"  ! {err}")
        else:
            print("  Nenhum erro crítico registrado pelo emulador.")


def inspect_screenshots() -> list[Path]:
    ss_dir = APPDATA_CITRA / "screenshots"
    if not ss_dir.exists():
        return []
    files = sorted(ss_dir.glob("*.png"), key=lambda f: f.stat().st_mtime, reverse=True)
    print(f"\n=== CAPTURAS DE TELA DO CITRA ({len(files)} encontradas) ===")
    for f in files[:5]:
        print(f"  {f.name} ({f.stat().st_size // 1024} KB)")
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")

    # run
    p_run = sub.add_parser("run", help="Inicia o jogo no Citra")
    p_run.add_argument("--target", type=Path, default=None, help="Caminho do .3dsx (default: dist_3ds)")
    p_run.add_argument("--cli", action="store_true", help="Usa citra.exe CLI em vez de citra-qt.exe")
    p_run.add_argument("--wait", type=int, default=0, help="Tempo de execução antes de fechar (segundos)")
    p_run.add_argument("--save", type=Path, default=None, help="Caminho de um save .sav para injetar")

    # test
    p_test = sub.add_parser("test", help="Executa teste automatizado de QA no Citra com auditoria")
    p_test.add_argument("--clean-save", action="store_true", help="Remove save anterior para testar New Game limpo")
    p_test.add_argument("--target", type=Path, default=None, help="Caminho do .3dsx (default: mais recente)")
    p_test.add_argument("--wait", type=int, default=0, help="Tempo de execução em segundos (0 = livre)")

    # logs
    sub.add_parser("logs", help="Audita a telemetria e os logs de port.log e citra_log.txt")

    # screenshots
    sub.add_parser("screenshots", help="Lista e localiza capturas de tela")

    args = parser.parse_args()

    if args.command == "run":
        target = args.target or get_latest_3dsx()
        if not target:
            print("[ERRO] Nenhum executável .3dsx encontrado para executar.")
            return 1
        if args.save:
            setup_sdmc(save_path=args.save)
        return run_citra(target, use_gui=not args.cli, wait_seconds=args.wait)

    elif args.command == "test":
        target = args.target or get_latest_3dsx()
        if not target:
            print("[ERRO] Nenhum executável .3dsx encontrado para executar.")
            return 1
        if args.clean_save:
            save_file = SDMC_EMERALD / "emerald3ds.sav"
            if save_file.exists():
                save_file.unlink()
                print(f"[Citra Runner] Save anterior removido para teste limpo: {save_file}")
        setup_sdmc(enable_debug=True)
        print(f"[Citra QA] Iniciando teste autônomo do executável: {target.name}")
        rc = run_citra(target, use_gui=True, wait_seconds=args.wait)
        inspect_telemetry()
        return rc

    elif args.command == "logs":
        inspect_telemetry()
        return 0

    elif args.command == "screenshots":
        inspect_screenshots()
        return 0

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
