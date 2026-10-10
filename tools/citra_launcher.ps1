$citra = 'E:\# Video-games, Jogos e Emuladores\# Emuladores\Citra\citra-qt.exe'
$rom = 'd:\Projetos\pokeemerald-3Ds-dualscreen\dist_3ds\emerald3ds.3dsx'

# Remove save anterior para começar com New Game 100% limpo
$save = "C:\Users\rapha\AppData\Roaming\Citra\sdmc\3ds\emerald3ds\emerald3ds.sav"
if (Test-Path $save) {
    Remove-Item $save -Force
    Write-Host "Save anterior removido para teste limpo."
}

Write-Host "Iniciando Citra via launcher .ps1..."
$p = Start-Process -FilePath $citra -ArgumentList "`"$rom`"" -PassThru
Write-Host "PID:$($p.Id)"
