pyinstaller --noconfirm --onedir --windowed --distpath "D:\source\pdfcommentscraper2\dist" --add-data "D:/source/pdfcommentscraper2/config;config/"  "D:/source/pdfcommentscraper2/main.py"
Compress-Archive -Path D:\source\pdfcommentscraper2\dist\main -Destination D:\source\pdfcommentscraper2\dist\disabilitydude.zip -Force
aws s3 cp D:\source\pdfcommentscraper2\dist\disabilitydude.zip s3://prestonneal.com/apps/disabilitydude.zip --profile me --acl=public-read
