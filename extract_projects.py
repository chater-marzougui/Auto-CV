import json
from pathlib import Path

def extract_project_fields(input_file: str, output_file: str):
    """
    Load projects.json and create a smaller version with selected fields.
    
    Args:
        input_file: Path to the input JSON file
        output_file: Path to the output JSON file
    """
    # Read the input JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        projects = json.load(f)
    
    # Extract only the required fields
    extracted_projects = []
    for project in projects:
        extracted_project = {
            "name": project.get("name"),
            "suggested_name": project.get("suggested_name"),
            "url": project.get("url"),
            "technologies": project.get("technologies", []),
            "detailed_paragraph": project.get("detailed_paragraph"),
            "language": project.get("language")
        }
        extracted_projects.append(extracted_project)
    
    # Write to the output JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_projects, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully extracted {len(extracted_projects)} projects")
    print(f"✓ Output saved to: {output_file}")

if __name__ == "__main__":
    # Define file paths
    input_file = Path("backend/app/data/projects.json")
    output_file = Path("backend/app/data/projects_minimal.json")
    
    # Run the extraction
    extract_project_fields(input_file, output_file)
