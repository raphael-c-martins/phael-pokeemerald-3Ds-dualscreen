param(
    [int]$TotalSeconds = 190
)

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;

public class CitraQAEngine {
    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int GetClassName(IntPtr hWnd, StringBuilder lpClassName, int nMaxCount);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

    [DllImport("user32.dll")]
    public static extern void SwitchToThisWindow(IntPtr hWnd, bool fAltTab);

    [DllImport("user32.dll")]
    public static extern uint MapVirtualKeyW(uint uCode, uint uMapType);

    [DllImport("user32.dll")]
    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, int dwExtraInfo);

    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left, Top, Right, Bottom; }

    public static IntPtr FindCitraWindow() {
        IntPtr found = IntPtr.Zero;
        EnumWindows((hWnd, lParam) => {
            if (IsWindowVisible(hWnd)) {
                StringBuilder sbTitle = new StringBuilder(256);
                GetWindowText(hWnd, sbTitle, 256);
                string title = sbTitle.ToString();

                StringBuilder sbClass = new StringBuilder(256);
                GetClassName(hWnd, sbClass, 256);
                string cls = sbClass.ToString();

                if (cls.Contains("Qt") && title.Contains("Citra") && !title.Contains("Antigravity")) {
                    RECT r;
                    GetWindowRect(hWnd, out r);
                    int w = r.Right - r.Left;
                    int h = r.Bottom - r.Top;
                    if (w > 200 && h > 200) {
                        found = hWnd;
                        return false;
                    }
                }
            }
            return true;
        }, IntPtr.Zero);
        return found;
    }

    public static RECT GetRect(IntPtr hWnd) {
        RECT r;
        GetWindowRect(hWnd, out r);
        return r;
    }

    public static void FocusAndTop(IntPtr hWnd) {
        ShowWindow(hWnd, 3); // SW_MAXIMIZE
        // Alt keypress para liberar lock de foco
        keybd_event(0x12, 0, 0, 0);
        keybd_event(0x12, 0, 2, 0);
        SetWindowPos(hWnd, new IntPtr(-1), 0, 0, 0, 0, 0x0043);
        SetForegroundWindow(hWnd);
        SwitchToThisWindow(hWnd, true);
        System.Threading.Thread.Sleep(80);
    }

    public static void PressKey(IntPtr hWnd, byte vk, int durationMs) {
        FocusAndTop(hWnd);
        uint scan = MapVirtualKeyW(vk, 0);
        keybd_event(vk, (byte)scan, 0, 0);
        System.Threading.Thread.Sleep(durationMs);
        keybd_event(vk, (byte)scan, 2, 0);
        System.Threading.Thread.Sleep(60);
    }
}
"@

$citraExe = 'E:\# Video-games, Jogos e Emuladores\# Emuladores\Citra\citra-qt.exe'
$romFile = 'd:\Projetos\pokeemerald-3Ds-dualscreen\dist_3ds\emerald3ds.3dsx'
$outputDir = 'd:\Projetos\pokeemerald-3Ds-dualscreen\# TEMPORARIO\Citra-QA'
$sdmcDir = "$env:APPDATA\Citra\sdmc\3ds\emerald3ds"
$saveFile = "$sdmcDir\emerald3ds.sav"
$portLog = "$sdmcDir\port.log"

if (!(Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir | Out-Null }
if (!(Test-Path $sdmcDir)) { New-Item -ItemType Directory -Path $sdmcDir | Out-Null }

Write-Host "======================================================================"
Write-Host 'BATERIA DE TESTES DE QA VISUAL AUTÔNOMO NO CITRA [EMERALD 3DS]'
Write-Host "Duração: $TotalSeconds segundos (pelo menos $([math]::Round($TotalSeconds/60, 1)) minutos)"
Write-Host 'Alvo: emerald3ds.3dsx [v4 + Birch Speech PT-BR + upstream v0.3.1]'
Write-Host "Destino das Evidências: $outputDir"
Write-Host "======================================================================"

# 1. Resetar save para garantir NOVO JOGO 100% limpo
if (Test-Path $saveFile) {
    Remove-Item $saveFile -Force
    Write-Host "[1/6] Save anterior removido. O teste começará do zero absoluto."
} else {
    Write-Host "[1/6] Nenhum save anterior detectado. Inicialização limpa garantida."
}

# Ativar sentinela debug.txt
Set-Content -Path "$sdmcDir\debug.txt" -Value "debug`n" -Encoding UTF8

# 2. Iniciar Citra
Write-Host "[2/6] Iniciando executável do Citra..."
$proc = Start-Process -FilePath $citraExe -ArgumentList "`"$romFile`"" -WindowStyle Maximized -PassThru
$wshell = New-Object -ComObject WScript.Shell
$wshell.AppActivate($proc.Id)
Write-Host "[2/6] Citra iniciado com sucesso no Windows! PID: $($proc.Id)"

# 3. Localizar Janela do Citra
$citraHwnd = [IntPtr]::Zero
for ($s = 1; $s -le 15; $s++) {
    Start-Sleep -Seconds 1
    $citraHwnd = [CitraQAEngine]::FindCitraWindow()
    if ($citraHwnd -ne [IntPtr]::Zero) {
        Write-Host "[3/6] Janela do Citra detectada aos $s s! HWND=$citraHwnd"
        break
    }
}

if ($citraHwnd -eq [IntPtr]::Zero) {
    Write-Host "[ERRO CRÍTICO] Janela do Citra não encontrada na tela."
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

# Função de Captura de Screenshot
function Take-Screenshot([string]$filename, [string]$description) {
    $wshell.AppActivate($proc.Id)
    [CitraQAEngine]::FocusAndTop($citraHwnd)
    Start-Sleep -Milliseconds 150
    $r = [CitraQAEngine]::GetRect($citraHwnd)
    $l = [Math]::Max(0, $r.Left)
    $t = [Math]::Max(0, $r.Top)
    $right = [Math]::Max($l + 100, $r.Right)
    $bottom = [Math]::Max($t + 100, $r.Bottom)

    $dest = Join-Path $outputDir $filename
    $capScript = "d:\Projetos\pokeemerald-3Ds-dualscreen\tools\capture_screenshot.py"
    python $capScript $l $t $right $bottom "$dest" "$description"
}

$startTime = [DateTime]::UtcNow
$wshell.AppActivate($proc.Id)
[CitraQAEngine]::FocusAndTop($citraHwnd)

# 4. Sequência Autônoma de Gameplay
Write-Host "`n[4/6] Executando rotina de gameplay autônomo..."

# Marco 1: Tela de título
Write-Host " -> Aguardando inicialização da tela de título e carregamento de assets (16s)..."
Start-Sleep -Seconds 16
Take-Screenshot "01_titulo_boot.png" "Tela de Título do Pokémon Emerald 3DS"

# Marco 2: START para entrar no menu principal
Write-Host " -> Pressionando START para abrir o Menu Principal..."
[CitraQAEngine]::PressKey($citraHwnd, 0x4D, 300) # VK_M (Start)
Start-Sleep -Seconds 3
Take-Screenshot "02_menu_principal.png" "Menu Principal com opção NOVO JOGO"

# Marco 3: A para NOVO JOGO
Write-Host " -> Pressionando A para iniciar NOVO JOGO..."
[CitraQAEngine]::PressKey($citraHwnd, 0x41, 300) # VK_A (A)
Start-Sleep -Seconds 4
Take-Screenshot "03_birch_intro_ptbr.png" "Introdução do Prof. Birch em Português"

# Marco 4: Avançar diálogos do Professor Birch
Write-Host " -> Avançando falas de apresentação do Professor Birch..."
for ($i = 1; $i -le 8; $i++) {
    [CitraQAEngine]::PressKey($citraHwnd, 0x41, 180)
    Start-Sleep -Milliseconds 1200
    if ($i -eq 4) {
        Take-Screenshot "04_birch_pokeball.png" "Birch apresentando o Pokémon"
    }
}

# Marco 5: Seleção de Gênero
Start-Sleep -Seconds 2
Take-Screenshot "05_gender_selection.png" "Seleção de Gênero (Menino)"
Write-Host " -> Confirmando seleção de gênero..."
[CitraQAEngine]::PressKey($citraHwnd, 0x41, 250)
Start-Sleep -Milliseconds 2500

# Marco 6: Confirmação de Nome
Write-Host " -> Selecionando e confirmando nome do jogador..."
[CitraQAEngine]::PressKey($citraHwnd, 0x41, 200) # Escolhe letra
Start-Sleep -Milliseconds 1200
[CitraQAEngine]::PressKey($citraHwnd, 0x4D, 250) # Start para OK
Start-Sleep -Milliseconds 1500
[CitraQAEngine]::PressKey($citraHwnd, 0x41, 200) # Confirmar 'SIM'
Start-Sleep -Seconds 2
Take-Screenshot "06_name_confirmed.png" "Nome do Jogador Confirmado"

# Marco 7: Transição para o Caminhão
Write-Host " -> Birch conclui apresentação e transiciona para o caminhão..."
for ($i = 1; $i -le 5; $i++) {
    [CitraQAEngine]::PressKey($citraHwnd, 0x41, 150)
    Start-Sleep -Milliseconds 1000
}
Start-Sleep -Seconds 4
Take-Screenshot "07_truck_arrival.png" "Chegada do Caminhão de Mudança"

# Marco 8: Saída do Caminhão e Encontro com a Mãe
Write-Host " -> Saindo do caminhão em Littleroot Town..."
[CitraQAEngine]::PressKey($citraHwnd, 0x27, 800) # Direita
Start-Sleep -Milliseconds 500
[CitraQAEngine]::PressKey($citraHwnd, 0x28, 800) # Baixo
Start-Sleep -Seconds 3
Take-Screenshot "08_littleroot_mom.png" "Diálogo com a Mãe em Littleroot Town"

# Marco 9: Avançar Diálogo da Mãe
Write-Host " -> Dialogando com a Mãe..."
for ($i = 1; $i -le 8; $i++) {
    [CitraQAEngine]::PressKey($citraHwnd, 0x41, 150)
    Start-Sleep -Milliseconds 900
}

# Marco 10: Entrar na Casa e Subir ao Quarto
Write-Host " -> Movimentando personagem pela casa..."
[CitraQAEngine]::PressKey($citraHwnd, 0x26, 1200) # Cima
Start-Sleep -Milliseconds 500
[CitraQAEngine]::PressKey($citraHwnd, 0x25, 800)  # Esquerda
Start-Sleep -Milliseconds 500
[CitraQAEngine]::PressKey($citraHwnd, 0x26, 1500) # Cima
Start-Sleep -Seconds 2
Take-Screenshot "09_bedroom_clock.png" "Quarto do Jogador e Ajuste do Relógio"

# Marco 11: Menu Start e Dual-Screen UI
Write-Host " -> Abrindo Menu START e testando tela inferior..."
[CitraQAEngine]::PressKey($citraHwnd, 0x4D, 250)
Start-Sleep -Seconds 2
Take-Screenshot "10_start_menu_dual_screen.png" "Menu START e Tela Inferior Touch"

# 5. Completar o restante dos 3 minutos em gameplay contínuo
$elapsed = ([DateTime]::UtcNow - $startTime).TotalSeconds
$remaining = $TotalSeconds - $elapsed
if ($remaining -gt 0) {
    Write-Host "`n[5/6] Mantendo gameplay ativo por mais $([int]$remaining)s para completar os 3 minutos..."
    $cycle = 0
    while (([DateTime]::UtcNow - $startTime).TotalSeconds -lt $TotalSeconds) {
        if ($cycle % 4 -eq 0) { [CitraQAEngine]::PressKey($citraHwnd, 0x28, 400) }
        elseif ($cycle % 4 -eq 1) { [CitraQAEngine]::PressKey($citraHwnd, 0x26, 400) }
        elseif ($cycle % 4 -eq 2) { [CitraQAEngine]::PressKey($citraHwnd, 0x27, 400) }
        else { [CitraQAEngine]::PressKey($citraHwnd, 0x25, 400) }
        Start-Sleep -Seconds 3
        $cycle++
    }
}

$totalElapsed = ([DateTime]::UtcNow - $startTime).TotalSeconds
Write-Host "`n[5/6] Teste de gameplay concluído com $([math]::Round($totalElapsed, 1)) segundos de execução contínua!"
Take-Screenshot "11_final_gameplay_state.png" "Estado Final do Teste Autônomo de 3 Minutos"

# 6. Encerrar Citra
Write-Host "[6/6] Encerrando emulador Citra..."
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue

# Relatório de Telemetria
Write-Host "`n======================================================================"
Write-Host "RELATÓRIO DE TELEMETRIA E QA (port.log)"
Write-Host "======================================================================"
if (Test-Path $portLog) {
    $lines = Get-Content $portLog
    Write-Host "Total de linhas no port.log: $($lines.Count)"
    Write-Host "`nDesempenho Registrado pelo Motor 3DS:"
    $lines | Where-Object { $_ -match "PROF avg" -or $_ -match "fps=" } | Select-Object -Last 8 | ForEach-Object { Write-Host "  $_" }

    $errs = $lines | Where-Object { $_ -match "err=[1-9]" -or $_ -match "PANIC" -or $_ -match "FATAL" -or $_ -match "crash" }
    if ($errs) {
        Write-Host "`nAvisos ou Erros:"
        $errs | Select-Object -Last 5 | ForEach-Object { Write-Host "  ! $_" }
    } else {
        Write-Host "`nEstabilidade: 100% ESTÁVEL! Nenhum erro ou travamento registrado no motor."
    }
}

Write-Host ("`nEvidencias visuais salvas em: " + $outputDir)
Get-ChildItem $outputDir -Filter *.png | ForEach-Object {
    $sizeKb = [math]::Round($_.Length / 1024, 0)
    Write-Host ("  - " + $_.Name + " (" + $sizeKb + " KB)")
}
Write-Host "======================================================================"
