import os
import subprocess
import tempfile
import re
from app.models.project import CVGenerationRequest
import shutil
import time

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
            
            # Format technologies as comma-separated string and escape LaTeX special chars
            tech_str = ", ".join(project.technologies) if project.technologies else ""
            tech_str = self._escape_latex(tech_str)
            
            # Escape LaTeX special characters in project data
            project_name = self._escape_latex(project.name)
            project_description = self._escape_latex(project.three_liner)
            project_url = project.url  # URLs typically don't need escaping in href
            
            # Generate LaTeX for each project
            project_latex = f"""\\item {{\\href{{{project_url}}}{{\\color{{bgcol}}\\faGithub{{ Code Link}}}} \\textbf{{{project_name}}}
{project_description}
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
            return pdf_path
            
        except Exception as e:
            raise RuntimeError(f"Error generating CV: {str(e)}")
    
    def _compile_latex(self, latex_content, output_name):
        """Compile LaTeX content to PDF with improved error handling for MiKTeX"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                tex_file = os.path.join(temp_dir, f"{output_name}.tex")
                pdf_file = os.path.join(temp_dir, f"{output_name}.pdf")
                output_pdf = os.path.join(self.output_dir, f"{output_name}.pdf")
                
                # Write LaTeX content to file
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(latex_content)

                print(f"Compiling {output_name}...")

                # Set environment variables for MiKTeX
                env = os.environ.copy()
                env['MIKTEX_ENABLEINSTALLER'] = 'yes'  # Allow automatic package installation
                env['TEXMFHOME'] = temp_dir  # Use temp directory for cache
                
                max_tries = 3  # Reduced from 5 since we have better error handling
                
                for attempt in range(max_tries):
                    print(f"Compilation attempt {attempt + 1}/{max_tries}")
                    
                    # Add a small delay between attempts to let MiKTeX settle
                    if attempt > 0:
                        time.sleep(2)
                    
                    # Run pdflatex with improved settings for MiKTeX
                    result = subprocess.run([
                        'pdflatex',
                        '-interaction=nonstopmode',
                        '-halt-on-error',
                        '-file-line-error',
                        '-synctex=1',
                        tex_file
                    ], 
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=60  # 60 second timeout
                    )
                    
                    if result.returncode == 0:
                        print("LaTeX compilation successful!")
                        break
                    else:
                        print(f"LaTeX compilation failed on attempt {attempt + 1}")
                        print(f"Return code: {result.returncode}")
                        print(f"STDOUT: {result.stdout}")
                        print(f"STDERR: {result.stderr}")
                        
                        # Check if it's a missing package issue
                        if "Package" in result.stderr and "not found" in result.stderr:
                            print("Detected missing package issue - MiKTeX should auto-install")
                            continue
                        
                        # Check if it's a font cache issue
                        if "font" in result.stderr.lower() or "cache" in result.stderr.lower():
                            print("Detected font/cache issue - clearing and retrying")
                            # Try to refresh font cache
                            subprocess.run(['fc-cache', '-f'], capture_output=True)
                            continue
                        
                        if attempt == max_tries - 1:
                            # Last attempt failed, provide detailed error
                            error_msg = f"""LaTeX compilation failed after {max_tries} attempts.
Return code: {result.returncode}
STDERR: {result.stderr}
STDOUT: {result.stdout}

Check the test.tex file in {self.templates_dir} for syntax issues."""
                            raise RuntimeError(error_msg)
                
                # Check if PDF was actually created
                if not os.path.exists(pdf_file):
                    raise RuntimeError("PDF file was not created despite successful compilation")
                
                # Copy output PDF to output directory
                shutil.copy2(pdf_file, output_pdf)
                print(f"PDF successfully created: {output_pdf}")
                
                return output_pdf
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("LaTeX compilation timed out - this may indicate an infinite loop or hanging process")
        except Exception as e:
            raise RuntimeError(f"PDF compilation error: {str(e)}")

    def _escape_latex(self, text: str) -> str:
        """
        Escape special LaTeX characters
        """
        if not text:
            return ""
            
        latex_special_chars = {
            '\\': r'\textbackslash{}',  # Must be first to avoid double escaping
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '^': r'\textasciicircum{}',
            '_': r'\_',
            '~': r'\textasciitilde{}',
            '{': r'\{',
            '}': r'\}',
        }
        
        for char, escape in latex_special_chars.items():
            text = text.replace(char, escape)
        
        return text