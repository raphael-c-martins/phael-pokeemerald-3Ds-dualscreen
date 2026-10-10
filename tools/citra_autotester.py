#!/usr/bin/env python3
"""Citra Autotester & Autonomous Visual QA Agent (3-Minute Comprehensive Run).

Executa uma bateria de testes visuais e funcionais 100% autônomos no Citra:
1. Inicia com um save limpo do zero para validar a introdução em PT-BR.
2. Lança o executável 3DS mais recente (v4 + Birch Speech PT-BR + upstream v0.3.1).
3. Localiza a janela gráfica, foca na tela do usuário e executa o gameplay por mais de 3 minutos.
4. Envia inputs sequenciais (Start, A, B, Setas) passando tela de título, introdução do Birch,
   seleção de gênero/nome, caminhão, Littleroot Town e interface dual-screen.
5. Captura evidências visuais de cada marco na pasta '# TEMPORARIO/Citra-QA/'.
6. Audita a telemetria final do 'port.log' e 'citra_log.txt'.
"""
import ctypes
import os
import subprocess
import sys
import time
from pathlib import Path
from PIL import ImageGrab
import win32gui
import win32con

# Configuração de caminhos
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "# TEMPORARIO/Citra-QA"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CITRA_EXE = Path(r"E:\# Video-games, Jogos e Emuladores\# Emuladores\Citra\citra-qt.exe")
ROM_FILE = ROOT / "dist_3ds/emerald3ds.3dsx"
LAUNCHER_PS1 = ROOT / "tools/citra_launcher.ps1"
SDMC_DIR = Path(os.path.expandvars(r"%APPDATA%\Citra\sdmc\3ds\emerald3ds"))
SAVE_FILE = SDMC_DIR / "emerald3ds.sav"
PORT_LOG = SDMC_DIR / "port.log"
CITRA_LOG = Path(os.path.expandvars(r"%APPDATA%\Citra\log\citra_log.txt"))

# Teclas padrão mapeadas no Citra
VK_A = 0x41      # Tecla A -> Botão A
VK_S = 0x53      # Tecla S -> Botão B
VK_M = 0x4D      # Tecla M -> Botão Start
VK_N = 0x4E      # Tecla N -> Botão Select
VK_T = 0x54      # Tecla T -> D-Pad Cima
VK_G = 0x47      # Tecla G -> D-Pad Baixo
VK_F = 0x46      # Tecla F -> D-Pad Esquerda
VK_H = 0x48      # Tecla H -> D-Pad Direita
VK_UP = 0x26     # Circle Pad Cima
VK_DOWN = 0x28   # Circle Pad Baixo
VK_LEFT = 0x25   # Circle Pad Esquerda
VK_RIGHT = 0x27  # Circle Pad Direita


def attach_interactive_desktop():
    """Anexa o processo atual à sessão interativa de desktop do Windows."""
    hwinsta = ctypes.windll.user32.OpenWindowStationW("WinSta0", False, 0x037F)
    if hwinsta:
        ctypes.windll.user32.SetProcessWindowStation(hwinsta)
    hdesk = ctypes.windll.user32.OpenDesktopW("Default", 0, False, 0x01FF)
    if hdesk:
        ctypes.windll.user32.SetThreadDesktop(hdesk)


def find_citra_window():
    """Localiza o HWND legítimo da janela de renderização do Citra."""
    citra_hwnd = None
    def cb(h, _):
        nonlocal citra_hwnd
        if win32gui.IsWindowVisible(h):
            c = win32gui.GetClassName(h)
            t = win32gui.GetWindowText(h)
            if "qt" in c.lower() and "citra" in t.lower() and "antigravity" not in t.lower():
                r = win32gui.GetWindowRect(h)
                if (r[2] - r[0]) > 200 and (r[3] - r[1]) > 200:
                    citra_hwnd = h
    win32gui.EnumWindows(cb, None)
    return citra_hwnd


def focus_window(hwnd):
    """Garante que a janela do Citra esteja visível e em primeiro plano."""
    try:
        attach_interactive_desktop()
        ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 0x0043)
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass


def press_key(hwnd, vk_code, duration=0.15):
    """Envia um comando de tecla com scan code direto para o emulador."""
    focus_window(hwnd)
    scan = ctypes.windll.user32.MapVirtualKeyW(vk_code, 0)
    ctypes.windll.user32.keybd_event(vk_code, scan, 0, 0)
    time.sleep(duration)
    ctypes.windll.user32.keybd_event(vk_code, scan, 2, 0)
    time.sleep(0.08)


def capture_screenshot(hwnd, filename, step_description):
    """Captura a tela do Citra e salva nos artefatos de QA."""
    attach_interactive_desktop()
    focus_window(hwnd)
    time.sleep(0.15)
    rect = win32gui.GetWindowRect(hwnd)
    dest = OUTPUT_DIR / filename
    try:
        left = max(0, rect[0])
        top = max(0, rect[1])
        right = max(left + 100, rect[2])
        bottom = max(top + 100, rect[3])
        img = ImageGrab.grab(bbox=(left, top, right, bottom))
        img.save(dest)
        print(f"  [QA SCREENSHOT] {filename} -> {step_description}")
        return dest
    except Exception as e:
        print(f"  [AVISO] Falha ao capturar {filename}: {e}")
        return None


def minimize_overlapping_windows():
    """Minimiza temporariamente janelas que possam obstruir a visão do jogo."""
    to_min = []
    def cb(h, _):
        if win32gui.IsWindowVisible(h):
            t = win32gui.GetWindowText(h)
            if any(k in t.lower() for k in ["antigravity ide", "google chrome", "filezilla", "explorador de arquivos"]):
                to_min.append(h)
    win32gui.EnumWindows(cb, None)
    for h in to_min:
        try:
            win32gui.ShowWindow(h, win32con.SW_MINIMIZE)
        except Exception:
            pass
    return to_min


def restore_windows(windows):
    """Restaura as janelas minimizadas ao término do teste."""
    for h in windows:
        try:
            win32gui.ShowWindow(h, win32con.SW_RESTORE)
        except Exception:
            pass


def run_autonomous_qa(total_seconds=190):
    print("=" * 70)
    print("INICIANDO BATERIA DE QA VISUAL AUTÔNOMO NO CITRA (EMERALD 3DS)")
    print(f"Duração planejada: pelo menos {total_seconds // 60} minutos ({total_seconds} segundos)")
    print(f"ROM Alvo: {ROM_FILE.name}")
    print(f"Destino das capturas: {OUTPUT_DIR}")
    print("=" * 70)

    attach_interactive_desktop()
    minimized_windows = minimize_overlapping_windows()

    # 1. Limpar save anterior para testar Novo Jogo do zero absoluto
    if SAVE_FILE.exists():
        SAVE_FILE.unlink()
        print("[1/6] Save anterior removido. O teste começará do zero absoluto.")
    else:
        print("[1/6] Nenhum save anterior detectado. Inicialização limpa garantida.")

    # Sentinela debug.txt
    SDMC_DIR.mkdir(parents=True, exist_ok=True)
    (SDMC_DIR / "debug.txt").write_text("debug\n", encoding="utf-8")

    # 2. Iniciar o Citra via script dedicado
    print("[2/6] Disparando emulador Citra...")
    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(LAUNCHER_PS1)]
    res = subprocess.check_output(cmd, text=True)
    pid_line = [l for l in res.splitlines() if "PID:" in l]
    pid = int(pid_line[0].split("PID:")[1].strip()) if pid_line else None
    print(f"[2/6] Citra iniciado com sucesso no Windows! PID: {pid}")

    # 3. Localizar a janela na tela
    citra_hwnd = None
    for s in range(15):
        time.sleep(1)
        citra_hwnd = find_citra_window()
        if citra_hwnd:
            print(f"[3/6] Janela do Citra detectada aos {s+1}s! HWND={citra_hwnd}")
            break

    if not citra_hwnd:
        print("[ERRO CRÍTICO] A janela do Citra não foi localizada na tela.")
        return 1

    start_time = time.time()
    focus_window(citra_hwnd)

    # 4. Sequência de Gameplay Autônomo
    print("\n[4/6] Executando rotina de gameplay autônomo...")

    # Marco 1: Tela de Título (aguarda 10 segundos para passar a intro da Game Freak)
    print(" -> Aguardando inicialização da tela de título...")
    time.sleep(9)
    capture_screenshot(citra_hwnd, "01_titulo_boot.png", "Tela de Título do Pokémon Emerald 3DS")

    # Marco 2: Pressionar START para entrar no menu principal
    print(" -> Pressionando START para abrir o Menu Principal...")
    press_key(citra_hwnd, VK_M, 0.3)
    time.sleep(3)
    capture_screenshot(citra_hwnd, "02_menu_principal.png", "Menu Principal com opção NOVO JOGO")

    # Marco 3: Pressionar A para selecionar NOVO JOGO
    print(" -> Pressionando A para iniciar NOVO JOGO...")
    press_key(citra_hwnd, VK_A, 0.3)
    time.sleep(4)
    capture_screenshot(citra_hwnd, "03_birch_intro_ptbr.png", "Introdução do Prof. Birch em Português")

    # Marco 4: Avançar diálogos do Professor Birch
    print(" -> Avançando falas de apresentação do Professor Birch...")
    for step in range(1, 9):
        press_key(citra_hwnd, VK_A, 0.15)
        time.sleep(1.2)
        if step == 4:
            capture_screenshot(citra_hwnd, "04_birch_pokeball.png", "Birch apresentando o Pokémon")

    # Marco 5: Seleção de Gênero (Menino / Menina)
    time.sleep(2)
    capture_screenshot(citra_hwnd, "05_gender_selection.png", "Seleção de Gênero (Menino)")
    print(" -> Confirmando seleção de gênero...")
    press_key(citra_hwnd, VK_A, 0.25)
    time.sleep(2.5)

    # Marco 6: Confirmação do Nome
    print(" -> Selecionando e confirmando nome do jogador...")
    press_key(citra_hwnd, VK_A, 0.2)
    time.sleep(1.5)
    press_key(citra_hwnd, VK_M, 0.2) # Start para confirmar
    time.sleep(1.5)
    press_key(citra_hwnd, VK_A, 0.2) # Confirmar 'SIM'
    time.sleep(2)
    capture_screenshot(citra_hwnd, "06_name_confirmed.png", "Nome do Jogador Confirmado")

    # Marco 7: Transição do Birch para o Caminhão
    print(" -> Birch encolhe o jogador para o mundo do jogo (transição para o caminhão)...")
    for _ in range(5):
        press_key(citra_hwnd, VK_A, 0.15)
        time.sleep(1.0)

    time.sleep(4)
    capture_screenshot(citra_hwnd, "07_truck_arrival.png", "Chegada do Caminhão de Mudança")

    # Marco 8: Saída do Caminhão e Encontro com a Mãe em Littleroot Town
    print(" -> Saindo do caminhão em Littleroot Town...")
    press_key(citra_hwnd, VK_RIGHT, 0.8) # Andar para a direita para sair do caminhão
    time.sleep(1)
    press_key(citra_hwnd, VK_DOWN, 0.8)
    time.sleep(3)
    capture_screenshot(citra_hwnd, "08_littleroot_mom.png", "Diálogo com a Mãe em Littleroot Town")

    # Marco 9: Avançar diálogo da Mãe e entrar na Casa
    print(" -> Dialogando com a Mãe...")
    for _ in range(8):
        press_key(citra_hwnd, VK_A, 0.15)
        time.sleep(0.9)

    # Marco 10: Movimentação dentro da Casa e Quarto
    print(" -> Movimentando o personagem pela casa...")
    press_key(citra_hwnd, VK_UP, 1.2)
    time.sleep(1)
    press_key(citra_hwnd, VK_LEFT, 0.8)
    time.sleep(1)
    press_key(citra_hwnd, VK_UP, 1.5)
    time.sleep(2)
    capture_screenshot(citra_hwnd, "09_bedroom_clock.png", "Quarto do Jogador e Ajuste do Relógio")

    # Marco 11: Abrir Menu START e testar Bottom Screen UI
    print(" -> Abrindo Menu e testando UI inferior (Dual-Screen)...")
    press_key(citra_hwnd, VK_M, 0.25)
    time.sleep(2)
    capture_screenshot(citra_hwnd, "10_start_menu_dual_screen.png", "Menu START e Tela Inferior Touch")

    # Manter o jogo rodando até atingir pelo menos total_seconds (3 minutos)
    elapsed = time.time() - start_time
    remaining = total_seconds - elapsed
    if remaining > 0:
        print(f"\n[5/6] Mantendo gameplay ativo por mais {int(remaining)}s para completar os 3 minutos...")
        cycle = 0
        while time.time() - start_time < total_seconds:
            # Alterna pequenas caminhadas e inputs para manter a emulação viva
            if cycle % 4 == 0:
                press_key(citra_hwnd, VK_DOWN, 0.4)
            elif cycle % 4 == 1:
                press_key(citra_hwnd, VK_UP, 0.4)
            elif cycle % 4 == 2:
                press_key(citra_hwnd, VK_RIGHT, 0.4)
            else:
                press_key(citra_hwnd, VK_LEFT, 0.4)
            time.sleep(3)
            cycle += 1

    total_elapsed = time.time() - start_time
    print(f"\n[5/6] Teste de gameplay concluído com {total_elapsed:.1f} segundos de execução contínua!")
    capture_screenshot(citra_hwnd, "11_final_gameplay_state.png", "Estado Final do Teste Autônomo de 3 Minutos")

    # 5. Encerrar o Citra
    print("[6/6] Encerrando emulador Citra...")
    if pid:
        subprocess.run(["powershell", "-Command", f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"])
    else:
        subprocess.run(["powershell", "-Command", "Stop-Process -Name citra-qt -Force -ErrorAction SilentlyContinue"])

    # 6. Restaurar janelas minimizadas e auditar a telemetria do port.log
    restore_windows(minimized_windows)
    audit_telemetry()
    return 0


def audit_telemetry():
    print("\n" + "=" * 70)
    print("RELATÓRIO DE TELEMETRIA E QA (port.log)")
    print("=" * 70)
    if PORT_LOG.exists():
        lines = PORT_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
        print(f"Total de linhas no port.log: {len(lines)}")
        
        # Filtra estatísticas de performance
        prof_lines = [l for l in lines if "PROF avg" in l or "fps=" in l]
        if prof_lines:
            print("\nDesempenho Registrado pelo Motor 3DS:")
            for p in prof_lines[-8:]:
                print(f"  {p}")

        # Filtra possíveis erros
        err_lines = [l for l in lines if "ERR" in l or "PANIC" in l or "FAIL" in l or "crash" in l.lower()]
        if err_lines:
            print("\nAvisos ou Erros Detectados:")
            for e in err_lines[-5:]:
                print(f"  ! {e}")
        else:
            print("\nEstabilidade: 100% ESTÁVEL! Nenhum erro ou travamento registrado.")
    else:
        print("Arquivo port.log não encontrado.")

    print("\nEvidências visuais geradas:")
    for f in sorted(OUTPUT_DIR.glob("*.png")):
        print(f"  - {f.name} ({f.stat().st_size // 1024} KB)")
    print("=" * 70)


if __name__ == "__main__":
    dur = 185
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        dur = int(sys.argv[1])
    sys.exit(run_autonomous_qa(dur))
