# CV Generator Backend

Automatically generate CVs and cover letters based on your GitHub projects and job descriptions using AI-powered project matching.

## Features

- **GitHub Integration**: Scrape all repositories from your GitHub profile
- **AI Project Analysis**: Generate 3-line summaries and detailed paragraphs for each project
- **Smart Matching**: Use embeddings and semantic similarity to match projects to job descriptions
- **LaTeX CV Generation**: Create professional CVs with matched projects
- **Cover Letter Generation**: Generate tailored cover letters for each job application
- **Template Support**: Upload and use custom LaTeX templates
- **RESTful API**: Complete FastAPI backend with comprehensive endpoints

## Architecture

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entrypoint
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── jobs.py          # Job matching endpoints
│   │   └── generate.py      # CV/Cover letter generation
│   ├── services/
│   │   ├── github_scraper.py # GitHub repository scraping
│   │   ├── embeddings.py     # Semantic similarity matching
│   │   ├── cv_generator.py   # LaTeX CV compilation
│   │   └── letter_generator.py # Cover letter generation
│   ├── models/
│   │   └── project.py        # Pydantic data models
│   └── data/
│       └── projects.json     # Cached project data
├── templates/
│   ├── cv_template.tex
│   └── cover_letter_template.tex
├── output/                   # Generated PDFs
├── requirements.txt
└── README.md
```

## Prerequisites

### System Requirements
1. **Python 3.8+**
2. **LaTeX Distribution**:
   - **Ubuntu/Debian**: `sudo apt-get install texlive-latex-base texlive-latex-recommended texlive-latex-extra`
   - **macOS**: `brew install --cask mactex`
   - **Windows**: Install [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/)

### Optional
- **GitHub Personal Access Token** (for higher API rate limits)

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd cv-generator-backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables** (optional):
```bash
export GITHUB_TOKEN="your_github_personal_access_token"
```

5. **Run the application**:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:5000`

## API Documentation

Once running, visit `http://localhost:5000/docs` for interactive API documentation.

### Key Endpoints

#### GitHub Integration
- `POST /api/v1/scrape-github` - Scrape GitHub profile repositories
- `GET /api/v1/projects` - List all scraped projects
- `GET /api/v1/projects/{name}` - Get specific project details

#### Job Matching
- `POST /api/v1/match-projects` - Match projects to job description
- `POST /api/v1/analyze-job` - Analyze job description requirements
- `POST /api/v1/refresh-embeddings` - Refresh project embeddings

#### Generation
- `POST /api/v1/generate-cv` - Generate CV PDF
- `POST /api/v1/generate-cover-letter` - Generate cover letter PDF
- `POST /api/v1/generate-full-application` - Generate both CV and cover letter

#### File Management
- `GET /api/v1/download/{filename}` - Download generated PDFs
- `POST /api/v1/upload-cv-template` - Upload custom CV template
- `GET /api/v1/templates` - List available templates
- `GET /api/v1/output` - List generated files

## Usage Examples

### 1. Scrape GitHub Profile
```bash
curl -X POST "http://localhost:5000/api/v1/scrape-github" \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/username"}'
```

### 2. Match Projects to Job
```bash
curl -X POST "http://localhost:5000/api/v1/match-projects" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Full Stack Developer",
    "company": "Tech Corp",
    "description": "Looking for a developer with Python, React, and API experience..."
  }'
```

### 3. Generate Full Application
```bash
curl -X POST "http://localhost:5000/api/v1/generate-full-application" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": {
      "title": "Software Engineer",
      "company": "StartupXYZ",
      "description": "Python backend developer with FastAPI experience..."
    },
    "personal_info": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "title": "Software Developer",
      "summary": "Experienced software developer with 5+ years..."
    }
  }'
```

## Data Models

### Project Model
```python
{
  "name": "project-name",
  "url": "https://github.com/user/repo",
  "description": "GitHub description",
  "three_liner": "• Concise project summary...",
  "detailed_paragraph": "Detailed project description...",
  "technologies": ["Python", "FastAPI", "React"],
  "stars": 42,
  "forks": 7
}
```

### Personal Info Structure
```python
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": "123 Main St",
  "city": "New York",
  "postal_code": "10001",
  "title": "Software Developer",
  "summary": "Professional summary...",
  "skills": {
    "Programming": ["Python", "JavaScript", "Java"],
    "Frameworks": ["FastAPI", "React", "Django"]
  },
  "experience": [...],
  "education": [...]
}
```

## Customization

### Custom Templates
1. Create LaTeX templates in the `templates/` directory
2. Use Jinja2 template syntax for variable substitution
3. Upload via API or place files directly

### Template Variables
Available in CV templates:
- `{{ personal_info }}` - Personal information
- `{{ projects }}` - Matched projects list
- `{{ projects[0].name }}` - Project name
- `{{ projects[0].technologies|join(', ') }}` - Technologies as comma-separated string

Available in cover letter templates:
- `{{ job.title }}`, `{{ job.company }}` - Job information
- `{{ cover_letter_content.introduction }}` - Generated content sections
- `{{ relevant_skills|join(', ') }}` - Relevant skills

## Configuration

### Environment Variables
- `GITHUB_TOKEN` - GitHub personal access token (optional)
- `MODEL_NAME` - Sentence transformer model (default: "all-MiniLM-L6-v2")

### File Locations
- Project data: `app/data/projects.json`
- Embeddings: `app/data/embeddings.pkl`
- FAISS index: `app/data/faiss_index.bin`
- Templates: `templates/`
- Generated files: `output/`

## Troubleshooting

### Common Issues

1. **LaTeX not found**:
   - Ensure LaTeX is installed and `pdflatex` is in PATH
   - Try: `which pdflatex` (Unix) or `where pdflatex` (Windows)

2. **GitHub rate limiting**:
   - Set up a GitHub personal access token
   - Token provides 5000 requests/hour vs 60 for anonymous

3. **Empty project matches**:
   - Ensure GitHub scraping completed successfully
   - Check if embeddings were generated: `POST /api/v1/refresh-embeddings`

4. **PDF generation fails**:
   - Check LaTeX template syntax
   - Ensure all required LaTeX packages are installed
   - View compilation errors in API response

### Logs and Debugging
- Enable debug logging: `uvicorn app.main:app --reload --log-level debug`
- Check file permissions in `output/` and `templates/` directories
- Verify template syntax with a simple LaTeX compiler test

## Performance Notes

- **Initial scraping**: Takes 1-2 minutes for 20-30 repositories
- **Embedding generation**: ~30 seconds for 50 projects
- **PDF generation**: 2-5 seconds per document
- **Project matching**: <1 second with FAISS indexing

## Security Considerations

- Never commit GitHub tokens to version control
- Sanitize user input in LaTeX templates
- Implement rate limiting for production use
- Consider file size limits for uploads
- Validate file types for template uploads

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black app/
flake8 app/
```

### Adding New Features
1. Create new service in `app/services/`
2. Add corresponding routes in `app/routes/`
3. Update models in `app/models/` if needed
4. Add tests and update documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details.