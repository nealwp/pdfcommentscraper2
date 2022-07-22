param ($IncludeOCR)

if ($IncludeOCR) {
    pyinstaller `
    --noconfirm --onedir --windowed `
    --distpath ".\dist" `
    --add-data "./config;config/" `
    --add-data "./lib;lib/" `
    --add-data "./install.bat;install.bat" `
    "./main.py"
} else {
    pyinstaller `
    --noconfirm --onedir --windowed `
    --distpath ".\dist" `
    --add-data "./config;config/" `
    --add-data "./install.bat;install.bat" `
    "./main.py"
}



