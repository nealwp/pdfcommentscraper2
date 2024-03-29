param ($IncludeOCR)

$release = Get-Date -UFormat "%Y-%m-%dT%T"
$hash = (git rev-parse --short HEAD)

Get-Content ".\config\config.ini" | ForEach-Object {
    $_ -replace "release = .*", "release = $release" `
        -replace "version = .*", "version = $hash"
} | Set-Content ".\config\config.tmp"

Remove-Item -Path '.\config\config.ini'
Rename-Item -Path '.\config\config.tmp' -NewName 'config.ini'

if ($IncludeOCR) {
    pyinstaller `
    --noconfirm --onedir --windowed `
    --distpath ".\dist" `
    --add-data "./config;config/" `
    --add-data "./lib;lib/" `
    --add-data "./install.bat;./" `
    "./main.py"
} else {
    pyinstaller `
    --name 'disabilitydude' `
    --noconfirm --onedir --windowed `
    --distpath ".\dist" `
    --add-data "./config;config/" `
    "./main.py"
}



