import os
import tempfile
import subprocess
import shutil
import PyPDF2
from app.models.project import CoverLetterRequest
from app.services.gemini_service import GeminiService

class CoverLetterGenerator:
    def __init__(self):
        self.temp_dir = "temp"
        self.output_dir = "output"
        self.templates_dir = "templates"
        
        # Create directories if they don't exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Initialize Gemini service
        self.gemini_service = GeminiService()
    
    def generate_cover_letter(self, request: CoverLetterRequest) -> str:
        """
        Generate cover letter PDF using Gemini AI
        """
        try:
            # Use a default professional template if no template PDF exists
            template_path = request.template_path or os.path.join(self.templates_dir, "cover_letter_template.pdf")
            
            if os.path.exists(template_path):
                template_text = self._extract_text_from_pdf(template_path)
            else:
                # Default professional template structure
                template_text = """
                Dear Hiring Manager,

                I am writing to express my strong interest in the [Position] role at [Company]. With my background in software development and proven track record in delivering high-quality projects, I am confident I would be a valuable addition to your team.

                In my recent projects, I have gained extensive experience with [relevant technologies]. My work has focused on [relevant domains], where I have successfully [achievements]. This experience has equipped me with the technical skills and problem-solving abilities that align perfectly with your requirements.

                What particularly excites me about this opportunity is [company/role specific interest]. I am eager to contribute my expertise to help [Company] achieve its goals and would welcome the opportunity to discuss how my background can benefit your team.

                Thank you for your time and consideration.

                Best regards,
                [Your Name]
                """
            # Generate cover letter content using Gemini
            cover_letter_content, company = self.gemini_service.generate_cover_letter(
                template_text=template_text,
                job_description=request.job_description,
                projects=request.matched_projects,
            )
            
            print("Generated Cover Letter for:\n", company)
            
            # Create LaTeX content with the generated text
            
            latex_content = self._create_latex_document(cover_letter_content, personal_info={})
            print("Generated LaTeX content for cover letter.")
            
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

    def _create_latex_document(self, content: str, personal_info: dict) -> str:
        """
        Create LaTeX document with generated content using professional template
        """
        # Extract personal info with defaults
        name = 'Chater Marzougui'
        email = 'chater.marzougui@supcom.tn'
        phone = '+216 28 356 927'
        title = 'Software Engineering Student'
        
        formatted_content = self.fix_latex_special_chars(content)

        latex_template = r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[left=0.8in,right=0.8in,top=0.8in,bottom=1in]{geometry}
\usepackage{parskip}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{microtype}
\usepackage{enumitem}
\usepackage{setspace}
\usepackage{titling}

% Define colors
\definecolor{primaryblue}{RGB}{41, 128, 185}
\definecolor{darkgray}{RGB}{64, 64, 64}
\definecolor{lightgray}{RGB}{128, 128, 128}

% Remove page numbering
\pagestyle{empty}

% Custom section formatting
\usepackage{titlesec}
\titleformat{\section}[hang]{\large\bfseries\color{primaryblue}}{}{0em}{}[\vspace{-0.5em}\color{primaryblue}\rule{\textwidth}{0.8pt}\vspace{0.2em}]

% Header with modern design
\newcommand{\letterheader}{
    \begin{center}
        \tikz[remember picture,overlay] \node[anchor=north,yshift=-0.5cm] at (current page.north) {
            \begin{tikzpicture}
                \fill[primaryblue!10] (0,0) rectangle (\paperwidth,-3cm);
            \end{tikzpicture}
        };
        
        \vspace{1.5cm}
        {\Huge\bfseries\color{primaryblue}""" + name + r"""}\\[0.3cm]
        {\Large\color{darkgray}""" + title + r"""}\\[0.8cm]
        
        \begin{tikzpicture}
            \node[anchor=center] at (0,0) {
                \color{lightgray}
                \textbf{Email:} """ + email + r""" \quad 
                \textbf{Phone:} """ + phone + r"""
            };
        \end{tikzpicture}
    \end{center}
    
    \vspace{1cm}
}

\begin{document}

\letterheader

""" + formatted_content + r"""

\vspace{2cm}

\begin{flushright}
    \begin{minipage}{4cm}
        \color{darkgray}
        Sincerely,\\[0.8cm]
        {\bfseries """ + name + r"""}
    \end{minipage}
\end{flushright}

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

            # Compile with pdflatex (run three times for references)
            for i in range(3):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode',
                    '-output-directory', self.temp_dir, tex_file],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0 and i == 2:
                    raise RuntimeError(f"LaTeX compilation failed after 3 attempts:\n{result}")
                elif result.returncode != 0:
                    print(result.stderr)
                    print(result.stdout)
                    print(f"LaTeX compilation error on attempt {i+1}:\n{result.stderr}")
                else:
                    break
                
            # Move PDF to output directory
            temp_pdf = os.path.join(self.temp_dir, f"{filename_prefix}.pdf")
            if not os.path.exists(temp_pdf):
                raise RuntimeError("PDF was not generated")
            
            output_pdf = os.path.join(self.output_dir, f"{filename_prefix}.pdf")
            shutil.copy2(temp_pdf, output_pdf)
            
            return output_pdf
                
        except Exception as e:
            raise RuntimeError(f"LaTeX compilation error: {str(e)}")
        
    def fix_latex_special_chars(self, text: str) -> str:
        """
        Fix special characters in LaTeX by escaping them if not already escaped.
        
        Args:
            text (str): The input text that may contain unescaped LaTeX special characters
            
        Returns:
            str: Text with properly escaped LaTeX special characters
        """
        import re
        
        # Define the special characters and their LaTeX escaped versions
        special_chars = {
            '&': r'\&',
            '%': r'\%', 
            '$': r'\$',
            '#': r'\#',
            '^': r'\^{}',
            '_': r'\_',
            '~': r'\~{}',
            '\\': r'\textbackslash{}',  # Handle backslash specially
        }
        
        result = text
        
        for char, escaped in special_chars.items():
            if char == '\\':
                # Special handling for backslash - only escape standalone backslashes
                # that aren't part of existing LaTeX commands
                pattern = r'(?<!\\)\\(?![a-zA-Z{}&%$#^_~])'
                result = re.sub(pattern, escaped, result)
            else:
                # Create pattern to match unescaped characters
                # Look for the character not preceded by backslash
                pattern = f'(?<!\\\\){re.escape(char)}'
                result = re.sub(pattern, escaped, result)
        
        return result
    
    def __del__(self):
        """
        Cleanup temporary directory
        """
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass