$release = Get-Date -UFormat "%Y-%m-%dT%T"
$hash = (git rev-parse --short HEAD)
$archive = "disabilitydude-$hash.zip"

pyinstaller `
    --name 'disabilitydude' `
    --noconfirm --onedir --windowed `
    --distpath ".\dist" `
    --add-data "./config;config/" `
    "./src/main.py"

$ProgressPreference = 'SilentlyContinue'
Compress-Archive -Path .\dist\disabilitydude -Destination ".\dist\$archive" -Force
