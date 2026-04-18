"""
Developer Career Intelligence System - Backend API
A comprehensive platform for auditing developer skills vs. claimed experience.
"""

import os
import uuid
import hashlib
import time
import re
import json
from datetime import datetime, timedelta
import concurrent.futures

from flask import Flask, request, jsonify
from flask_cors import CORS

# Import analysis modules
from github_analyzer import GitHubAnalyzer
from code_quality import CodeQualityAnalyzer
from live_app_audit import LiveAppAuditor
# from security_scanner import SecurityScanner
from market_engine import MarketComparisonEngine
from resume_rewriter import ResumeRewriter
from roadmap_generator import RoadmapGenerator
from scoring import ScoringEngine

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# In-memory store for audit results (use Redis in production)
audit_store = {}
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# Initialize engines
scoring_engine = ScoringEngine()
market_engine = MarketComparisonEngine()
resume_rewriter = ResumeRewriter()
roadmap_generator = RoadmapGenerator()


@app.route('/')
def serve_index():
    """Serve the frontend application."""
    return app.send_static_file('index.html')


def generate_audit_id(data):
    """Generate a unique audit ID based on input data."""
    content = f"{data.get('github_username','')}-{data.get('portfolio_url','')}-{time.time()}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})


@app.route('/api/audit', methods=['POST'])
def start_audit():
    """
    Start a comprehensive developer career audit.
    
    Request body:
    {
        "github_username": "string (required)",
        "portfolio_url": "string (optional)",
        "claimed_role": "string (e.g., 'Senior Full-Stack Developer')",
        "claimed_years": "number",
        "claimed_skills": ["skill1", "skill2"],
        "target_role": "string (optional)",
        "location": "string (optional, e.g., 'Remote', 'San Francisco')"
    }
    """
    data = request.get_json()
    
    if not data or not data.get('github_username'):
        return jsonify({"error": "GitHub username is required"}), 400
    
    audit_id = generate_audit_id(data)
    
    # Store initial audit record
    audit_store[audit_id] = {
        "id": audit_id,
        "status": "processing",
        "progress": 0,
        "created_at": datetime.utcnow().isoformat(),
        "input": data,
        "results": None
    }
    
    # Start async analysis
    executor.submit(run_full_audit, audit_id, data)
    
    return jsonify({
        "audit_id": audit_id,
        "status": "processing",
        "message": "Audit started. Poll /api/audit/{id} for results."
    }), 202


def run_full_audit(audit_id, data):
    """Run the complete audit pipeline."""
    try:
        audit = audit_store[audit_id]
        github_username = data.get('github_username')
        portfolio_url = data.get('portfolio_url')
        claimed_role = data.get('claimed_role', 'Developer')
        claimed_years = data.get('claimed_years', 0)
        claimed_skills = data.get('claimed_skills', [])
        target_role = data.get('target_role', claimed_role)
        location = data.get('location', 'Remote')
        
        # Phase 1: GitHub Profile Analysis (0-25%)
        audit['progress'] = 5
        gh_analyzer = GitHubAnalyzer(github_username)
        github_data = gh_analyzer.analyze_profile()
        audit['progress'] = 25
        
        # Phase 2: Code Quality Analysis (25-50%)
        audit['progress'] = 30
        code_analyzer = CodeQualityAnalyzer(github_data)
        code_quality = code_analyzer.analyze_all_repos()
        audit['progress'] = 50
        
        # Phase 3: Live App Audit (50-60%)
        audit['progress'] = 55
        live_audit = {"performed": False}
        if portfolio_url:
            app_auditor = LiveAppAuditor(portfolio_url)
            live_audit = app_auditor.audit()
            live_audit['performed'] = True
        audit['progress'] = 60
        
        # Phase 4: Security Scan (60-70%)
        audit['progress'] = 65
        # security_scanner = SecurityScanner(github_data, code_quality)
        # security_results = security_scanner.scan()
        security_results = {}  # Placeholder for security results
        audit['progress'] = 70
        
        # Phase 5: Scoring (70-75%)
        audit['progress'] = 72
        scores = scoring_engine.calculate_all_scores(
            github_data, code_quality, live_audit, security_results,
            claimed_role, claimed_years
        )
        audit['progress'] = 75
        
        # Phase 6: Market Comparison (75-85%)
        audit['progress'] = 80
        market_comparison = market_engine.compare(
            scores, claimed_role, claimed_years, claimed_skills,
            target_role, location
        )
        audit['progress'] = 85
        
        # Phase 7: Generate Feedback & Roadmap (85-95%)
        audit['progress'] = 88
        feedback = generate_actionable_feedback(
            github_data, code_quality, security_results, scores
        )
        audit['progress'] = 90
        
        roadmap = roadmap_generator.generate(
            scores, feedback, market_comparison, target_role
        )
        audit['progress'] = 93
        
        resume_bullets = resume_rewriter.generate_bullets(
            github_data, code_quality, scores
        )
        audit['progress'] = 95
        
        # Phase 8: Compile final results (95-100%)
        audit['progress'] = 100
        audit['status'] = 'completed'
        audit['results'] = {
            "summary": {
                "audit_id": audit_id,
                "audited_at": datetime.utcnow().isoformat(),
                "github_username": github_username,
                "claimed_role": claimed_role,
                "claimed_years": claimed_years,
                "demonstrated_level": scores['overall_level'],
                "level_match": scores['level_match'],
                "overall_score": scores['overall_score'],
                "critical_issues_count": len([f for f in feedback if f.get('severity') == 'critical']),
                "warnings_count": len([f for f in feedback if f.get('severity') == 'warning']),
                "market_position": market_comparison['percentile'],
                "interview_success_rate": market_comparison['interview_success_rate']
            },
            "scores": scores,
            "github_profile": github_data,
            "code_quality": code_quality,
            "live_app_audit": live_audit,
            "security_scan": security_results,
            "market_comparison": market_comparison,
            "feedback": feedback,
            "roadmap": roadmap,
            "resume_bullets": resume_bullets
        }
        
    except Exception as e:
        audit['status'] = 'error'
        audit['error'] = str(e)
        audit['results'] = {"error": str(e)}


def generate_actionable_feedback(github_data, code_quality, security_results, scores):
    """Generate specific, actionable feedback items."""
    feedback = []
    
    # Test coverage feedback
    for repo in code_quality.get('repo_analysis', []):
        if repo.get('test_coverage', 0) < 20:
            feedback.append({
                "severity": "critical",
                "category": "Testing",
                "repo": repo.get('name'),
                "message": f"Repository '{repo.get('name')}' has virtually no tests ({repo.get('test_coverage', 0):.1f}% coverage). A senior engineer would reject PRs without tests.",
                "fix": f"Add unit tests for all service layers in {repo.get('name')}. Target 70%+ coverage.",
                "impact": "Moves you from junior to mid-level"
            })
        elif repo.get('test_coverage', 0) < 50:
            feedback.append({
                "severity": "warning",
                "category": "Testing",
                "repo": repo.get('name'),
                "message": f"Repository '{repo.get('name')}' has insufficient test coverage ({repo.get('test_coverage', 0):.1f}%).",
                "fix": f"Increase test coverage in {repo.get('name')} to at least 70%.",
                "impact": "Shows engineering maturity"
            })
    
    # Documentation feedback
    for repo in code_quality.get('repo_analysis', []):
        if repo.get('has_readme', False) and repo.get('readme_quality', 0) < 40:
            feedback.append({
                "severity": "warning",
                "category": "Documentation",
                "repo": repo.get('name'),
                "message": f"README in '{repo.get('name')}' is minimal. Recruiters and senior engineers judge projects by README quality.",
                "fix": "Add setup instructions, architecture overview, screenshots, and API documentation.",
                "impact": "Increases project credibility by 3x"
            })
        if not repo.get('has_readme', False):
            feedback.append({
                "severity": "critical",
                "category": "Documentation",
                "repo": repo.get('name'),
                "message": f"Repository '{repo.get('name')}' has no README. This is a red flag for any hiring manager.",
                "fix": "Create a comprehensive README with project description, setup guide, and screenshots.",
                "impact": "Basic requirement for portfolio projects"
            })
    
    # Security issues
    for issue in security_results.get('issues', []):
        if issue.get('severity') == 'critical':
            feedback.append({
                "severity": "critical",
                "category": "Security",
                "repo": issue.get('repo', 'unknown'),
                "file": issue.get('file', ''),
                "message": issue.get('description', 'Security issue found'),
                "fix": issue.get('recommendation', 'Fix immediately'),
                "impact": "Blocking issue for any production role"
            })
    
    # Commit pattern feedback
    commit_patterns = github_data.get('commit_patterns', {})
    if commit_patterns.get('avg_commits_per_week', 0) < 3:
        feedback.append({
            "severity": "warning",
            "category": "Consistency",
            "message": "Low commit frequency detected. Consistent coding practice is key to skill development.",
            "fix": "Commit code daily, even for small changes. Build the habit of incremental progress.",
            "impact": "Demonstrates professional work ethic"
        })
    
    # Code smell feedback
    for repo in code_quality.get('repo_analysis', []):
        for smell in repo.get('code_smells', []):
            feedback.append({
                "severity": smell.get('severity', 'warning'),
                "category": "Code Quality",
                "repo": repo.get('name'),
                "file": smell.get('file', ''),
                "message": smell.get('description', ''),
                "fix": smell.get('recommendation', 'Refactor this code'),
                "impact": smell.get('impact', 'Improves code maintainability')
            })
    
    # Architectural feedback
    for repo in code_quality.get('repo_analysis', []):
        arch_score = repo.get('architecture_score', 0)
        if arch_score < 40:
            feedback.append({
                "severity": "critical" if arch_score < 20 else "warning",
                "category": "Architecture",
                "repo": repo.get('name'),
                "message": f"Repository '{repo.get('name')}' shows poor architectural organization (score: {arch_score:.1f}/100).",
                "fix": "Implement proper separation of concerns. Separate controllers, services, and data access layers.",
                "impact": "Key differentiator between junior and senior developers"
            })
    
    return feedback


@app.route('/api/audit/<audit_id>', methods=['GET'])
def get_audit_results(audit_id):
    """Get audit results by ID."""
    if audit_id not in audit_store:
        return jsonify({"error": "Audit not found"}), 404
    
    audit = audit_store[audit_id]
    return jsonify({
        "audit_id": audit_id,
        "status": audit['status'],
        "progress": audit['progress'],
        "results": audit.get('results'),
        "error": audit.get('error')
    })


@app.route('/api/audit/<audit_id>/feedback', methods=['GET'])
def get_feedback(audit_id):
    """Get specific actionable feedback for an audit."""
    if audit_id not in audit_store:
        return jsonify({"error": "Audit not found"}), 404
    
    audit = audit_store[audit_id]
    if audit['status'] != 'completed':
        return jsonify({"error": "Audit not completed"}), 400
    
    return jsonify({
        "feedback": audit['results']['feedback'],
        "total_issues": len(audit['results']['feedback']),
        "critical_count": len([f for f in audit['results']['feedback'] if f.get('severity') == 'critical']),
        "warning_count": len([f for f in audit['results']['feedback'] if f.get('severity') == 'warning'])
    })


@app.route('/api/rewrite-resume', methods=['POST'])
def rewrite_resume():
    """
    Generate resume bullet points based on actual code analysis.
    
    Request body:
    {
        "audit_id": "string (optional - uses existing audit)",
        "github_username": "string (if no audit_id)",
        "tone": "string (professional|technical|executive, default: professional)"
    }
    """
    data = request.get_json()
    audit_id = data.get('audit_id')
    tone = data.get('tone', 'professional')
    
    if audit_id and audit_id in audit_store:
        audit = audit_store[audit_id]
        if audit['status'] == 'completed':
            bullets = audit['results']['resume_bullets']
            return jsonify({"bullets": bullets, "source": "audit_analysis"})
    
    # Fresh analysis
    github_username = data.get('github_username')
    if not github_username:
        return jsonify({"error": "GitHub username or audit_id required"}), 400
    
    gh_analyzer = GitHubAnalyzer(github_username)
    github_data = gh_analyzer.analyze_profile()
    code_analyzer = CodeQualityAnalyzer(github_data)
    code_quality = code_analyzer.analyze_all_repos()
    
    bullets = resume_rewriter.generate_bullets(github_data, code_quality, {})
    
    return jsonify({
        "bullets": bullets,
        "source": "fresh_analysis",
        "github_username": github_username
    })


@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    """Get current job market data for developer roles."""
    role = request.args.get('role', 'Full-Stack Developer')
    location = request.args.get('location', 'Remote')
    
    market_data = market_engine.get_market_overview(role, location)
    return jsonify(market_data)


@app.route('/api/roadmap/<audit_id>', methods=['GET'])
def get_roadmap(audit_id):
    """Get 90-day learning roadmap for an audit."""
    if audit_id not in audit_store:
        return jsonify({"error": "Audit not found"}), 404
    
    audit = audit_store[audit_id]
    if audit['status'] != 'completed':
        return jsonify({"error": "Audit not completed"}), 400
    
    return jsonify(audit['results']['roadmap'])


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
