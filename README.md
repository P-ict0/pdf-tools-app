# 🖨️ PDF Merger App 🖨️

# Contents

- [📖 Description](#-description)
- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [⚙️ Run from source](#️-run-from-source)
- [💻 Development](#-development)
- [👥 Contributing](#-contributing)

# 📖 Description

💻 **Windows, Linux and Mac compatible.** 💻

The PDF Merger App is a simple, local and cross-platform desktop application that allows you to combine multiple PDF files into a single document. Built with `Tkinter` for GUI and `PyPDF2` for PDF processing, this app currently supports Windows, macOS, and Linux.

![App Demo](./media/app.png)

# ✨ Features

- **PDF Selection**: Add PDFs and see them in a preview list.
- **File Reordering**: Reorder files before merging.
- **Cross-Platform**: Works on Windows, macOS, and Linux.

# 📦 Installation

In the [**releases**](https://github.com/P-ict0/pdf-merger-app/releases) tab, you will find the executable for the app. Then you can run them directly.

If you prefer to run from source, continue reading.

# ⚙️ Run from source

If you want to run from source:

```bash
# Clone
git clone https://github.com/P-ict0/pdf-merger-app.git
cd pdf-merger-app

# (recommended) Set up a virtual environment
python3 -m venv ./venv
# Activate
source ./venv/bin/activate # For linux (Different for Windows and Mac)

# Requirements and run
pip install --upgrade pip
pip install -r requirements.txt
python src/app.py
```

To build the app into an executable, you can use Pyinstaller

# 💻 Development

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/pdf-merger-app.git
   cd pdf-merger-app
   ```

2. **Install dependencies**: (You might want to use a virtual environment)

   ```bash
   pip install -r requirements.txt
   ```

3. **Run**:
   ```bash
   python src/app.py
   ```

# 👥 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to help improve functionality, design, or cross-platform compatibility.
