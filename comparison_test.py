#!/usr/bin/env python3
"""
Comparison test: Basic vs Enhanced cover letter design
"""
import tempfile
import subprocess
import shutil
import os

def create_basic_template(content: str, personal_info: dict) -> str:
    """Original basic LaTeX template"""
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

def create_enhanced_template(content: str, personal_info: dict) -> str:
    """New enhanced LaTeX template"""
    name = personal_info.get('first_name', 'John') + ' ' + personal_info.get('last_name', 'Doe')
    email = personal_info.get('email', 'john.doe@example.com')
    phone = personal_info.get('phone', '+1 (555) 123-4567')
    title = personal_info.get('title', 'Software Developer')
    
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

def compile_latex(latex_content: str, filename: str) -> str:
    """Compile LaTeX to PDF"""
    temp_dir = tempfile.mkdtemp()
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    tex_file = os.path.join(temp_dir, f"{filename}.tex")
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    # Compile twice for references
    for _ in range(2):
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', temp_dir, tex_file],
            capture_output=True,
            text=True,
            cwd=temp_dir
        )
        if result.returncode != 0:
            print(f"LaTeX error for {filename}:")
            print(result.stderr)
            return None
    
    temp_pdf = os.path.join(temp_dir, f"{filename}.pdf")
    output_pdf = os.path.join(output_dir, f"{filename}.pdf")
    
    if os.path.exists(temp_pdf):
        shutil.copy2(temp_pdf, output_pdf)
        shutil.rmtree(temp_dir, ignore_errors=True)
        return output_pdf
    return None

def main():
    """Generate both versions for comparison"""
    print("🔄 Generating cover letter comparison...")
    
    # Sample data
    personal_info = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@email.com",
        "phone": "+1 (555) 987-6543",
        "title": "Senior Software Engineer"
    }
    
    cover_letter_content = """Dear Hiring Manager,

I am writing to express my strong interest in the Senior Software Engineer position at your company. With over 6 years of experience in software development and a proven track record of delivering high-quality applications, I am confident I would be a valuable addition to your engineering team.

My expertise spans across multiple technologies including Python, JavaScript, React, and cloud platforms. In my recent projects, I have successfully led the development of scalable web applications, implemented robust API architectures, and mentored junior developers. My experience with agile methodologies and cross-functional collaboration has enabled me to deliver projects on time while maintaining high code quality standards.

I am particularly excited about this opportunity because it aligns perfectly with my passion for building innovative solutions and my desire to work with cutting-edge technologies. I would welcome the chance to discuss how my technical skills and leadership experience can contribute to your team's success.

Thank you for considering my application."""
    
    # Generate basic version
    print("📝 Generating basic template...")
    basic_latex = create_basic_template(cover_letter_content, personal_info)
    basic_pdf = compile_latex(basic_latex, "cover_letter_basic")
    
    # Generate enhanced version
    print("✨ Generating enhanced template...")
    enhanced_latex = create_enhanced_template(cover_letter_content, personal_info)
    enhanced_pdf = compile_latex(enhanced_latex, "cover_letter_enhanced")
    
    # Results
    print("\n" + "="*60)
    print("📊 COMPARISON RESULTS")
    print("="*60)
    
    if basic_pdf:
        basic_size = os.path.getsize(basic_pdf)
        print(f"📄 Basic Template: {basic_pdf}")
        print(f"   Size: {basic_size} bytes")
    else:
        print("❌ Basic template failed to compile")
    
    if enhanced_pdf:
        enhanced_size = os.path.getsize(enhanced_pdf)
        print(f"✨ Enhanced Template: {enhanced_pdf}")
        print(f"   Size: {enhanced_size} bytes")
    else:
        print("❌ Enhanced template failed to compile")
    
    print("\n🎨 DESIGN IMPROVEMENTS:")
    print("• Professional header with colored background")
    print("• Modern typography with better font selection")
    print("• Visual hierarchy with color-coded elements")
    print("• Better spacing and layout")
    print("• Contact information prominently displayed")
    print("• Professional signature section")
    
    if basic_pdf and enhanced_pdf:
        print(f"\n📈 Size difference: {enhanced_size - basic_size} bytes")
        print("Both PDFs generated successfully for comparison!")

if __name__ == "__main__":
    main()