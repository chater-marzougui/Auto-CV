#!/usr/bin/env python3
"""
Test script to generate and compare cover letters
"""
import sys
import os
sys.path.append('backend')

from backend.app.models.project import CoverLetterRequest, MatchedProject, Project
from backend.app.services.letter_generator import CoverLetterGenerator
from datetime import datetime

def create_test_data():
    """Create sample test data"""
    # Sample projects
    project1 = Project(
        name="E-commerce API",
        url="https://github.com/user/ecommerce-api",
        description="RESTful API for e-commerce platform",
        readme_content="Full-featured e-commerce API built with FastAPI and PostgreSQL",
        three_liner="Developed a comprehensive e-commerce API handling user authentication, product management, and payment processing. Implemented RESTful endpoints with full CRUD operations and integrated secure payment gateways.",
        detailed_paragraph="A comprehensive e-commerce API built with FastAPI, featuring user authentication with JWT tokens, product catalog management, shopping cart functionality, and payment processing integration. The system uses PostgreSQL for data persistence and implements Redis for caching. Features include role-based access control, order management, inventory tracking, and real-time notifications.",
        technologies=["Python", "FastAPI", "PostgreSQL", "Redis", "JWT"],
        tree=["app/", "models/", "routes/", "services/"],
        bad_readme=False,
        no_readme=False,
        stars=45,
        forks=12,
        language="Python",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    project2 = Project(
        name="React Dashboard",
        url="https://github.com/user/react-dashboard",
        description="Modern dashboard built with React and TypeScript",
        readme_content="Admin dashboard with data visualization and user management",
        three_liner="Built a modern admin dashboard using React, TypeScript, and Tailwind CSS. Features real-time data visualization, user management, and responsive design across all device types.",
        detailed_paragraph="A modern, responsive admin dashboard built with React 18, TypeScript, and Tailwind CSS. The dashboard features interactive charts using Chart.js, real-time data updates via WebSocket connections, user role management, and a comprehensive notification system. The application follows modern React patterns including hooks, context API, and component composition.",
        technologies=["React", "TypeScript", "Tailwind CSS", "Chart.js", "WebSocket"],
        tree=["src/", "components/", "hooks/", "utils/"],
        bad_readme=False,
        no_readme=False,
        stars=78,
        forks=23,
        language="TypeScript",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Create matched projects
    matched_projects = [
        MatchedProject(project=project1, similarity_score=0.85),
        MatchedProject(project=project2, similarity_score=0.72)
    ]
    
    return matched_projects

def test_cover_letter_generation():
    """Test the cover letter generation with sample data"""
    print("Testing cover letter generation...")
    
    # Sample job description
    job_description = """
    Senior Full Stack Developer - TechCorp
    
    TechCorp is seeking a Senior Full Stack Developer to join our growing team. 
    
    Requirements:
    - 5+ years experience with Python and JavaScript
    - Experience with FastAPI, React, and PostgreSQL
    - Strong background in API development and frontend frameworks
    - Experience with cloud services and deployment
    
    Responsibilities:
    - Build and maintain scalable web applications
    - Design and implement RESTful APIs
    - Work with cross-functional teams to deliver high-quality products
    - Mentor junior developers and contribute to code reviews
    """
    
    # Sample personal info
    personal_info = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1 (555) 123-4567",
        "title": "Senior Full Stack Developer"
    }
    
    # Create test data
    matched_projects = create_test_data()
    
    # Create cover letter request
    request = CoverLetterRequest(
        job_description=job_description,
        matched_projects=matched_projects,
        personal_info=personal_info
    )
    
    try:
        # Generate cover letter
        print("Generating cover letter...")
        generator = CoverLetterGenerator()
        pdf_path = generator.generate_cover_letter(request)
        
        print(f"Cover letter generated successfully!")
        print(f"PDF saved to: {pdf_path}")
        print(f"Absolute path: {os.path.abspath(pdf_path)}")
        
        # Check if file exists and get size
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"File size: {file_size} bytes")
            return pdf_path
        else:
            print("Error: PDF file not found!")
            return None
            
    except Exception as e:
        print(f"Error generating cover letter: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Note: This test will fail without GEMINI_API_KEY
    # But it will help us test the LaTeX template structure
    test_cover_letter_generation()