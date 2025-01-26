**DISCLAIMER**: Sometimes Windows defender doesn't let you download the app and the executable get's falsely flagged as malware. I'm working to get this fixed.
As a temporary fix, you can temporarily disable real-time-protection before installing. After the installation it should work fine.

<div align = center>

# 🖨️ PDF Tools App 🖨️

**A local, offline and more simple imitation of [iLovePDF](https://www.ilovepdf.com/)**

<p align="center">
  <img src="./media/app.png" alt="App Demo" width="50%">
</p>

![Badge Workflow]
[![Badge License]][License]
![Badge Language]
[![Badge Pull Requests]][Pull Requests]
[![Badge Issues]][Issues]

<br>

</div>

# Contents

- [📖 Description](#-description)
- [🚀 Quick Start](#-quick-start)
- [✨ Features](#-features)
- [🖼️ Screenshots](#%EF%B8%8F-screenshots)
- [📦 Installation](#-installation)
- [🗑️ Uninstall](#%EF%B8%8F-uninstall)
- [💻 Development / Run without installing](#-development--run-without-installing)
- [🏗️ Build from source](#%EF%B8%8F-build-from-source)
- [👥 Contributing](#-contributing)

# 📖 Description

💻 **Windows, Linux and Mac compatible.** 💻

The PDF Tools App is a simple, offline and local and cross-platform desktop application that allows you to manipulate PDF files. Built with `Tkinter` for GUI and `PyMuPDF` for fast PDF processing, this app currently supports Windows, macOS, and Linux. So you don't have to upload your PDF files to the web.

**Basically, an app that you can install locally on your system similar to [iLovePDF](https://www.ilovepdf.com/), but works offline and is much simpler.**

# 🚀 Quick Start

Download the latest release from the [**releases**](https://github.com/P-ict0/pdf-tools-app/releases).

(More info at [INSTALL.md](./INSTALL.md))

# ✨ Features

Right now, the app supports the following features:

- **PDF Merger**: Merge multiple PDF files into a single PDF file.
- **PDF Encryptor/Decryptor**: Encrypt or decrypt a PDF file with a password.
- **PDF Compressor**: Compress your PDFs.

# 🖼️ Screenshots

For screenshots of all the tools a look at [DEMO.md](./DEMO.md)

# 📦 Installation

For OS-specific installation instructions, please refer to the [INSTALL.md](./INSTALL.md) file.

You can also clone the repository and run the app locally.

# 🗑️ Uninstall

Refer to the [INSTALL.md](./INSTALL.md) file for OS-specific uninstallation instructions.

# 💻 Development / Run without installing

1. **Clone the repository**:

   ```bash
   git clone https://github.com/P-ict0/pdf-tools-app.git
   cd pdf-tools-app
   ```

2. **Install dependencies**: (You might want to use a virtual environment)

   ```bash
   pip install -r requirements.txt
   ```

3. **Run**:
   ```bash
   python src/main.py
   ```

# 🏗️ Build from source

To build from source:

1. Basic requirements and PyInstaller
```bash
git clone https://github.com/P-ict0/pdf-tools-app.git; cd pdf-tools-app

# Create venv and activate
python3 -m venv .venv
source ./.venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1

# Requirements
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Create executable (You might want to change --icon path: Windows/Linux uses `.ico` and MacOS uses `.icns`)
pyinstaller --windowed --onedir --name pdf_tools --icon ./media/icons/pdf.ico --add-data "VERSION:." ./src/main.py
```

2. OS-specific (Now follow instructions for your OS)

**(WINDOWS ONLY) Create app installer:**
```PowerShell
# Might need Admin terminal for this
choco install innosetup --no-progress -y

# Compile
$VERSION = $(type .\VERSION)
iscc installers/windows_setup.iss /DMyAppVersion=$VERSION

# This will create a pdf_tools_setup.exe file to install the app
```

**(MacOS ONLY): Create app**
```shell
brew install create-dmg
mkdir -p dist/AppBundle
cp -R "dist/pdf_tools.app" dist/AppBundle/
create-dmg \
  --volname "PDF Tools Installer" \
  --volicon "./media/icons/pdf.icns" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --app-drop-link 600 185 \
  --icon "pdf_tools.app.app" 200 190 \
  "dist/pdf_tools_macos.dmg" \
  dist/AppBundle

# This will create a `dist/pdf_tools_macos.dmg` that you can then use to install
```


# 👥 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to help improve functionality, design, or cross-platform compatibility.

<!----------------------------------------------------------------------------->

[Pull Requests]: https://github.com/P-ict0/pdf-tools-app/pulls
[Issues]: https://github.com/P-ict0/pdf-tools-app/issues
[License]: LICENSE

<!----------------------------------{ Badges }--------------------------------->

[Badge Workflow]: https://github.com/P-ict0/pdf-tools-app/actions/workflows/build.yml/badge.svg
[Badge Issues]: https://img.shields.io/github/issues/P-ict0/pdf-tools-app
[Badge Pull Requests]: https://img.shields.io/github/issues-pr/P-ict0/pdf-tools-app
[Badge Language]: https://img.shields.io/github/languages/top/P-ict0/pdf-tools-app
[Badge License]: https://img.shields.io/github/license/P-ict0/pdf-tools-app
[Badge Lines]: https://img.shields.io/tokei/lines/github/P-ict0/pdf-tools-app
