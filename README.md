# PDF Combiner

A simple and user-friendly web application to combine multiple PDF files into one. Built with Python Flask and a clean, modern UI.

## Features

- 📄 **Multiple PDF Upload**: Upload 2 or more PDF files
- ✏️ **Custom Filename**: Rename the combined output file
- 🎨 **User-Friendly Interface**: Clean, modern design with drag-and-drop support
- ⬇️ **Instant Download**: Download the combined PDF directly to your system
- 🔒 **Secure**: File validation and secure filename handling

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mihirsangani/pdf-combiner.git
cd pdf-combiner
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Use the application:
   - Click on the upload area or drag and drop multiple PDF files
   - Enter a custom name for the combined PDF (optional)
   - Click "Combine PDFs" button
   - The combined PDF will be automatically downloaded to your system

## How It Works

The application consists of:
- **Backend (app.py)**: Flask web server that handles file uploads and PDF combining using pypdf library
- **Frontend (templates/index.html)**: Modern, responsive web interface with drag-and-drop functionality

## Technical Details

- **Backend Framework**: Flask
- **PDF Library**: pypdf (for combining PDFs)
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **File Size Limit**: 50MB per request
- **Supported Format**: PDF files only

## Security Features

- File type validation (PDF only)
- Secure filename handling
- File size limits
- Temporary file cleanup

## License

This project is open source and available for personal and commercial use.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.