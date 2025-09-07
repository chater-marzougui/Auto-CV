import os
import tempfile
import subprocess
import shutil
import PyPDF2
from typing import List, Dict, Any
from app.models.project import CoverLetterRequest
from app.services.gemini_service import GeminiService

class CoverLetterGenerator:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = "output"
        self.templates_dir = "templates"
        
        # Create directories if they don't exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Initialize Gemini service
        self.gemini_service = GeminiService()
    
    def generate_cover_letter(self, request: CoverLetterRequest) -> str:
        """
        Generate cover letter PDF using Gemini AI
        """
        try:
            # Extract text from template PDF
            template_path = request.template_path or os.path.join(self.templates_dir, "cover_letter_template.pdf")
            template_text = self._extract_text_from_pdf(template_path)
            # Generate cover letter content using Gemini
            cover_letter_content, company = self.gemini_service.generate_cover_letter(
                template_text=template_text,
                job_description=request.job_description,
                projects=request.matched_projects,
            )
            
            # Create LaTeX content with the generated text
            latex_content = self._create_latex_document(cover_letter_content)
            
            # Generate PDF
            pdf_path = self._compile_latex(latex_content, f"cover_letter_{company}")
            return pdf_path

        except Exception as e:
            raise RuntimeError(f"Error generating cover letter: {str(e)}")

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from PDF template
        """
        try:
            return pdf_path
            
        except Exception as e:
            raise RuntimeError(f"Error generating cover letter: {str(e)}")

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from PDF template
        """
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"Template PDF not found: {pdf_path}")
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            return text.strip()
        
        except Exception as e:
            raise RuntimeError(f"Error extracting text from PDF: {str(e)}")
    
    def _create_latex_document(self, content: str) -> str:
        """
        Create LaTeX document with generated content
        """
        latex_template = r"""
\documentclass[11pt,a4paper]{letter}
\usepackage[utf8]{inputenc}
\usepackage[margin=1in]{geometry}
\usepackage{parskip}

\begin{document}

\begin{letter}{}

""" + content + r"""

\end{letter}
\end{document}
"""
        return latex_template
    
    def _compile_latex(self, latex_content: str, filename_prefix: str) -> str:
        """
        Compile LaTeX content to PDF
        """
        try:
            # Check if pdflatex is available
            if not shutil.which('pdflatex'):
                raise RuntimeError("pdflatex not found. Please install LaTeX (e.g., texlive-latex-base)")
            
            # Write LaTeX content to temporary file
            tex_file = os.path.join(self.temp_dir, f"{filename_prefix}.tex")
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            # Compile with pdflatex (run twice for references)
            for _ in range(2):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', '-output-directory', self.temp_dir, tex_file],
                    capture_output=True,
                    text=True,
                    cwd=self.temp_dir
                )
                
                if result.returncode != 0:
                    raise RuntimeError(f"LaTeX compilation failed: {result.stderr}")
            
            # Move PDF to output directory
            temp_pdf = os.path.join(self.temp_dir, f"{filename_prefix}.pdf")
            if not os.path.exists(temp_pdf):
                raise RuntimeError("PDF was not generated")
            
            output_pdf = os.path.join(self.output_dir, f"{filename_prefix}_{hash(latex_content)}.pdf")
            shutil.copy2(temp_pdf, output_pdf)
            
            return output_pdf
                
        except Exception as e:
            raise RuntimeError(f"LaTeX compilation error: {str(e)}")
    
    def __del__(self):
        """
        Cleanup temporary directory
        """
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass