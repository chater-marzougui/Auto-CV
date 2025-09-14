import google.generativeai as genai
import os
import json

class GeminiService:
    def __init__(self):
        apikey = os.getenv("GEMINI_API_KEY")
        if not apikey:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=apikey)
        self.fast_model = genai.GenerativeModel("gemini-2.0-flash")
        self.precise_model = genai.GenerativeModel("gemini-2.5-flash")

    def generate_project_summary(self, repo_name: str, readme_content: str, file_tree: list) -> dict:
        """
        Generate a detailed description, a concise 3-liner summary 
        and used technologies for a GitHub repository description
        """

        readme_content = readme_content[:15000] if len(readme_content) > 15000 else readme_content
        
        prompt = f"""You will be given a readme file a github repository.
    You need to generate these three values for the given readme content:
    detailed: A detailed paragraph summarizing the project
    three_liner: A concise 3-liner summary of the project
    technologies: A list of key technologies used in the project
    bad_readme: A boolean indicating if the readme content is too short or not useful for understanding the project (true/false)

    Your response for each question should be in the following format:
    {{
        "detailed": "Detailed paragraph here",
        "three_liner": "3-liner paragraph (no return to line) summary here it should be a short and straight to the point",
        "technologies": ["Technology 1", "Technology 2", ...],
        "bad_readme": true/false
    }}

    The response should adhere to the following:
    - Ensure the JSON is properly formatted.
    - Only the json response should be returned no other data.
    - The 3 liner will be used in a CV so format it to be unambiguous and impactful and straight to the point (no long lines).
    - never mention the technologies in the three liner.
    - The detailed paragraph should provide a comprehensive overview of the project.
    - in the three liner don't include the project name start directly.
    - The technologies should be a list of key technologies used in the project (e.g., React, Node.js).
    - The technologies should be relevant to the project and not generic.
    - The technologies should be only the main ones that are critical to the project with no examples.
    - Examples of absolutely not acceptable technologies: "JSON", "LLAMA-7b", "Raspberry Pi",
    "Sensors", "Ultra Sonic", "Windows encryption", "Ngrok", "LocalTunnel".
    - Examples of acceptable technologies: "React", "Node.js", "Express", "PostgreSQL", "Docker", "Kubernetes", "Flask", "Django", "TensorFlow", "PyTorch".
    - Technologies should be formatted in camel case or proper case (e.g., "Node.js", "React", "PostgreSQL").
    - Technologies should not include versions, examples, or long names.
    - Formatting examples of not acceptable technologies: "Node.js v14 -> Node.js", "React 17 -> React", "PostgreSQL database -> PostgreSQL", "Docker containerization -> Docker", "Long Short-Term Memory (LSTM) -> LSTM".
    - If the readme is too short or not useful, set "bad_readme" to true.
    - If "bad_readme" is true, the "detailed" and "three_liner" can be generic but still relevant to the project.
    
    Here is the repository information:
    Repository Name: {repo_name}
    
    Readme content:
    {readme_content}
    
    File tree:
    {','.join(file_tree[:50]) if file_tree else 'N/A'}

"""
        
        response = self.precise_model.generate_content([prompt])
        json_response = self._extract_json(response.text)

        return json_response

    def job_description_parser(self, job_description: str) -> dict:
        """
        Parse job description to extract title, company, description, and requirements
        """
        print("Parsing job description with Gemini...")
        prompt = f"""You will be given a job description text.
    Extract the following fields and return them in a JSON format:
    - title: Job title
    - company: Company name
    - required_technologies: List of key technologies required
    - experience_level: Experience level required (e.g., Junior, Senior)
    - soft_skills: List of important soft skills mentioned
    - analysis_summary: A brief summary of the job highlighting main points    
    - requirements: Key requirements or qualifications
    Your response should be in the following format:
    {{
        "title": "Job Title",
        "company": "Company Name",
        "required_technologies": ["Tech 1", "Tech 2", ...],
        "experience_level": "Experience Level",
        "soft_skills": ["Skill 1", "Skill 2", ...],
        "analysis_summary": "Brief summary here of the job highlighting main points (3-5 lines)",
        "requirements": "Key requirements here"
    }}

    Job description:
    {job_description}
    """

        response = self.fast_model.generate_content([prompt])
        json_response = self._extract_json(response.text)

        return {**json_response, "full_description": job_description}

    def generate_cover_letter(self, template_text: str, job_description: str, projects: list) -> tuple[str, str]:
        """
        Generate cover letter content using template, job description, and relevant projects
        """
        # Prepare project information
        project_info = ""
        for i, matched_project in enumerate(projects, 1):
            project = matched_project.project
            project_info += f"""
            Project {i}: {project.name}
            - Description: {project.detailed_paragraph}
            - three liner: {project.three_liner}
            - Technologies: {', '.join(project.technologies)}
            """
        
        prompt = f"""You are an expert professional cover letter writer. Create a compelling, personalized cover letter that follows modern best practices and stands out to hiring managers.

    TEMPLATE TO FOLLOW (adapt the structure, tone and style):
    {template_text}

    JOB INFORMATION:
    {job_description}


    RELEVANT PROJECTS (if relevant to the job, incorporate 1-2 max naturally):
    {project_info}

    INSTRUCTIONS:
    1. Follow the structure and tone of the provided template
    2. Adapt the content to match the specific job requirements
    3. If the provided projects are relevant to the job requirements, mention them naturally in the experience section
    4. Only include projects that are actually relevant - don't force irrelevant projects into the letter
    5. Keep the same professional tone as the template
    6. Make sure the letter flows naturally and doesn't sound templated
    7. Focus on how the candidate's experience matches the job requirements
    8. Keep it concise and impactful (2-3 paragraphs)
    9. Don't include placeholder text like [Your Name] or [Company Name] - use actual values
    10. Return only the body paragraphs of the cover letter, without salutation or closing
    
    IMPORTANT:
    1. The text will be used in a LaTeX template so avoid any special characters that could break the formatting
    2. You can use latex commands for formatting like textbf for bold and try to make empty lines between paragraphs.
    2. don't include package imports or document structure just the letter content
    4. Don't make the cover letter long a maximum of 3 paragraphs with max 300 words for the entire letter
    
    return a json with two keys and no other text just the json:
    {{
        "company_name": "the company name extracted from the job description no spaces or special characters",
        "cover_letter": "the full text of the cover letter following the template structure and tone"
    }}
"""

        response = self.precise_model.generate_content([prompt])
        json_response = self._extract_json(response.text)
        response_text = json_response.get("cover_letter", "").replace("\\\\n", "\n")
        comp = json_response.get("company_name", "")
        return response_text, comp

    def extract_job_description_for_embeddings(self, job_description: str) -> dict:
        """
        Extract and structure job description information optimized for embeddings.
        Returns key components that improve job-to-project matching quality.
        """
        print("Extracting job description with Gemini for embeddings...")
        
        prompt = f"""You will be given a job description text. Extract and structure the following information to optimize it for embedding-based project matching:

    Extract the following fields and return them in JSON format:
    - core_technologies: List of essential technical skills/technologies required (e.g., Python, React, Docker)
    - secondary_technologies: List of nice-to-have or secondary technologies mentioned
    - technical_keywords: List of important technical terms, frameworks, methodologies mentioned
    - experience_level: Required experience level (Junior, Mid-level, Senior, etc.)
    - domain_context: Brief description of the business domain/industry context
    - key_responsibilities: List of main job responsibilities that might match project work
    - soft_skills: Important soft skills mentioned
    - weighted_description: A condensed, keyword-rich version of the job description optimized for embedding matching

    Your response should be in the following format:
    {{
        "core_technologies": ["Technology 1", "Technology 2", ...],
        "secondary_technologies": ["Tech 1", "Tech 2", ...],
        "technical_keywords": ["keyword1", "keyword2", ...],
        "experience_level": "Experience Level",
        "domain_context": "Brief domain description",
        "key_responsibilities": ["responsibility1", "responsibility2", ...],
        "soft_skills": ["skill1", "skill2", ...],
        "weighted_description": "Keyword-rich condensed description for embeddings"
    }}

    Guidelines:
    - Focus on technologies that would be used in actual projects/repositories
    - Normalize technology names (e.g., "React.js" -> "React", "Node.js" -> "Node.js")
    - Include both exact technology names and broader categories
    - The weighted_description should emphasize the most important technical requirements
    - Extract technical methodologies (e.g., "Agile", "TDD", "Microservices")
    - Include relevant technical domains (e.g., "machine learning", "web development", "mobile")

    Job description:
    {job_description}
    """

        response = self.fast_model.generate_content([prompt])
        json_response = self._extract_json(response.text)
        
        return json_response

    def _extract_json(self, text: str) -> dict:
        """
        Extract JSON object from text
        """
        try:        
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = text[json_start:json_end]
                parsed_json = json.loads(json_str)
                return parsed_json
            else:
                print("Warning: Could not find valid JSON in response")
                return {}
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return {}
        except Exception as e:
            print(f"Error extracting JSON: {str(e)}")
            return {}