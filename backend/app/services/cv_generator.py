import os
import subprocess
import tempfile
import re
from app.models.project import CVGenerationRequest
import shutil

class CVGenerator:
    def __init__(self):
        self.templates_dir = "templates"
        self.output_dir = "output"
        
        # Create directories if they don't exist
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_projects_latex(self, matched_projects):
        """Generate LaTeX content for projects section only"""
        projects_content = []
        
        for matched_project in matched_projects:
            project = matched_project.project
            
            # Format technologies as comma-separated string
            tech_str = ", ".join(project.technologies) if project.technologies else ""
            
            # Generate LaTeX for each project
            project_latex = f"""\\item {{\\href{{{project.url}}}{{\\color{{bgcol}}\\faGithub{{ Code Link}}}} \\textbf{{{project.name}}}
{project.three_liner}
\\textit{{({tech_str})}}}}
\\vspace{{5px}}"""
            
            projects_content.append(project_latex)
        
        return "\n\n".join(projects_content)
    
    def generate_cv(self, request: CVGenerationRequest) -> str:
        """
        Generate CV PDF by replacing projects section in existing LaTeX template
        """
        try:
            template_filename = request.template_path or "cv_template.tex"
            template_full_path = os.path.join(self.templates_dir, template_filename)
            
            # Check if template exists
            if not os.path.exists(template_full_path):
                raise FileNotFoundError(f"CV template not found: {template_full_path}")
            
            # Read the existing LaTeX file
            with open(template_full_path, 'r', encoding='utf-8') as f:
                latex_content = f.read()
            
            # Generate new projects section
            new_projects_content = self.generate_projects_latex(request.matched_projects)
            
            print("Replacing projects section")
            # Find and replace the projects section
            # Pattern to match everything between \begin{itemize} after Personal Projects and \end{itemize}
            pattern = r'(\\cvsection\{PERSONAL PROJECTS\}.*?\\begin\{itemize\}(?:\[.*?\])?)(.*?)(\\end\{itemize\})'

            def replace_projects(match):
                return match.group(1) + "\n" + new_projects_content + "\n" + match.group(3)
            
            # Replace the projects content
            latex_content = re.sub(pattern, replace_projects, latex_content, flags=re.DOTALL)
            # Write the modified LaTeX content to test.tex for inspection
            with open(os.path.join(self.templates_dir, "test.tex"), 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            # Generate PDF
            pdf_path = self._compile_latex(latex_content, "cv")
            print("CV generated at:", pdf_path) 
            return pdf_path
            
        except Exception as e:
            raise RuntimeError(f"Error generating CV: {str(e)}")
    
    def _compile_latex(self, latex_content, output_name):
        """Compile LaTeX content to PDF"""
        # This method needs to be implemented based on your LaTeX compilation setup
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                tex_file = os.path.join(temp_dir, f"{output_name}.tex")
                pdf_file = os.path.join(temp_dir, f"{output_name}.pdf")
                output_pdf = os.path.join(self.output_dir, f"{output_name}.pdf")
                
                # Write LaTeX content to file
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(latex_content)
                
                # Compile LaTeX (requires pdflatex to be installed)
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', tex_file],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    raise RuntimeError(f"LaTeX compilation failed: {result.stderr}")
                
                # Copy output PDF to output directory
                shutil.copy2(pdf_file, output_pdf)
                
                return output_pdf
                
        except Exception as e:
            raise RuntimeError(f"PDF compilation error: {str(e)}")

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