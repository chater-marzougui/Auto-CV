<a name="readme-top"></a>

<div align="center">

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
</div>

---

# 🛠️ Auto-CV

**AI-powered CV and cover letter generator that automatically creates tailored applications based on your GitHub projects and job descriptions.**
Built with ❤️ by [Chater Marzougui](https://github.com/chater-marzougui).

<br />
<div align="center">
  <a href="https://github.com/chater-marzougui/Auto-CV">
     <img src="https://img.shields.io/badge/Auto--CV-AI%20Powered-blue?style=for-the-badge&logo=github" alt="Auto-CV Logo" width="256" height="64">
  </a>
  <h3>Auto-CV</h3>
  <p align="center">
    <strong>Automatically generate professional CVs and cover letters with AI-powered project matching</strong>
    <br />
    <br />
    <a href="https://github.com/chater-marzougui/Auto-CV/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/chater-marzougui/Auto-CV/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
      </p>
</div>

<br/>

---

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#-features">Features</a></li>
    <li><a href="#-getting-started">Getting Started</a></li>
    <li><a href="#-installation">Installation</a></li>
    <li><a href="#-usage">Usage</a></li>
    <li><a href="#-configuration">Configuration</a></li>
    <li><a href="#-contributing">Contributing</a></li>
    <li><a href="#-license">License</a></li>
     <li><a href="#-contact">Contact</a></li>
  </ol>
</details>

<div align="right">
  <a href="#readme-top">
    <img src="https://img.shields.io/badge/Back_to_Top-⬆️-blue?style=for-the-badge" alt="Back to Top">
  </a>
</div>

---

## About The Project

**🚀 Auto-CV** is a comprehensive AI-powered application that revolutionizes the job application process by automatically generating professional CVs and cover letters tailored to specific job descriptions. The system intelligently analyzes your GitHub projects, matches them to job requirements using semantic similarity, and creates compelling application documents using LaTeX generation.

### 🎯 Key Features

- 🔧 **GitHub Integration**: Automatically scrapes and analyzes all repositories from your GitHub profile
- 🤖 **AI-Powered Analysis**: Uses Google Gemini AI to generate compelling project summaries and descriptions  
- ⚡ **Smart Project Matching**: Employs sentence transformers and FAISS indexing for semantic similarity matching
- 🌐 **Real-time Progress**: WebSocket-powered live updates during the scraping and generation process
- 📝 **LaTeX Document Generation**: Professional CV and cover letter creation with customizable templates
- 🎨 **Modern Web Interface**: React TypeScript frontend with Tailwind CSS and Radix UI components
- 📊 **REST API**: Comprehensive FastAPI backend with full documentation and testing support
- 💾 **Database Storage**: SQLite database for storing personal information and job application history
- 📋 **Application Tracking**: Track all job applications with generated CV and cover letter links

<div align="right">
  <a href="#readme-top">
    <img src="https://img.shields.io/badge/Back_to_Top-⬆️-blue?style=for-the-badge" alt="Back to Top">
  </a>
</div>

---

## ⚡ Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - Backend development
- **Node.js 16+** - Frontend development  
- **LaTeX Distribution** - Document generation
  - **Ubuntu/Debian**: `sudo apt-get install texlive-latex-base texlive-latex-recommended texlive-latex-extra`
  - **macOS**: `brew install --cask mactex`
  - **Windows**: Install [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/)
- **Google Gemini API Key** - AI analysis (optional but recommended)
- **GitHub Personal Access Token** - Higher API rate limits (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/chater-marzougui/Auto-CV.git
cd Auto-CV
```

2. **Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
echo "GITHUB_TOKEN=your_github_token_here" > .env
echo "GEMINI_API_KEY=your_gemini_api_key_here" >> .env
```

3. **Frontend Setup**
```bash
cd ../frontend

# Install dependencies
npm install

# Build the project
npm run build
```

4. **Start the Application**
```bash
# Start backend (from backend directory)
cd ../backend
python main.py

# Start frontend (from frontend directory, in another terminal)
cd ../frontend  
npm run dev
```

The application will be available at:
- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:5000`
- **API Documentation**: `http://localhost:5000/docs`

<div align="right">
  <a href="#readme-top">
    <img src="https://img.shields.io/badge/Back_to_Top-⬆️-blue?style=for-the-badge" alt="Back to Top">
  </a>
</div>

---

## 📚 Usage

### Web Interface

1. **GitHub Analysis**: Enter your GitHub username to scrape and analyze all repositories
2. **Job Description Input**: Paste the job description you're applying for
3. **Project Matching**: View automatically matched projects based on semantic similarity
4. **Document Generation**: Generate professional CV and cover letter with one click

### API Usage

#### Scrape GitHub Profile
```bash
curl -X POST "http://localhost:5000/api/v1/scrape-github" \
  -H "Content-Type: application/json" \
  -d '{"github_username": "your-username"}'
```

#### Match Projects to Job
```bash
curl -X POST "http://localhost:5000/api/v1/match-projects" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Full Stack Developer",
    "company": "Tech Corp", 
    "description": "Looking for a developer with Python, React, and API experience..."
  }'
```

#### Generate Full Application
```bash
curl -X POST "http://localhost:5000/api/v1/generate-full-application" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": {
      "title": "Software Engineer",
      "company": "StartupXYZ",
      "description": "Python backend developer with FastAPI experience..."
    },
    "personal_info_id": 1
  }'
```

#### Manage Personal Information
```bash
# Create personal info
curl -X POST "http://localhost:5000/api/v1/personal-info/" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "title": "Software Developer",
    "summary": "Experienced software developer with 5+ years..."
  }'

# Update personal info
curl -X PUT "http://localhost:5000/api/v1/personal-info/1" \
  -H "Content-Type: application/json" \
  -d '{"title": "Senior Software Developer"}'

# Get personal info
curl "http://localhost:5000/api/v1/personal-info/1"
```

#### Track Job Applications
```bash
# Create job application
curl -X POST "http://localhost:5000/api/v1/job-applications/" \
  -H "Content-Type: application/json" \
  -d '{
    "personal_info_id": 1,
    "job_title": "Full Stack Developer", 
    "company_name": "TechCorp",
    "job_description": "Looking for a developer...",
    "status": "applied"
  }'

# Get job applications for a person
curl "http://localhost:5000/api/v1/personal-info/1/job-applications"
```

<div align="right">
  <a href="#readme-top">
    <img src="https://img.shields.io/badge/Back_to_Top-⬆️-blue?style=for-the-badge" alt="Back to Top">
  </a>
</div>

---

## 🪛 Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# GitHub API (optional - for higher rate limits)
GITHUB_TOKEN=your_github_personal_access_token

# Google Gemini AI (optional - for enhanced project analysis)
GEMINI_API_KEY=your_gemini_api_key

# Model Configuration
MODEL_NAME=all-MiniLM-L6-v2

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
```

### Custom Templates

1. **CV Templates**: Place custom LaTeX templates in `backend/templates/`
2. **Template Variables**: Use Jinja2 syntax for dynamic content
   - `{{ personal_info.first_name }}` - Personal information
   - `{{ projects }}` - Matched projects array
   - `{{ projects[0].technologies|join(', ') }}` - Project technologies

### File Structure
```
Auto-CV/
├── backend/
│   ├── app/
│   │   ├── database/         # Database models and CRUD operations
│   │   │   ├── models.py     # SQLAlchemy models
│   │   │   ├── schemas.py    # Pydantic schemas
│   │   │   ├── crud.py       # Database operations
│   │   │   └── database.py   # Database connection
│   │   ├── services/         # Core business logic
│   │   ├── routes/           # API endpoints
│   │   │   ├── personal_info.py        # Personal info management
│   │   │   ├── job_applications.py     # Job application tracking
│   │   │   ├── generate.py             # CV/Cover letter generation
│   │   │   └── jobs.py                 # Project matching
│   │   ├── models/           # Data models
│   │   └── data/             # Generated data and embeddings
│   ├── templates/            # LaTeX templates
│   ├── output/               # Generated PDFs
│   ├── app_data.db           # SQLite database
│   └── main.py               # FastAPI application
├── frontend/
│   └── src/
│       ├── components/       # React components
│       └── hooks/            # Custom React hooks
└── package.json             # Root package configuration
```

<div align="right">
  <a href="#readme-top">
    <img src="https://img.shields.io/badge/Back_to_Top-⬆️-blue?style=for-the-badge" alt="Back to Top">
  </a>
</div>

---

## 🤝 Contributing

Contributions are what make the open source community amazing! Any contributions are **greatly appreciated**.

### How to Contribute

1. **Fork the Project**
2. **Create your Feature Branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your Changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the Branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Development Setup

```bash
# Backend development
cd backend
pip install -r requirements.txt
python main.py

# Frontend development  
cd frontend
npm install
npm run dev

# Run tests
cd backend && python -m pytest tests/
cd frontend && npm test
```

<div align="right">
  <a href="#readme-top">
    <img src="https://img.shields.io/badge/Back_to_Top-⬆️-blue?style=for-the-badge" alt="Back to Top">
  </a>
</div>

---

## 📃 License

Distributed under the MIT License. See `LICENSE` for more information.

<div align="right">
  <a href="#readme-top">
    <img src="https://img.shields.io/badge/Back_to_Top-⬆️-blue?style=for-the-badge" alt="Back to Top">
  </a>
</div>

---

## 📧 Contact

**Chater Marzougui** - [@chater-marzougui](https://github.com/chater-marzougui) - [LinkedIn](https://www.linkedin.com/in/chater-marzougui-342125299/)

Project Link: [https://github.com/chater-marzougui/Auto-CV](https://github.com/chater-marzougui/Auto-CV)

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - Frontend library
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Radix UI](https://www.radix-ui.com/) - Accessible component library
- [Sentence Transformers](https://www.sbert.net/) - Semantic similarity matching
- [Google Gemini AI](https://ai.google.dev/) - Advanced AI analysis
- [FAISS](https://faiss.ai/) - Efficient similarity search
- [PyGithub](https://pygithub.readthedocs.io/) - GitHub API integration

<div align="right">
  <a href="#readme-top">
    <img src="https://img.shields.io/badge/Back_to_Top-⬆️-blue?style=for-the-badge" alt="Back to Top">
  </a>
</div>

---

**Revolutionize your job applications with AI-powered CV generation.**


[contributors-shield]: https://img.shields.io/github/contributors/chater-marzougui/Auto-CV.svg?style=for-the-badge
[contributors-url]: https://github.com/chater-marzougui/Auto-CV/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/chater-marzougui/Auto-CV.svg?style=for-the-badge
[forks-url]: https://github.com/chater-marzougui/Auto-CV/network/members
[stars-shield]: https://img.shields.io/github/stars/chater-marzougui/Auto-CV.svg?style=for-the-badge
[stars-url]: https://github.com/chater-marzougui/Auto-CV/stargazers
[issues-shield]: https://img.shields.io/github/issues/chater-marzougui/Auto-CV.svg?style=for-the-badge
[issues-url]: https://github.com/chater-marzougui/Auto-CV/issues
[license-shield]: https://img.shields.io/github/license/chater-marzougui/Auto-CV.svg?style=for-the-badge
[license-url]: https://github.com/chater-marzougui/Auto-CV/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/chater-marzougui-342125299/