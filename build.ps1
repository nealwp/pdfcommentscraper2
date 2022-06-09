pyinstaller `
    --noconfirm --onedir --windowed `
    --distpath "D:\source\pdfcommentscraper2\dist" `
    --add-data "D:/source/pdfcommentscraper2/config;config/" `
    --add-data "D:/source/pdfcommentscraper2/lib;lib/" `
    "D:/source/pdfcommentscraper2/main.py"
