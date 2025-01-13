# PDF Document Analyzer

A desktop application that uses OCR and AI to analyze PDF documents and provide intelligent summaries and Q&A capabilities. Built with Python and powered by OpenAI's GPT models.

![PDF Analyzer Screenshot]
[Add a screenshot of your application here]

## Features

- PDF text extraction using OCR (Optical Character Recognition)
- AI-powered document summarization
- Interactive Q&A based on document content
- Cross-platform support (Windows & macOS)
- User-friendly GUI interface
- Secure API key management
- Progress tracking for long operations

## Prerequisites

Before installing the application, ensure you have the following:

- Python 3.8 or higher
- An OpenAI API key ([Get one here](https://platform.openai.com/account/api-keys))

### System Dependencies

#### macOS
1. Install Homebrew (if not already installed):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install required system dependencies:
```bash
brew install poppler tesseract
```

#### Windows
1. Install Tesseract OCR:
   - Download the installer from the [UB Mannheim GitHub repository](https://github.com/UB-Mannheim/tesseract/wiki)
   - Run the installer and note the installation path

2. Install Poppler:
   - Download the latest release from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases/)
   - Extract to `C:\Program Files\Poppler`
   - Add `C:\Program Files\Poppler\Library\bin` to your system PATH

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pdf-analyzer.git
cd pdf-analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python pdf_analyzer_gui.py
```

2. Enter your OpenAI API key in the configuration section
3. Click "Browse PDF" to select a PDF document
4. Click "Analyze Document" to process the file
5. Once analysis is complete, you can:
   - View the AI-generated summary
   - Ask questions about the document content

## Building the Application

To create a standalone executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Create the executable
pyinstaller --onefile --windowed pdf_analyzer_gui.py
```

The executable will be created in the `dist` directory.

## Project Structure

```
pdf-analyzer/
├── pdf_analyzer_gui.py     # Main application file
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── dist/                  # Directory for compiled executables
```

## Requirements

See `requirements.txt` for a complete list of Python dependencies. Key requirements include:

- tkinter (included with Python)
- pdf2image
- pytesseract
- openai
- Pillow

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for providing the GPT API
- Tesseract OCR project
- Poppler PDF rendering library
- All other open-source contributors

## Support

If you encounter any issues or have questions, please:
1. Check the [Issues](https://github.com/yourusername/pdf-analyzer/issues) page
2. Create a new issue if your problem isn't already listed

## Authors

- Your Name - Initial work - [YourGitHub](https://github.com/yourusername)
