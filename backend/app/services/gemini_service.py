import google.generativeai as genai
import os
import re
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

    Your response for each question should be in the following format:
    {{
        "detailed": "Detailed paragraph here",
        "three_liner": "3-liner paragraph (no return to line) summary here it should be a short and straight to the point",
        "technologies": ["Technology 1", "Technology 2", ...]
    }}

    The response should adhere to the following:
    - Only the json response should be returned no other data.
    - The 3 liner will be used in a CV so format it to be unambiguous and impactful and straight to the point (no long lines).
    - The detailed paragraph should provide a comprehensive overview of the project.
    - in the three liner don't include the project name start directly.
    - The technologies should be a list of key technologies used in the project (e.g., React, Node.js).
    - Ensure the JSON is properly formatted.
    
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
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
        except Exception as e:
            print(f"Error extracting JSON: {str(e)}")
        