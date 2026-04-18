# DevCareer Intelligence - Developer Career Audit System

A comprehensive platform that performs a brutally honest 360-degree audit of a developer's demonstrated skills versus their claimed experience by analyzing GitHub profiles, project links, and live application URLs.

## Live Demo

**Frontend Dashboard:** https://i5vrmoh7lx742.kimi.page

> The deployed frontend includes a complete mock data demo. Enter any GitHub username to see the full dashboard in action.

## Architecture

```
devcareer-audit/
├── backend/           # Python Flask API
│   ├── app.py                 # Main Flask application & API endpoints
│   ├── github_analyzer.py     # GitHub API integration & profile analysis
│   ├── code_quality.py        # Code quality analysis engine
│   ├── live_app_audit.py      # Live application UI/UX auditing
│   ├── security_scanner.py    # Security anti-pattern detection
│   ├── market_engine.py       # Job market comparison engine
│   ├── resume_rewriter.py     # Resume bullet generator
│   ├── roadmap_generator.py   # 90-day learning roadmap
│   ├── scoring.py             # Scoring system & level determination
│   └── requirements.txt       # Python dependencies
│
└── frontend/          # HTML/CSS/JS Dashboard
    ├── index.html             # Main HTML structure
    ├── css/
    │   └── style.css          # Dark theme dashboard styles
    └── js/
        └── app.js             # Frontend application logic
```

## Backend API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/audit` | Start a comprehensive audit |
| GET | `/api/audit/<id>` | Get audit results & progress |
| GET | `/api/audit/<id>/feedback` | Get specific actionable feedback |
| POST | `/api/rewrite-resume` | Generate resume bullet points |
| GET | `/api/market-data` | Get current job market data |
| GET | `/api/roadmap/<id>` | Get 90-day learning roadmap |

## Core Features

### 1. GitHub Profile Ingestion
- Input field for GitHub username or repository URLs
- Fetches complete activity history, all public repositories, commit patterns, and contribution graphs
- Detects tech stack, frameworks, and language breakdown

### 2. Code Quality Analysis
Analyzes every repository for:
- **Modularity** - component/file organization, separation of concerns
- **Test coverage** - presence of test files, test-to-code ratios
- **Documentation completeness** - README quality, inline comments, API docs
- **Naming conventions** - consistency, clarity, industry standards
- **Architectural patterns** - MVC, microservices, proper abstraction layers
- **Code smells** - over-engineered solutions, anti-patterns, copy-pasted code

### 3. Live Application Audit (if URL provided)
Automated UI/UX testing for:
- Responsiveness across screen sizes
- Accessibility scores (WCAG compliance)
- Load times and performance metrics
- Animation smoothness (60fps checks)
- Interaction feedback quality

### 4. Security & Quality Scan
Detects:
- Hardcoded secrets and credentials
- SQL injection vulnerabilities
- XSS vulnerabilities
- CORS misconfigurations
- Insecure transport (HTTP)
- Weak cryptography
- Missing authentication

### 5. Market Comparison Engine
Cross-references developer's real skill level against current job market:
- Which roles they actually qualify for today
- Specific companies that would realistically hire them
- Percentile ranking among comparable developers
- Precise skills gap between current abilities and next salary bracket
- Salary estimates in USD and EGP

### 6. Specific Actionable Feedback
Replace generic advice with exact, traceable issues:
- File and line-level precision
- Severity classification (critical/warning/info)
- Specific fix recommendations
- Impact statements (e.g., "fixing this moves you from junior to mid-level")

### 7. 90-Day Learning Roadmap
Personalized improvement plan that:
- Attacks weakest skills first based on audit findings
- Identifies which projects to lead vs. remove from resume
- Provides week-by-week goals with measurable milestones
- Includes learning resources (courses, books, practice projects)

### 8. Resume Rewriter
Auto-generates bullet points based on actual code found:
- Highlights demonstrated strengths
- Omits unverified claims
- Provides specific recommendations for improvement

### 9. Scoring System
- Rates each dimension 1-10
- Weights by role type (frontend-heavy vs backend-heavy vs fullstack)
- Calculates overall demonstrated level: junior/mid/senior/staff
- Based on actual evidence, not self-reporting

## Running Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The API will be available at `http://localhost:5000`

### Frontend

The Flask backend serves the frontend automatically at `http://localhost:5000`

Alternatively, open `frontend/index.html` directly in a browser (mock data will be used).

### With Environment Variables

```bash
export GITHUB_TOKEN="your_github_token"  # Optional - increases rate limits
export PORT=5000                           # Optional - default is 5000
python backend/app.py
```

## Tech Stack

- **Frontend:** HTML5, CSS3, Vanilla JavaScript (no frameworks)
- **Backend:** Python 3.8+, Flask, Flask-CORS
- **External APIs:** GitHub REST API
- **Data Sources:** GitHub API, job board APIs, Puppeteer/Playwright (for live audits)

## Design Decisions

1. **Vanilla JS Frontend** - No build step required, fast loading, easy to customize
2. **Flask Backend** - Lightweight, easy to run locally, well-documented
3. **In-Memory Storage** - Simple for demo; swap for Redis in production
4. **Mock Data Fallback** - Frontend works standalone with realistic demo data
5. **Dark Theme** - Professional developer aesthetic, reduces eye strain
6. **Modular Backend** - Each analysis engine is independent and testable
