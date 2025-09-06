import os
import tempfile
import subprocess
import shutil
from typing import List, Dict, Any
from jinja2 import Template, Environment, FileSystemLoader
from app.models.project import MatchedProject, CoverLetterRequest, JobDescription
import aiofiles

class CoverLetterGenerator:
    def __init__(self):
        self.templates_dir = "templates"
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = "output"
        
        # Create directories if they don't exist
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(loader=FileSystemLoader(self.templates_dir))
    
    async def generate_cover_letter(self, request: CoverLetterRequest) -> str:
        """
        Generate cover letter PDF from template
        """
        try:
            template_path = request.template_path or "cover_letter_template.tex"
            
            # Prepare template data
            template_data = {
                'personal_info': request.personal_info,
                'job': {
                    'title': request.job_description.title,
                    'company': request.job_description.company,
                    'description': request.job_description.description,
                    'requirements': request.job_description.requirements
                },
                'projects': [],
                'relevant_skills': self._extract_relevant_skills(request),
                'cover_letter_content': await self._generate_cover_letter_content(request)
            }
            
            # Process matched projects
            for matched_project in request.matched_projects[:3]:  # Use top 3 projects for cover letter
                project = matched_project.project
                project_data = {
                    'name': project.name,
                    'url': project.url,
                    'description': project.three_liner.split('\n')[0].replace('•', '').strip(),
                    'technologies': project.technologies[:5],  # Limit to top 5 technologies
                    'relevance_reason': matched_project.relevance_reason,
                    'similarity_score': matched_project.similarity_score
                }
                template_data['projects'].append(project_data)
            
            # Load and render template
            template = self.jinja_env.get_template(template_path)
            latex_content = template.render(**template_data)
            
            # Generate PDF
            pdf_path = await self._compile_latex(latex_content, f"cover_letter_{request.job_description.company}")
            
            return pdf_path
            
        except Exception as e:
            raise RuntimeError(f"Error generating cover letter: {str(e)}")

    def _generate_cover_letter_content(self, request: CoverLetterRequest) -> Dict[str, str]:
        """
        Generate the main content paragraphs for the cover letter
        """
        job = request.job_description
        projects = request.matched_projects[:3]
        
        # Introduction paragraph
        introduction = f"I am writing to express my strong interest in the {job.title} position at {job.company}. "
        introduction += "With my demonstrated experience in software development and a portfolio of relevant projects, "
        introduction += "I am confident that I would be a valuable addition to your team."
        
        # Experience paragraph (based on projects)
        experience = "My technical expertise is demonstrated through several key projects: "
        project_descriptions = []
        
        for matched_project in projects:
            project = matched_project.project
            project_desc = f"{project.name}, which showcases my proficiency in {', '.join(project.technologies[:3])}"
            if project.stars > 5:
                project_desc += f" and has gained recognition with {project.stars} GitHub stars"
            project_descriptions.append(project_desc)
        
        if project_descriptions:
            experience += "; ".join(project_descriptions[:2]) + ". "
        
        experience += "These projects demonstrate my ability to deliver practical solutions and work with modern development practices."
        
        # Skills alignment paragraph
        alignment = f"I am particularly drawn to this role at {job.company} because it aligns perfectly with my technical background. "
        
        # Extract common technologies between job and projects
        job_text = f"{job.description} {job.requirements or ''}".lower()
        common_techs = set()
        
        for matched_project in projects:
            for tech in matched_project.project.technologies:
                if tech.lower() in job_text:
                    common_techs.add(tech)
        
        if common_techs:
            alignment += f"My experience with {', '.join(list(common_techs)[:4])} directly addresses your technical requirements. "
        
        alignment += "I am excited about the opportunity to contribute to your team's success and grow within your organization."
        
        # Closing paragraph
        closing = f"I would welcome the opportunity to discuss how my technical skills and project experience can contribute to {job.company}'s continued success. "
        closing += "Thank you for considering my application. I look forward to hearing from you soon."
        
        return {
            'introduction': introduction,
            'experience': experience,
            'alignment': alignment,
            'closing': closing
        }
    
    def _extract_relevant_skills(self, request: CoverLetterRequest) -> List[str]:
        """
        Extract skills that are relevant to the job from the matched projects
        """
        job_text = f"{request.job_description.description} {request.job_description.requirements or ''}".lower()
        
        all_skills = set()
        for matched_project in request.matched_projects:
            all_skills.update(matched_project.project.technologies)
        
        # Filter skills that appear in job description
        relevant_skills = []
        for skill in all_skills:
            if skill.lower() in job_text:
                relevant_skills.append(skill)
        
        # Add some common professional skills
        soft_skills = []
        if 'team' in job_text or 'collaborative' in job_text:
            soft_skills.append('Team Collaboration')
        if 'problem' in job_text:
            soft_skills.append('Problem Solving')
        if 'communication' in job_text:
            soft_skills.append('Communication')
        
        return relevant_skills[:8] + soft_skills[:2]  # Limit to avoid overcrowding
    
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
    
    def create_default_cover_letter_template(self):
        """
        Create a default cover letter template if none exists
        """
        template_path = os.path.join(self.templates_dir, "cover_letter_template.tex")
        
        if os.path.exists(template_path):
            return template_path
        
        default_template = r"""
\documentclass[11pt,a4paper]{letter}

% Packages
\usepackage[utf8]{inputenc}
\usepackage[scale=0.75]{geometry}
\usepackage{url}

% Letter formatting
\longindentation=0pt

% Personal information
\name{{ personal_info.first_name }} {{ personal_info.last_name }}
\address{{ personal_info.address }}\\{{ personal_info.city }}, {{ personal_info.postal_code }}}
\telephone{{ personal_info.phone }}

\begin{document}

% Date and recipient address
\begin{letter}{%
Hiring Manager\\
{{ job.company }}\\
{% if job.address %}{{ job.address }}{% else %}[Company Address]{% endif %}
}

% Opening
\opening{Dear Hiring Manager,}

% Introduction
{{ cover_letter_content.introduction }}

% Experience paragraph
{{ cover_letter_content.experience }}

% Project highlights
{% if projects %}
Specifically, I would like to highlight the following relevant projects:
\begin{itemize}
{% for project in projects %}
    \item \textbf{{ project.name }}: {{ project.description }} ({{ project.technologies|join(', ') }})
{% endfor %}
\end{itemize}
{% endif %}

% Skills alignment
{{ cover_letter_content.alignment }}

% Relevant skills
{% if relevant_skills %}
My technical skill set includes: {{ relevant_skills|join(', ') }}.
{% endif %}

% Closing paragraph
{{ cover_letter_content.closing }}

% Sign off
\closing{Sincerely,}

% Optional: Enclosures
\encl{Resume}

\end{letter}
\end{document}
"""
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(default_template)
        
        return template_path