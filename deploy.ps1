Compress-Archive -Path .\dist\main -Destination .\dist\disabilitydude.zip -Force
try {
    aws s3 cp .\dist\disabilitydude.zip s3://prestonneal.com/apps/disabilitydude.zip --profile me --acl=public-read
} catch {
    Write-Host "Upload to S3 failed. Do you have AWS CLI installed and configured?"
}