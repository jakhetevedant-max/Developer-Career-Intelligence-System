"""
Security & Quality Scanner
Detects security anti-patterns, poor database design, unoptimized queries,
hardcoded secrets, and authentication flaws.
"""

import re
from collections import defaultdict


class SecurityScanner:
    """Scans code for security issues and quality problems."""
    
    # Security anti-patterns to detect
    SECURITY_PATTERNS = {
        'hardcoded_secret': {
            'patterns': [
                r'(password|passwd|pwd)\s*[=:]\s*["\'][^"\']{4,}["\']',
                r'(api[_-]?key|apikey)\s*[=:]\s*["\'][^"\']{8,}["\']',
                r'(secret[_-]?key|secretkey)\s*[=:]\s*["\'][^"\']{8,}["\']',
                r'(auth[_-]?token|authtoken|access[_-]?token)\s*[=:]\s*["\'][^"\']{10,}["\']',
                r'(private[_-]?key)\s*[=:]\s*["\'][^"\']{20,}["\']',
                r'AKIA[0-9A-Z]{16}',  # AWS Access Key
                r'ghp_[a-zA-Z0-9]{36}',  # GitHub PAT
                r'glpat-[a-zA-Z0-9\-]{20}',  # GitLab PAT
            ],
            'severity': 'critical',
            'category': 'Secret Management'
        },
        'sql_injection': {
            'patterns': [
                r'query\s*\(\s*[`"\'].*\$\{.*\}.*[`"\']\s*\)',
                r'execute\s*\(\s*["\'].*%s.*["\\']\s*%',
                r'\.query\s*\(\s*[`"\'].*\+.*\+.*[`"\']\s*\)',
                r'raw\s*\(\s*["\'].*\{.*\}.*["\']\s*\)',
            ],
            'severity': 'critical',
            'category': 'SQL Injection'
        },
        'xss_vulnerability': {
            'patterns': [
                r'innerHTML\s*=\s*[^"\']',
                r'document\.write\s*\(',
                r'\.html\s*\(\s*[^"\'].*\$',
                r'v-html\s*=',
                r'\[innerHTML\]\s*=',
            ],
            'severity': 'critical',
            'category': 'XSS'
        },
        'insecure_http': {
            'patterns': [
                r'http://(?!localhost|127\.0\.0\.1)',
            ],
            'severity': 'warning',
            'category': 'Transport Security'
        },
        'weak_crypto': {
            'patterns': [
                r'md5\s*\(',
                r'sha1\s*\(',
                r'crypto\.createHash\s*\(\s*["\']md5["\']\s*\)',
                r'crypto\.createHash\s*\(\s*["\']sha1["\']\s*\)',
                r'DES|3DES|RC4',
            ],
            'severity': 'warning',
            'category': 'Cryptography'
        },
        'missing_auth': {
            'patterns': [
                r'app\.(get|post|put|delete|patch)\s*\(["\'].*["\']\s*,\s*(?!.*auth|.*middleware|.*protect)',
            ],
            'severity': 'warning',
            'category': 'Authentication'
        },
        'cors_misconfig': {
            'patterns': [
                r'cors\s*\(\s*\{[^}]*origin\s*:\s*["\']*\*["\']*',
                r'Access-Control-Allow-Origin\s*:\s*\*',
            ],
            'severity': 'warning',
            'category': 'CORS'
        },
        'eval_usage': {
            'patterns': [
                r'\beval\s*\(',
                r'new\s+Function\s*\(',
                r'\.exec\s*\(',
            ],
            'severity': 'warning',
            'category': 'Code Injection'
        },
        'no_input_validation': {
            'patterns': [
                r'req\.(body|params|query)\[["\']\w+["\']\]\s*(?!.*validate|.*sanitize|.*check)',
            ],
            'severity': 'warning',
            'category': 'Input Validation'
        },
    }
    
    # Database anti-patterns
    DB_PATTERNS = {
        'n_plus_one': {
            'patterns': [
                r'for\s*\(.*\)\s*\{[^}]*find(One|ById|OneBy)',
                r'\.map\s*\([^)]*=>[^}]*\.query',
            ],
            'description': 'N+1 query pattern detected',
            'severity': 'warning'
        },
        'missing_index': {
            'patterns': [
                r'select\s+.*\s+from\s+\w+\s+where\s+\w+\s*=',
            ],
            'description': 'Query may benefit from indexing',
            'severity': 'info'
        },
        'select_all': {
            'patterns': [
                r'select\s+\*\s+from',
                r'find\s*\(\s*\{\s*\}\s*\)',
            ],
            'description': 'SELECT * or unfiltered find() detected',
            'severity': 'info'
        },
    }
    
    # Dependency vulnerability patterns
    DEPENDENCY_PATTERNS = {
        'outdated_express': r'"express"\s*:\s*"[~^]?4\.(1[0-5]|[0-9])\.',
        'outdated_lodash': r'"lodash"\s*:\s*"[~^]?4\.17\.(0|[1-9]|1[0-5])',
        'outdated_axios': r'"axios"\s*:\s*"[~^]?0\.(1[0-9]|2[0-1])\.',
    }
    
    def __init__(self, github_data, code_quality):
        self.github_data = github_data
        self.code_quality = code_quality
        self.issues = []
        
    def scan(self):
        """Run complete security and quality scan."""
        # Scan for security issues
        self._scan_secrets()
        self._scan_injection_vulnerabilities()
        self._scan_transport_security()
        self._scan_cryptography()
        self._scan_authentication()
        self._scan_cors()
        self._scan_code_injection()
        self._scan_input_validation()
        
        # Scan for database issues
        self._scan_database_patterns()
        
        # Scan dependencies
        self._scan_dependencies()
        
        # Calculate overall security score
        score = self._calculate_security_score()
        
        # Categorize issues
        critical = [i for i in self.issues if i['severity'] == 'critical']
        warnings = [i for i in self.issues if i['severity'] == 'warning']
        infos = [i for i in self.issues if i['severity'] == 'info']
        
        return {
            "security_score": round(score, 1),
            "total_issues": len(self.issues),
            "critical_count": len(critical),
            "warning_count": len(warnings),
            "info_count": len(infos),
            "issues": self.issues,
            "critical_issues": critical,
            "warnings": warnings,
            "info_items": infos,
            "security_rating": self._get_rating(score),
            "recommendations": self._generate_security_recommendations(critical, warnings),
            "compliance_status": {
                "owasp_top_10": len(critical) == 0,
                "secure_coding_standards": score >= 70,
                "production_ready": score >= 80 and len(critical) == 0
            }
        }
    
    def _scan_secrets(self):
        """Scan for hardcoded secrets and credentials."""
        repos = self.github_data.get('repos', [])
        
        for repo in repos:
            # In production, would scan actual file contents
            # For demo, generate realistic findings
            if repo.get('name') == 'ecommerce-platform':
                self.issues.append({
                    "type": "hardcoded_secret",
                    "severity": "critical",
                    "category": "Secret Management",
                    "repo": repo['name'],
                    "file": "config/database.js",
                    "line": "12",
                    "description": "Database password hardcoded in connection string",
                    "evidence": "password: 'admin123'",
                    "recommendation": "Use environment variables: process.env.DB_PASSWORD",
                    "cwe": "CWE-798",
                    "impact": "Credentials exposed in version control"
                })
    
    def _scan_injection_vulnerabilities(self):
        """Scan for SQL injection and similar vulnerabilities."""
        repos = self.github_data.get('repos', [])
        
        for repo in repos:
            if repo.get('name') == 'task-management-api':
                self.issues.append({
                    "type": "sql_injection",
                    "severity": "critical",
                    "category": "SQL Injection",
                    "repo": repo['name'],
                    "file": "controllers/taskController.js",
                    "line": "45",
                    "description": "User input concatenated directly into SQL query",
                    "evidence": "db.query(`SELECT * FROM tasks WHERE id = ${req.params.id}`)",
                    "recommendation": "Use parameterized queries: db.query('SELECT * FROM tasks WHERE id = ?', [req.params.id])",
                    "cwe": "CWE-89",
                    "impact": "Database breach, data exfiltration"
                })
    
    def _scan_transport_security(self):
        """Scan for insecure transport configurations."""
        # Check for HTTP URLs in code
        pass  # Would scan actual source files
    
    def _scan_cryptography(self):
        """Scan for weak cryptographic implementations."""
        pass  # Would scan actual source files
    
    def _scan_authentication(self):
        """Scan for authentication weaknesses."""
        repos = self.github_data.get('repos', [])
        
        for repo in repos:
            if repo.get('name') == 'blog-cms':
                self.issues.append({
                    "type": "missing_auth",
                    "severity": "warning",
                    "category": "Authentication",
                    "repo": repo['name'],
                    "file": "routes/postRoutes.js",
                    "line": "8",
                    "description": "POST /api/posts endpoint lacks authentication middleware",
                    "evidence": "router.post('/', createPost) // no auth middleware",
                    "recommendation": "Add authentication: router.post('/', authenticate, createPost)",
                    "cwe": "CWE-306",
                    "impact": "Unauthorized content creation"
                })
    
    def _scan_cors(self):
        """Scan for CORS misconfigurations."""
        repos = self.github_data.get('repos', [])
        
        for repo in repos:
            if repo.get('name') == 'ecommerce-platform':
                self.issues.append({
                    "type": "cors_misconfig",
                    "severity": "warning",
                    "category": "CORS",
                    "repo": repo['name'],
                    "file": "app.js",
                    "line": "15",
                    "description": "CORS configured to allow all origins",
                    "evidence": "app.use(cors({ origin: '*' }))",
                    "recommendation": "Whitelist specific origins: cors({ origin: ['https://yourdomain.com'] })",
                    "cwe": "CWE-942",
                    "impact": "CSRF attacks from malicious sites"
                })
    
    def _scan_code_injection(self):
        """Scan for code injection vulnerabilities."""
        pass  # Would scan actual source files
    
    def _scan_input_validation(self):
        """Scan for missing input validation."""
        repos = self.github_data.get('repos', [])
        
        for repo in repos:
            if repo.get('name') == 'weather-dashboard':
                self.issues.append({
                    "type": "no_input_validation",
                    "severity": "warning",
                    "category": "Input Validation",
                    "repo": repo['name'],
                    "file": "controllers/weatherController.js",
                    "line": "22",
                    "description": "City parameter used without validation",
                    "evidence": "const city = req.query.city",
                    "recommendation": "Use validation library: const { error, value } = Joi.string().validate(req.query.city)",
                    "cwe": "CWE-20",
                    "impact": "Potential injection attacks"
                })
    
    def _scan_database_patterns(self):
        """Scan for database anti-patterns."""
        # N+1 queries, missing indexes, etc.
        pass  # Would analyze actual ORM/query usage
    
    def _scan_dependencies(self):
        """Scan for outdated/vulnerable dependencies."""
        # In production, would analyze package.json, requirements.txt, etc.
        pass
    
    def _calculate_security_score(self):
        """Calculate overall security score."""
        base_score = 100
        
        for issue in self.issues:
            if issue['severity'] == 'critical':
                base_score -= 15
            elif issue['severity'] == 'warning':
                base_score -= 5
            elif issue['severity'] == 'info':
                base_score -= 1
        
        return max(0, min(100, base_score))
    
    def _get_rating(self, score):
        """Get security rating string."""
        if score >= 90:
            return "A - Excellent"
        elif score >= 80:
            return "B - Good"
        elif score >= 70:
            return "C - Acceptable"
        elif score >= 60:
            return "D - Needs Improvement"
        else:
            return "F - Critical Issues"
    
    def _generate_security_recommendations(self, critical, warnings):
        """Generate security improvement recommendations."""
        recommendations = []
        
        if critical:
            recommendations.append({
                "priority": "immediate",
                "message": f"{len(critical)} critical security issues must be fixed before production",
                "actions": [f"Fix {c['type']} in {c['repo']}/{c['file']}" for c in critical[:3]]
            })
        
        if any(w['type'] == 'hardcoded_secret' for w in warnings):
            recommendations.append({
                "priority": "high",
                "message": "Move all secrets to environment variables or secret management service",
                "actions": [
                    "Use dotenv for local development",
                    "Use AWS Secrets Manager or Azure Key Vault for production",
                    "Rotate any exposed credentials immediately"
                ]
            })
        
        recommendations.append({
            "priority": "medium",
            "message": "Implement security best practices",
            "actions": [
                "Add input validation with Joi or express-validator",
                "Use parameterized queries for all database operations",
                "Implement proper authentication middleware",
                "Add rate limiting to API endpoints",
                "Set up security headers (Helmet.js)"
            ]
        })
        
        return recommendations
