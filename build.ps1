param ($IncludeOCR)

if ($IncludeOCR) {
    pyinstaller `
    --noconfirm --onedir --windowed `
    --distpath ".\dist" `
    --add-data "./config;config/" `
    --add-data "./lib;lib/" `
    "./main.py"
} else {
    pyinstaller `
    --noconfirm --onedir --windowed `
    --distpath ".\dist" `
    --add-data "./config;config/" `
    "./main.py"
}



