# 📦 Installation instructions

# Contents

- [📦 Install](#-install)
  - [Windows](#windows)
  - [MacOS](#macos)
  - [Linux](#linux)
- [🗑️ Uninstall](#-uninstall)
  - [Windows](#windows-1)
  - [MacOS](#macos-1)
  - [Linux](#linux-1)

<hr>

# 📦 Install

## Windows

1. Download `pdf_tools_setup.exe` from [**releases**](https://github.com/P-ict0/pdf-tools-app/releases).
2. Run the installer. (Windows Defender might block the installation. Click on "More info" and then "Run anyway".)
3. The app will be installed in `C:\Program Files\PDF Tools`.

## MacOS

1. Download `pdf_tools_macos.dmg` from [**releases**](https://github.com/P-ict0/pdf-tools-app/releases).
2. Open the `.dmg` file.
3. MacOS might block the installation. Go to `System Preferences` -> `Security & Privacy` -> `General` -> Click on `Open Anyway` (at the bottom of the page).
4. Drag the app to the `Applications` folder.

## Linux

1. Download `pdf_tools_linux` from [**releases**](https://github.com/P-ict0/pdf-tools-app/releases).
2. Give execute permission to the file.
   ```bash
   chmod +x pdf_tools_linux
   ```
3. (Optional) Add the executable to your PATH. To be able to run the app from anywhere.
   ```bash
   sudo mv pdf_tools_linux /usr/local/bin/pdf_tools
   ```

# 🗑️ Uninstall

## Windows

1. Go to `Control Panel` -> `Programs` -> `Programs and Features`.
2. Find `PDF Tools` in the list and click on `Uninstall`.

## MacOS

1. Go to `Applications` folder.
2. Right-click on `PDF Tools` and click on `Move to Trash`.

## Linux

1. Delete the executable.
   ```bash
   sudo rm /usr/local/bin/pdf_tools
   ```
