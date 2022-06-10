pyinstaller `
    --noconfirm --onedir --windowed `
    --distpath ".\dist" `
    --add-data "./config;config/" `
    --add-data "./lib;lib/" `
    "./main.py"
