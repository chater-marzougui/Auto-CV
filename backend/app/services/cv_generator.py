from asyncio import create_subprocess_exec
import os
import subprocess
import tempfile
from jinja2 import Template, Environment, FileSystemLoader
from app.models.project import MatchedProject, CVGenerationRequest
import shutil

class CVGenerator:
    def __init__(self):
        self.templates_dir = "templates"
        self.output_dir = "output"
        
        # Create directories if they don't exist
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(loader=FileSystemLoader(self.templates_dir))
    
    def generate_cv(self, request: CVGenerationRequest) -> str:
        """
        Generate CV PDF from LaTeX template
        """
        try:
            template_path = request.template_path or "cv_template.tex"
            
            # Prepare template data
            template_data = {
                'personal_info': request.personal_info,
                'projects': []
            }
            
            # Process matched projects for CV
            for matched_project in request.matched_projects:
                project = matched_project.project
                project_data = {
                    'name': project.name,
                    'url': project.url,
                    'three_liner': project.three_liner,
                    'technologies': project.technologies,
                    'relevance_reason': matched_project.relevance_reason,
                    'stars': project.stars,
                    'forks': project.forks
                }
                template_data['projects'].append(project_data)
            
            # Load and render template
            template = self.jinja_env.get_template(template_path)
            latex_content = template.render(**template_data)
            
            # Generate PDF
            pdf_path = self._compile_latex(latex_content, "cv")
            
            return pdf_path
            
        except Exception as e:
            raise RuntimeError(f"Error generating CV: {str(e)}")
    
    def _compile_latex(self, latex_content: str, filename_prefix: str) -> str:
        """
        Compile LaTeX content to PDF
        """
        try:
            # Check if pdflatex is available
            if not shutil.which('pdflatex'):
                raise FileNotFoundError("pdflatex not found. Please install LaTeX (e.g., texlive-latex-base)")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                tex_file = os.path.join(temp_dir, f"{filename_prefix}.tex")
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(latex_content)
                
                import asyncio

                # Compile with pdflatex (run twice for references)
                for _ in range(2):
                    process = create_subprocess_exec(
                        'pdflatex', '-interaction=nonstopmode', '-output-directory', temp_dir, tex_file,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=temp_dir
                    )
                    _ , stderr = process.communicate()

                    if process.returncode != 0:
                        raise RuntimeError(f"LaTeX compilation failed: {stderr.decode()}")

                # Move PDF to output directory
                temp_pdf = os.path.join(temp_dir, f"{filename_prefix}.pdf")
                if not os.path.exists(temp_pdf):
                    raise RuntimeError("PDF was not generated")

                output_pdf = os.path.join(self.output_dir, f"{filename_prefix}_{hash(latex_content)}.pdf")
                shutil.copy2(temp_pdf, output_pdf)
                
                return output_pdf
                
        except Exception as e:
            raise RuntimeError(f"LaTeX compilation error: {str(e)}")

    def _escape_latex(self, text: str) -> str:
        """
        Escape special LaTeX characters
        """
        latex_special_chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '^': r'\textasciicircum{}',
            '_': r'\_',
            '~': r'\textasciitilde{}',
            '{': r'\{',
            '}': r'\}',
            '\\': r'\textbackslash{}'
        }
        
        for char, escape in latex_special_chars.items():
            text = text.replace(char, escape)
        
        return text
    
    def create_default_cv_template(self):
        """
        Create a default CV template if none exists
        """
        template_path = os.path.join(self.templates_dir, "cv_template.tex")
        
        if os.path.exists(template_path):
            return template_path
        
        default_template = r"""
\documentclass[11pt,a4paper]{moderncv}

% ModernCV themes
\moderncvstyle{classic}
\moderncvcolor{blue}

% Character encoding
\usepackage[utf8]{inputenc}

% Page margins
\usepackage[scale=0.75]{geometry}

% Personal data
\name{{ personal_info.first_name }}{{ personal_info.last_name }}
\title{{ personal_info.title }}
\address{{ personal_info.address }}{{ personal_info.city }}{{ personal_info.postal_code }}
\phone[mobile]{{ personal_info.phone }}
\email{{ personal_info.email }}
{% if personal_info.linkedin %}\social[linkedin]{{ personal_info.linkedin }}{% endif %}
{% if personal_info.github %}\social[github]{{ personal_info.github }}{% endif %}

\begin{document}

\makecvtitle

% Professional Summary
{% if personal_info.summary %}
\section{Professional Summary}
\cvitem{}{{ personal_info.summary }}
{% endif %}

% Technical Skills
{% if personal_info.skills %}
\section{Technical Skills}
{% for skill_category, skills in personal_info.skills.items() %}
\cvitem{{ skill_category }}{{ skills|join(', ') }}
{% endfor %}
{% endif %}

% Relevant Projects
\section{Relevant Projects}
{% for project in projects %}
\cventry{}{{ project.name }}{}{}{}
{
    \begin{itemize}
        \item {{ project.three_liner.replace('\n', '') }}
        \item Technologies: {{ project.technologies|join(', ') }}
        \item {{ project.relevance_reason }}
        {% if project.stars > 0 %}\item GitHub: {{ project.stars }} stars, {{ project.forks }} forks{% endif %}
    \end{itemize}
    \textit{Repository: \url{{ project.url }}}
}
{% endfor %}

% Work Experience
{% if personal_info.experience %}
\section{Work Experience}
{% for job in personal_info.experience %}
\cventry{{ job.start_date }}--{{ job.end_date }}{{ job.title }}{{ job.company }}{{ job.location }}{}
{
    {% if job.description %}{{ job.description }}{% endif %}
    {% if job.achievements %}
    \begin{itemize}
        {% for achievement in job.achievements %}
        \item {{ achievement }}
        {% endfor %}
    \end{itemize}
    {% endif %}
}
{% endfor %}
{% endif %}

% Education
{% if personal_info.education %}
\section{Education}
{% for edu in personal_info.education %}
\cventry{{ edu.start_date }}--{{ edu.end_date }}{{ edu.degree }}{{ edu.institution }}{{ edu.location }}{{ edu.gpa }}{{ edu.description }}
{% endfor %}
{% endif %}

\end{document}
"""
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(default_template)
        
        return template_path