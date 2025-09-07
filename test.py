#!/usr/bin/env python3
"""
Example usage script for CV Generator Backend
Run this after starting the server to test all functionality
"""

import requests
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:5000"
GITHUB_USERNAME = "chater-marzougui"  # Change this to your GitHub username

# Sample personal information
PERSONAL_INFO = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123",
    "address": "123 Tech Street",
    "city": "San Francisco",
    "postal_code": "94105",
    "title": "Software Developer",
    "summary": "Experienced software developer with 5+ years of experience in full-stack development, specializing in Python, JavaScript, and modern web technologies. Passionate about creating efficient, scalable solutions and contributing to open-source projects.",
    "skills": {
        "Programming Languages": ["Python", "JavaScript", "TypeScript", "Java"],
        "Web Frameworks": ["FastAPI", "React", "Django", "Express.js"],
        "Databases": ["PostgreSQL", "MongoDB", "Redis"],
        "Tools & Technologies": ["Docker", "Git", "AWS", "Linux"]
    },
    "experience": [
        {
            "title": "Senior Software Developer",
            "company": "Tech Solutions Inc.",
            "location": "San Francisco, CA",
            "start_date": "2020-01",
            "end_date": "Present",
            "description": "Lead full-stack development projects and mentor junior developers",
            "achievements": [
                "Reduced application load time by 40% through optimization",
                "Led team of 4 developers on major product redesign",
                "Implemented CI/CD pipeline reducing deployment time by 60%"
            ]
        }
    ],
    "education": [
        {
            "degree": "Bachelor of Science in Computer Science",
            "institution": "University of Technology",
            "location": "California, USA",
            "start_date": "2016",
            "end_date": "2020",
            "gpa": "3.8/4.0",
            "description": "Focus on software engineering and data structures"
        }
    ]
}

# Sample job description
JOB_DESCRIPTION = {
    "title": "Full Stack Developer",
    "company": "InnovateTech Solutions",
    "description": """
    We are looking for a talented Full Stack Developer to join our growing team. 
    The ideal candidate will have experience with Python, React, and modern web technologies.
    
    Responsibilities:
    - Develop and maintain web applications using Python and JavaScript
    - Work with databases and API development
    - Collaborate with cross-functional teams
    - Write clean, maintainable code
    - Participate in code reviews and technical discussions
    
    Requirements:
    - 3+ years of experience in software development
    - Strong proficiency in Python and JavaScript
    - Experience with React and modern frontend frameworks
    - Knowledge of RESTful APIs and database design
    - Familiarity with version control (Git)
    - Experience with cloud platforms (AWS, Azure, or GCP)
    """,
    "requirements": """
    Required Skills:
    - Python (Django, FastAPI, or Flask)
    - JavaScript/TypeScript
    - React or similar frontend framework
    - SQL and database design
    - Git version control
    - RESTful API development
    
    Preferred Skills:
    - Docker containerization
    - Cloud deployment experience
    - Agile development methodologies
    - Unit testing and TDD
    """
}

def make_request(method: str, endpoint: str, data: Dict[Any, Any] = None) -> Dict[Any, Any]:
    """Make HTTP request and handle response"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return {}

def test_health_check():
    """Test if the API is running"""
    print("🏥 Testing health check...")
    result = make_request("GET", "/health")
    if result.get("status") == "healthy":
        print("✅ API is healthy")
        return True
    else:
        print("❌ API health check failed")
        return False

def scrape_github_profile():
    """Scrape GitHub profile"""
    print(f"🔍 Scraping GitHub profile: {GITHUB_USERNAME}")
    
    # Note: The API expects a full GitHub URL
    result = make_request("POST", "/api/v1/scrape-github", {"github_username": GITHUB_USERNAME})
    
    if result.get("projects_count"):
        print(f"✅ Successfully scraped {result['projects_count']} projects")
        return True
    else:
        print("❌ Failed to scrape GitHub profile")
        return False

def list_projects():
    """List all scraped projects"""
    print("📋 Listing all projects...")
    
    result = make_request("GET", "/api/v1/projects")
    
    if result.get("total_projects"):
        print(f"✅ Found {result['total_projects']} projects:")
        for project in result.get("projects", [])[:3]:  # Show first 3
            print(f"   • {project['name']}: {project.get('description', 'No description')[:50]}...")
        return True
    else:
        print("❌ No projects found")
        return False

def match_projects_to_job():
    """Match projects to job description"""
    print("🎯 Matching projects to job description...")
    
    result = make_request("POST", "/api/v1/match-projects", JOB_DESCRIPTION)
    
    if result:
        print(f"✅ Found {len(result)} matching projects:")
        for i, match in enumerate(result, 1):
            project = match["project"]
            score = match["similarity_score"]
            print(f"{project['name']} (Score: {score:.3f})")
        return result
    else:
        print("❌ Failed to match projects")
        return []

def analyze_job_description():
    """Analyze job description"""
    print("🔍 Analyzing job description...")
    
    result = make_request("POST", "/api/v1/analyze-job", JOB_DESCRIPTION)
    
    if result:
        print("✅ Job analysis complete:")
        print(f"   Required technologies: {', '.join(result.get('required_technologies', []))}")
        print(f"   Experience level: {result.get('experience_level', 'Not specified')}")
        print(f"   Summary: {result.get('analysis_summary', 'No summary')}")
        return True
    else:
        print("❌ Failed to analyze job description")
        return False

def generate_full_application():
    """Generate complete job application"""
    print("📄 Generating full application (CV + Cover Letter)...")
    
    request_data = {
        "job_description": JOB_DESCRIPTION,
        "personal_info": PERSONAL_INFO,
        "top_k": 4
    }
    
    result = make_request("POST", "/api/v1/generate-full-application", request_data)
    
    if result.get("message") == "Full application generated successfully":
        print("✅ Full application generated!")
        print(f"   CV: {result['cv']['download_url']}")
        print(f"   Cover Letter: {result['cover_letter']['download_url']}")
        print("   Matched projects:")
        for project in result.get("matched_projects", []):
            print(f"      • {project['name']} (Score: {project['similarity_score']:.3f})")
        return True
    else:
        print("❌ Failed to generate application")
        print(f"Error: {result}")
        return False

def list_generated_files():
    """List generated files"""
    print("📁 Listing generated files...")
    
    result = make_request("GET", "/api/v1/output")
    
    if result.get("files"):
        print(f"✅ Found {len(result['files'])} generated files:")
        for file_info in result["files"]:
            print(f"   • {file_info['filename']} ({file_info['size_bytes']} bytes)")
            print(f"     Download: {BASE_URL}{file_info['download_url']}")
        return True
    else:
        print("❌ No generated files found")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting CV Generator Backend Test Suite")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health_check():
        print("❌ Server is not running. Please start with: uvicorn app.main:app --reload")
        return
    
    print()
    
    # Test 2: Scrape GitHub (this takes time)
    print("⚠️  GitHub scraping may take 1-2 minutes...")
    scrape_result = scrape_github_profile()
    
    if scrape_result:
        # Wait a moment for processing
        print("⏳ Waiting for processing to complete...")
        time.sleep(3)
    
    print()
    
    # Test 3: List projects
    list_projects()
    print()
    # Test 4: Analyze job
    analyze_job_description()
    print()
    
    # Test 5: Match projects
    matched_projects = match_projects_to_job()
    
    # Test 6: Generate application (only if we have matches)
    if matched_projects:
        print("⚠️  PDF generation may take 30-60 seconds...")
        generate_full_application()
        print()
        
        # Test 7: List generated files
        list_generated_files()
    else:
        print("⚠️  Skipping PDF generation due to no project matches")
    
    print()
    print("🎉 Test suite completed!")
    print("💡 Visit http://localhost:5000/docs for interactive API documentation")

if __name__ == "__main__":
    main()