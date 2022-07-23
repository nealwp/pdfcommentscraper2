$release = Get-Date -UFormat "%Y-%m-%dT%T"
$hash = (git rev-parse --short HEAD)
$archive = "disabilitydude-$hash.zip"

Get-Content ".\config\config.ini" | ForEach-Object {
    $_ -replace "release = .*","release = $release"
} | Set-Content ".\config\config.tmp"

Remove-Item -Path '.\config\config.ini'
Rename-Item -Path '.\config\config.tmp' -NewName 'config.ini'

pyinstaller `
    --noconfirm --onedir --windowed `
    --distpath ".\dist" `
    --add-data "./config;config/" `
    --add-data "./install.bat;install.bat" `
    "./main.py"

$ProgressPreference = 'SilentlyContinue'
Compress-Archive -Path .\dist\main -Destination ".\dist\$archive" -Force

try {
    aws s3 cp ".\dist\$archive" "s3://prestonneal.com/apps/$archive" --acl=public-read
    
    $body = @{
        "version"="0.0.0";
        "release_date"="$release";
        "hash"="$hash";
        "url"="https://s3.amazonaws.com/prestonneal.com/apps/$archive"
    }
    
    Invoke-WebRequest -Uri "https://prestonneal.com/v1/apps/disabilitydude" `
        -Method POST `
        -Body $body
        
} catch {
    Write-Host "Upload to S3 failed. Do you have AWS CLI installed and configured?"
}

