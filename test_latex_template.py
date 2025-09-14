#!/usr/bin/env python3
"""
Test script to test LaTeX template with sample content
"""
import sys
import os
sys.path.append('backend')

import tempfile
import subprocess
import shutil

def create_sample_latex_content():
    """Create sample content for testing the LaTeX template"""
    personal_info = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1 (555) 123-4567",
        "title": "Senior Full Stack Developer"
    }
    
    # Sample cover letter content
    cover_letter_content = """Dear Hiring Manager,

I am writing to express my strong interest in the Senior Full Stack Developer position at TechCorp. With over 5 years of experience in full-stack development and a proven track record of building scalable web applications, I am confident I would be a valuable addition to your development team.

In my recent projects, I have gained extensive experience with Python, FastAPI, React, and PostgreSQL - technologies that align perfectly with your requirements. My E-commerce API project demonstrates my expertise in building RESTful APIs with FastAPI, implementing secure authentication systems, and managing complex data relationships with PostgreSQL. Additionally, my React Dashboard project showcases my frontend capabilities, featuring real-time data visualization, responsive design, and modern TypeScript implementation.

What particularly excites me about this opportunity at TechCorp is the chance to work with cross-functional teams and contribute to mentoring junior developers. I am passionate about code quality, scalable architecture, and staying current with emerging technologies. I would welcome the opportunity to discuss how my technical expertise and collaborative approach can contribute to TechCorp's continued success.

Thank you for your time and consideration."""
    
    return create_latex_document(cover_letter_content, personal_info)

def create_latex_document(content: str, personal_info: dict = None) -> str:
    """
    Create LaTeX document with generated content using professional template
    """
    # Extract personal info with defaults
    name = personal_info.get('first_name', 'John') + ' ' + personal_info.get('last_name', 'Doe') if personal_info else 'John Doe'
    email = personal_info.get('email', 'john.doe@example.com') if personal_info else 'john.doe@example.com'
    phone = personal_info.get('phone', '+1 (555) 123-4567') if personal_info else '+1 (555) 123-4567'
    title = personal_info.get('title', 'Software Developer') if personal_info else 'Software Developer'
    
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

""" + content + r"""

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

def compile_latex_test(latex_content: str, filename_prefix: str = "test_cover_letter") -> str:
    """
    Compile LaTeX content to PDF for testing
    """
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Check if pdflatex is available
        if not shutil.which('pdflatex'):
            raise RuntimeError("pdflatex not found. Please install LaTeX (e.g., texlive-latex-base)")
        
        # Write LaTeX content to temporary file
        tex_file = os.path.join(temp_dir, f"{filename_prefix}.tex")
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        print(f"LaTeX source written to: {tex_file}")
        
        # Compile with pdflatex (run twice for references)
        for i in range(2):
            print(f"Running pdflatex (pass {i+1}/2)...")
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', temp_dir, tex_file],
                capture_output=True,
                text=True,
                cwd=temp_dir
            )
            
            if result.returncode != 0:
                print("LaTeX compilation error:")
                print(result.stdout)
                print(result.stderr)
                raise RuntimeError(f"LaTeX compilation failed: {result.stderr}")
        
        # Move PDF to output directory
        temp_pdf = os.path.join(temp_dir, f"{filename_prefix}.pdf")
        if not os.path.exists(temp_pdf):
            raise RuntimeError("PDF was not generated")
        
        output_pdf = os.path.join(output_dir, f"{filename_prefix}_enhanced.pdf")
        shutil.copy2(temp_pdf, output_pdf)
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return output_pdf
            
    except Exception as e:
        raise RuntimeError(f"LaTeX compilation error: {str(e)}")

def test_latex_template():
    """Test the LaTeX template with sample content"""
    print("Testing enhanced LaTeX template...")
    
    try:
        # Create sample content
        latex_content = create_sample_latex_content()
        
        # Compile to PDF
        pdf_path = compile_latex_test(latex_content)
        
        print(f"✅ Enhanced cover letter generated successfully!")
        print(f"📄 PDF saved to: {pdf_path}")
        print(f"📁 Absolute path: {os.path.abspath(pdf_path)}")
        
        # Check file size
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"📊 File size: {file_size} bytes")
        
        return pdf_path
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_latex_template()