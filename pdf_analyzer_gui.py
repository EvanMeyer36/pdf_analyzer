import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import subprocess
import sys
import os
from pathlib import Path
import threading
import json
import pkg_resources
import platform

class DependencyManager:
    @staticmethod
    def is_mac():
        return platform.system() == 'Darwin'

    @staticmethod
    def is_windows():
        return platform.system() == 'Windows'
    @staticmethod
    def get_poppler_path():
        """Get the appropriate Poppler path for the current platform"""
        if DependencyManager.is_mac():
            # Check common Homebrew installation paths
            poppler_paths = [
                "/opt/homebrew/bin",
                "/usr/local/bin",
                "/opt/homebrew/Cellar/poppler/*/bin",
                "/usr/local/Cellar/poppler/*/bin"
            ]
            
            # Expand glob patterns and check each path
            expanded_paths = []
            for path in poppler_paths:
                if '*' in path:
                    import glob
                    expanded_paths.extend(glob.glob(path))
                else:
                    expanded_paths.append(path)
            
            # Return the first valid path that contains pdftotext
            for path in expanded_paths:
                if os.path.exists(os.path.join(path, 'pdftotext')):
                    return path
            
            return None
        elif DependencyManager.is_windows():
            return r"C:\Program Files\Poppler\Library\bin"
        return None
    
    @staticmethod
    def find_brew():
        """Find the correct path to Homebrew"""
        homebrew_paths = ["/opt/homebrew/bin/brew", "/usr/local/bin/brew"]
        for path in homebrew_paths:
            if Path(path).exists():
                return path
        return None

    @staticmethod
    def install_mac_dependencies():
        """Install required dependencies on macOS using Homebrew"""
        brew_path = DependencyManager.find_brew()
        if not brew_path:
            msg = ("Homebrew is not installed. Please install it first:\n"
                   "/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"\n")
            messagebox.showerror("Homebrew Required", msg)
            return False

        try:
            subprocess.run([brew_path, "update"], check=True)
            return True
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to update Homebrew: {str(e)}")
            return False
        
    @staticmethod
    def setup_windows_poppler():
        """Guide user through Windows Poppler setup"""
        instructions = """
To install Poppler on Windows:

1. Download latest Poppler from:
   https://github.com/oschwartz10612/poppler-windows/releases/

2. Extract the zip to:
   C:\\Program Files\\Poppler

3. Add to System PATH:
   C:\\Program Files\\Poppler\\Library\\bin

4. Restart your computer
"""
        messagebox.showinfo("Windows Installation Instructions", instructions)
        return False

    @staticmethod
    def verify_installation():
        """Verify all required dependencies are installed"""
        if DependencyManager.is_mac():
            try:
                subprocess.run(['tesseract', '--version'], check=True, capture_output=True)
                subprocess.run(['pdftotext', '--version'], check=True, capture_output=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False
        else:  # Windows
            try:
                tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
                poppler_path = r"C:\Program Files\Poppler\Library\bin\pdftotext.exe"
                
                subprocess.run([tesseract_path, '--version'], check=True, capture_output=True)
                subprocess.run([poppler_path, '--version'], check=True, capture_output=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False
            
class PDFAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Document Analyzer")
        self.root.geometry("1000x800")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'))
        self.style.configure('Status.TLabel', font=('Helvetica', 10))
        self.style.configure('Action.TButton', padding=10)
        
        # Set up config directory
        self.config_dir = self.get_config_directory()
        self.config_file = os.path.join(self.config_dir, 'pdf_analyzer_config.json')
        os.makedirs(self.config_dir, exist_ok=True)

        # Create main container with padding
        self.container = ttk.Frame(root, padding="20")
        self.container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive layout
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)
        
        # Header
        header = ttk.Label(self.container, text="PDF Document Analyzer", style='Header.TLabel')
        header.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)
        
        # Create sections with visual separation
        self.create_api_section()
        self.create_file_section()
        self.create_summary_section()
        self.create_qa_section()
        self.create_status_section()
        
        # Store the current summary
        self.current_summary = ""
        
        # Load saved API key
        self.load_api_key()
        
        # Check dependencies
        if not DependencyManager.verify_installation():
            if DependencyManager.is_mac():
                if not DependencyManager.install_mac_dependencies():
                    root.destroy()
                    return
            else:
                if not DependencyManager.setup_windows_poppler():
                    root.destroy()
                    return

    def create_api_section(self):
        # API Key Section
        api_frame = ttk.LabelFrame(self.container, text="OpenAI API Configuration", padding="10")
        api_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        api_frame.columnconfigure(0, weight=1)
        
        self.api_key_var = tk.StringVar()
        key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, show="*", width=60)
        key_entry.grid(row=0, column=0, padx=(5, 10), sticky=(tk.W, tk.E))
        
        save_btn = ttk.Button(api_frame, text="Save API Key", command=self.save_api_key, style='Action.TButton')
        save_btn.grid(row=0, column=1, padx=5)

    def create_file_section(self):
        # File Selection Section
        file_frame = ttk.LabelFrame(self.container, text="Document Selection", padding="10")
        file_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(0, weight=1)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=60)
        file_entry.grid(row=0, column=0, padx=(5, 10), sticky=(tk.W, tk.E))
        
        browse_btn = ttk.Button(file_frame, text="Browse PDF", command=self.browse_file, style='Action.TButton')
        browse_btn.grid(row=0, column=1, padx=5)
        
        analyze_btn = ttk.Button(file_frame, text="▶ Analyze Document", command=self.analyze_pdf, style='Action.TButton')
        analyze_btn.grid(row=0, column=2, padx=5)

    def create_summary_section(self):
        # Summary Section
        summary_frame = ttk.LabelFrame(self.container, text="Document Summary", padding="10")
        summary_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.rowconfigure(0, weight=1)
        
        self.summary_text = scrolledtext.ScrolledText(
            summary_frame, 
            wrap=tk.WORD, 
            width=70, 
            height=12,
            font=('Helvetica', 11)
        )
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)

    def create_qa_section(self):
        # Q&A Section
        qa_frame = ttk.LabelFrame(self.container, text="Ask Questions About the Document", padding="10")
        qa_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        qa_frame.columnconfigure(0, weight=1)
        
        # Question input area
        input_frame = ttk.Frame(qa_frame)
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        self.question_var = tk.StringVar()
        question_entry = ttk.Entry(input_frame, textvariable=self.question_var, width=60)
        question_entry.grid(row=0, column=0, padx=(5, 10), sticky=(tk.W, tk.E))
        
        ask_btn = ttk.Button(input_frame, text="Ask Question", command=self.ask_question, style='Action.TButton')
        ask_btn.grid(row=0, column=1, padx=5)
        
        # Q&A display area
        self.qa_output = scrolledtext.ScrolledText(
            qa_frame, 
            wrap=tk.WORD, 
            width=70, 
            height=8,
            font=('Helvetica', 11)
        )
        self.qa_output.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)

    def create_status_section(self):
        # Status Section
        status_frame = ttk.Frame(self.container, padding="5")
        status_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            status_frame, 
            variable=self.progress_var, 
            maximum=100,
            length=300
        )
        self.progress.grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            status_frame, 
            textvariable=self.status_var,
            style='Status.TLabel'
        )
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        
        # Clear button
        clear_btn = ttk.Button(
            status_frame, 
            text="Clear All", 
            command=self.clear_all,
            style='Action.TButton'
        )
        clear_btn.grid(row=0, column=2, padx=(10, 0), sticky=tk.E)

        # Store the current summary
        self.current_summary = ""
        
        # Load saved API key
        self.load_api_key()

    def get_config_directory(self):
        """Get the appropriate configuration directory for the current platform."""
        if platform.system() == 'Darwin':  # macOS
            return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'PDFAnalyzer')
        elif platform.system() == 'Windows':
            return os.path.join(os.getenv('APPDATA'), 'PDFAnalyzer')
        else:  # Linux and others
            return os.path.join(os.path.expanduser('~'), '.config', 'pdfanalyzer')
    
    def save_api_key(self):
        try:
            config = {'api_key': self.api_key_var.get()}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            messagebox.showinfo("Success", "API key saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API key: {str(e)}")
    
    def load_api_key(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.api_key_var.set(config.get('api_key', ''))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load API key: {str(e)}")



    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf")]
        )
        if filename:
            self.file_path_var.set(filename)
    
    def clear_all(self):
        self.summary_text.delete(1.0, tk.END)
        self.qa_output.delete(1.0, tk.END)
        self.question_var.set("")
        self.progress_var.set(0)
        self.status_var.set("")
        self.current_summary = ""
    
    def analyze_pdf(self):
        if not self.api_key_var.get():
            messagebox.showerror("Error", "Please enter your OpenAI API key.")
            return
        
        if not self.file_path_var.get():
            messagebox.showerror("Error", "Please select a PDF file.")
            return
        
        threading.Thread(target=self._run_analysis, daemon=True).start()
    
    def _run_analysis(self):
        try:
            import openai
            from pdf2image import convert_from_path
            import pytesseract
            
            self.progress_var.set(20)
            self.status_var.set("Converting PDF to images...")
            
            pdf_path = self.file_path_var.get()
            
            # Get platform-specific Poppler path
            poppler_path = DependencyManager.get_poppler_path()
            if not poppler_path:
                raise Exception("Poppler not found. Please ensure it's installed and in PATH.")
            
            # Set environment variables for subprocess calls
            os.environ["PATH"] = f"{poppler_path}:{os.environ.get('PATH', '')}"
            
            # Convert PDF to images with explicit poppler path
            images = convert_from_path(
                pdf_path,
                poppler_path=poppler_path
            )
            
            # Handle platform-specific Poppler path
            if DependencyManager.is_windows():
                poppler_path = r"C:\Program Files\Poppler\Library\bin"
                images = convert_from_path(pdf_path, poppler_path=poppler_path)
            else:
                images = convert_from_path(pdf_path)
            
            self.status_var.set("Performing OCR...")
            text = []
            for i, image in enumerate(images):
                self.progress_var.set(20 + (40 * (i + 1) / len(images)))
                image = image.convert('L')
                text.append(pytesseract.image_to_string(image))
            
            extracted_text = "\n".join(text)
            
            self.status_var.set("Generating summary...")
            self.progress_var.set(70)
            
            openai.api_key = self.api_key_var.get()
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a precise and thorough document summarizer."},
                    {"role": "user", "content": f"Please provide a comprehensive summary of this text:\n\n{extracted_text[:3000]}"}
                ],
                temperature=0.7
            )
            
            summary = response.choices[0].message.content
            self.current_summary = summary
            
            self.root.after(0, lambda: self.summary_text.delete(1.0, tk.END))
            self.root.after(0, lambda: self.summary_text.insert(tk.END, summary))
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.status_var.set("Analysis complete!"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("Analysis failed."))
    
    def ask_question(self):
        if not self.current_summary:
            messagebox.showerror("Error", "Please analyze a PDF first.")
            return
        
        question = self.question_var.get()
        if not question:
            messagebox.showerror("Error", "Please enter a question.")
            return
        
        threading.Thread(target=self._process_question, args=(question,), daemon=True).start()
    
    def _process_question(self, question):
        try:
            import openai
            
            openai.api_key = self.api_key_var.get()
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable assistant answering questions based on a document summary."},
                    {"role": "user", "content": f"Context summary:\n{self.current_summary}\n\nQuestion: {question}"}
                ],
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            self.root.after(0, lambda: self.qa_output.insert(tk.END, f"Q: {question}\nA: {answer}\n\n"))
            self.root.after(0, lambda: self.question_var.set(""))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))

def main():
    root = tk.Tk()
    app = PDFAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    try:
        def main():
            root = tk.Tk()
            app = PDFAnalyzerGUI(root)
            root.mainloop()

        main()
    except Exception as e:
        messagebox.showerror("Critical Error", f"An unexpected error occurred: {str(e)}")
        sys.exit(1)