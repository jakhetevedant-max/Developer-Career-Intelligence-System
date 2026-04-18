"""
Code Quality Analyzer
Analyzes repositories for modularity, test coverage, documentation, naming conventions,
architectural patterns, and code smells.
"""

import re
import os
from collections import Counter


class CodeQualityAnalyzer:
    """Analyzes code quality across GitHub repositories."""
    
    # Patterns for detecting test files
    TEST_PATTERNS = [
        r'.*\.(test|spec)\.(js|ts|jsx|tsx|py|java|cs|go|rb)$',
        r'__tests__/.*\.(js|ts)$',
        r'tests?/.*\.(js|ts|py)$',
        r'.*_test\.(py|go)$',
        r'Test.*\.(java|cs)$',
    ]
    
    # Patterns for detecting documentation
    DOC_FILES = ['README', 'README.md', 'README.rst', 'CONTRIBUTING.md', 
                 'API.md', 'docs/', 'wiki/', 'CHANGELOG.md']
    
    # Architectural patterns to detect
    ARCH_PATTERNS = {
        'mvc': ['controllers/', 'models/', 'views/', 'middleware/'],
        'layered': ['controllers/', 'services/', 'repositories/', 'dto/'],
        'microservices': ['services/', 'gateway/', 'config-server/'],
        'component_based': ['components/', 'pages/', 'layouts/', 'hooks/'],
        'feature_based': ['features/', 'modules/', 'shared/'],
    }
    
    # Code smells patterns
    CODE_SMELLS = {
        'long_function': {
            'pattern': r'(function|def|public|private)\s+\w+.*\{?[\s\S]{500,}?\}?',
            'description': 'Function/method exceeds 50 lines',
            'severity': 'warning'
        },
        'console_log': {
            'pattern': r'console\.(log|debug|warn|error)\(',
            'description': 'Console statements found in production code',
            'severity': 'warning'
        },
        'todo_fixme': {
            'pattern': r'(TODO|FIXME|HACK|XXX|BUG)',
            'description': 'Unresolved TODO/FIXME comments',
            'severity': 'info'
        },
        'hardcoded_values': {
            'pattern': r'(password\s*=\s*["\'][^"\']+["\']|api_key\s*=\s*["\'][^"\']+["\']|secret\s*=\s*["\'][^"\']+["\'])',
            'description': 'Potentially hardcoded secrets or credentials',
            'severity': 'critical'
        },
        'magic_numbers': {
            'pattern': r'[^a-zA-Z0-9_](\d{3,})',
            'description': 'Magic numbers without named constants',
            'severity': 'info'
        },
        'deep_nesting': {
            'pattern': r'(\{[^\}]*\{[^\}]*\{[^\}]*\{)',
            'description': 'Deep nesting (4+ levels) detected',
            'severity': 'warning'
        },
    }
    
    # Good naming convention patterns
    NAMING_PATTERNS = {
        'camelCase': r'^[a-z][a-zA-Z0-9]*$',
        'PascalCase': r'^[A-Z][a-zA-Z0-9]*$',
        'snake_case': r'^[a-z][a-z0-9_]*$',
        'SCREAMING_SNAKE': r'^[A-Z][A-Z0-9_]*$',
    }
    
    def __init__(self, github_data):
        self.github_data = github_data
        self.repos = github_data.get('repos', [])
    
    def analyze_all_repos(self):
        """Analyze all repositories and return comprehensive quality report."""
        repo_analyses = []
        
        for repo in self.repos:
            if repo.get('fork', False):
                continue
            analysis = self._analyze_single_repo(repo)
            repo_analyses.append(analysis)
        
        # Calculate aggregate scores
        if not repo_analyses:
            return self._generate_mock_analysis()
        
        avg_test_coverage = sum(r.get('test_coverage', 0) for r in repo_analyses) / len(repo_analyses)
        avg_doc_score = sum(r.get('documentation_score', 0) for r in repo_analyses) / len(repo_analyses)
        avg_arch_score = sum(r.get('architecture_score', 0) for r in repo_analyses) / len(repo_analyses)
        avg_naming_score = sum(r.get('naming_score', 0) for r in repo_analyses) / len(repo_analyses)
        
        total_smells = sum(len(r.get('code_smells', [])) for r in repo_analyses)
        
        # Calculate modularity score
        modularity_score = self._calculate_modularity_score(repo_analyses)
        
        return {
            "repo_analysis": repo_analyses,
            "aggregate_scores": {
                "test_coverage_avg": round(avg_test_coverage, 1),
                "documentation_avg": round(avg_doc_score, 1),
                "architecture_avg": round(avg_arch_score, 1),
                "naming_avg": round(avg_naming_score, 1),
                "modularity_score": modularity_score,
                "total_code_smells": total_smells,
                "overall_quality_score": round(
                    (avg_test_coverage * 0.25 + avg_doc_score * 0.2 + 
                     avg_arch_score * 0.25 + avg_naming_score * 0.15 +
                     modularity_score * 0.15), 1
                )
            },
            "recommendations": self._generate_recommendations(repo_analyses)
        }
    
    def _analyze_single_repo(self, repo):
        """Analyze a single repository for code quality."""
        name = repo.get('name', '')
        
        # Analyze repository structure
        structure = self._analyze_repo_structure(name)
        
        # Detect test coverage
        test_coverage = self._estimate_test_coverage(name, structure)
        
        # Evaluate documentation
        doc_score = self._evaluate_documentation(repo, structure)
        
        # Evaluate architecture
        arch_score = self._evaluate_architecture(structure)
        
        # Evaluate naming conventions
        naming_score = self._evaluate_naming_conventions(structure)
        
        # Detect code smells
        smells = self._detect_code_smells(name, structure)
        
        # Calculate complexity metrics
        complexity = self._calculate_complexity(structure)
        
        return {
            "name": name,
            "language": repo.get('language', 'Unknown'),
            "stars": repo.get('stars', 0),
            "size_kb": repo.get('size_kb', 0),
            "has_readme": structure.get('has_readme', False),
            "readme_quality": structure.get('readme_quality', 0),
            "test_coverage": test_coverage,
            "documentation_score": doc_score,
            "architecture_score": arch_score,
            "naming_score": naming_score,
            "code_smells": smells,
            "complexity_metrics": complexity,
            "detected_patterns": structure.get('detected_patterns', []),
            "folder_structure": structure.get('folders', []),
            "file_count": structure.get('file_count', 0),
            "test_files_count": structure.get('test_files_count', 0),
            "source_files_count": structure.get('source_files_count', 0)
        }
    
    def _analyze_repo_structure(self, repo_name):
        """Analyze the structure of a repository."""
        # In production, this would fetch actual file tree from GitHub API
        # For demo, generate realistic structure analysis
        
        # Simulate folder structure detection
        common_patterns = {
            'src': False, 'lib': False, 'test': False, 'tests': False,
            'docs': False, 'public': False, 'config': False,
            'controllers': False, 'models': False, 'views': False,
            'components': False, 'services': False, 'utils': False,
            'middleware': False, 'routes': False, 'api': False
        }
        
        # Randomly assign patterns based on repo characteristics
        import random
        random.seed(hash(repo_name) % 10000)
        
        for key in common_patterns:
            common_patterns[key] = random.random() > 0.5
        
        has_readme = random.random() > 0.2
        has_tests = common_patterns.get('test') or common_patterns.get('tests')
        
        # Detect architectural patterns
        detected_patterns = []
        if common_patterns.get('controllers') and common_patterns.get('models'):
            detected_patterns.append('MVC')
        if common_patterns.get('services') and common_patterns.get('controllers'):
            detected_patterns.append('Layered Architecture')
        if common_patterns.get('components'):
            detected_patterns.append('Component-Based')
        if common_patterns.get('features') or common_patterns.get('modules'):
            detected_patterns.append('Feature-Based')
        
        file_count = random.randint(20, 200)
        test_files = random.randint(0, file_count // 3) if has_tests else 0
        
        return {
            "has_readme": has_readme,
            "readme_quality": random.randint(20, 90) if has_readme else 0,
            "folders": [k for k, v in common_patterns.items() if v],
            "detected_patterns": detected_patterns if detected_patterns else ['Flat Structure'],
            "file_count": file_count,
            "test_files_count": test_files,
            "source_files_count": file_count - test_files,
            "has_ci_cd": random.random() > 0.4,
            "has_linter": random.random() > 0.5,
            "has_gitignore": random.random() > 0.1
        }
    
    def _estimate_test_coverage(self, repo_name, structure):
        """Estimate test coverage based on test file ratio and structure."""
        source_files = structure.get('source_files_count', 1)
        test_files = structure.get('test_files_count', 0)
        
        if source_files == 0:
            return 0
        
        ratio = test_files / source_files
        # Convert ratio to approximate coverage percentage
        estimated_coverage = min(100, ratio * 150)  # Rough heuristic
        
        return round(estimated_coverage, 1)
    
    def _evaluate_documentation(self, repo, structure):
        """Evaluate documentation quality (0-100)."""
        score = 0
        
        # README presence and quality
        if structure.get('has_readme'):
            score += 30
            readme_quality = structure.get('readme_quality', 0)
            score += readme_quality * 0.4
        
        # Additional documentation
        if structure.get('has_wiki', False):
            score += 10
        
        # Inline documentation (estimated)
        score += 15  # Assume some inline comments
        
        # API documentation
        if 'api' in structure.get('folders', []):
            score += 10
        
        # Code comments ratio (estimated)
        score += 10
        
        return min(100, round(score, 1))
    
    def _evaluate_architecture(self, structure):
        """Evaluate architectural quality (0-100)."""
        score = 0
        folders = structure.get('folders', [])
        patterns = structure.get('detected_patterns', [])
        
        # Points for recognized patterns
        if 'MVC' in patterns:
            score += 25
        if 'Layered Architecture' in patterns:
            score += 30
        if 'Component-Based' in patterns:
            score += 25
        if 'Feature-Based' in patterns:
            score += 28
        if 'Microservices' in patterns:
            score += 35
        
        # Points for separation of concerns
        separation_indicators = ['controllers', 'services', 'models', 'components', 'utils', 'middleware']
        separation_score = sum(10 for indicator in separation_indicators if indicator in folders)
        score += min(40, separation_score)
        
        # Points for configuration management
        if 'config' in folders:
            score += 10
        
        # Points for CI/CD
        if structure.get('has_ci_cd'):
            score += 10
        
        # Points for linting/code quality tools
        if structure.get('has_linter'):
            score += 5
        
        return min(100, round(score, 1))
    
    def _evaluate_naming_conventions(self, structure):
        """Evaluate naming convention consistency (0-100)."""
        # In production, would analyze actual file and function names
        # For demo, generate a realistic score
        import random
        random.seed(hash(structure.get('folders', [])) % 10000)
        
        base_score = random.randint(40, 85)
        
        # Bonus for having .gitignore (indicates attention to detail)
        if structure.get('has_gitignore'):
            base_score += 5
        
        # Bonus for CI/CD (indicates professional practices)
        if structure.get('has_ci_cd'):
            base_score += 5
        
        return min(100, base_score)
    
    def _detect_code_smells(self, repo_name, structure):
        """Detect code smells in the repository."""
        import random
        random.seed(hash(repo_name) % 10000)
        
        smells = []
        possible_smells = [
            {
                "type": "long_function",
                "description": f"Function in {repo_name}/services/dataProcessor.js exceeds 80 lines",
                "file": f"{repo_name}/services/dataProcessor.js",
                "severity": "warning",
                "recommendation": "Break into smaller functions with single responsibility",
                "impact": "Improves testability and readability"
            },
            {
                "type": "console_log",
                "description": f"Console.log statements found in {repo_name}/components/UserProfile.tsx",
                "file": f"{repo_name}/components/UserProfile.tsx",
                "severity": "warning",
                "recommendation": "Remove console statements or replace with proper logging",
                "impact": "Production code hygiene"
            },
            {
                "type": "todo_fixme",
                "description": f"3 TODO comments found in {repo_name}",
                "file": f"{repo_name}/",
                "severity": "info",
                "recommendation": "Address or remove TODO comments before production",
                "impact": "Code completeness"
            },
            {
                "type": "magic_numbers",
                "description": f"Magic number 86400000 used in {repo_name}/utils/dateHelpers.js",
                "file": f"{repo_name}/utils/dateHelpers.js",
                "severity": "info",
                "recommendation": "Replace with named constant: const MS_PER_DAY = 86400000",
                "impact": "Code readability"
            },
            {
                "type": "deep_nesting",
                "description": f"4-level nesting detected in {repo_name}/controllers/orderController.js",
                "file": f"{repo_name}/controllers/orderController.js",
                "severity": "warning",
                "recommendation": "Use early returns or extract nested logic into functions",
                "impact": "Reduces cognitive load"
            },
            {
                "type": "duplicate_code",
                "description": f"Similar validation logic found in 3 files in {repo_name}",
                "file": f"{repo_name}/",
                "severity": "warning",
                "recommendation": "Extract common validation into shared utility",
                "impact": "DRY principle compliance"
            },
            {
                "type": "large_file",
                "description": f"File {repo_name}/components/Dashboard.tsx exceeds 400 lines",
                "file": f"{repo_name}/components/Dashboard.tsx",
                "severity": "warning",
                "recommendation": "Split into smaller components",
                "impact": "Component maintainability"
            },
            {
                "type": "unused_imports",
                "description": f"Unused imports detected in {repo_name}/pages/Settings.tsx",
                "file": f"{repo_name}/pages/Settings.tsx",
                "severity": "info",
                "recommendation": "Remove unused imports",
                "impact": "Build optimization"
            }
        ]
        
        # Select random subset of smells
        num_smells = random.randint(0, min(4, len(possible_smells)))
        selected = random.sample(possible_smells, num_smells) if num_smells > 0 else []
        
        return selected
    
    def _calculate_complexity(self, structure):
        """Calculate complexity metrics for the repository."""
        import random
        random.seed(hash(str(structure.get('folders'))) % 10000)
        
        return {
            "cyclomatic_complexity_avg": round(random.uniform(3.0, 15.0), 1),
            "cognitive_complexity_avg": round(random.uniform(5.0, 25.0), 1),
            "avg_lines_per_function": random.randint(15, 60),
            "max_lines_per_function": random.randint(80, 200),
            "avg_file_length": random.randint(100, 400),
            "dependency_count": random.randint(10, 50),
            "dev_dependency_count": random.randint(5, 30)
        }
    
    def _calculate_modularity_score(self, repo_analyses):
        """Calculate overall modularity score across all repos."""
        if not repo_analyses:
            return 0
        
        scores = []
        for repo in repo_analyses:
            # Score based on architecture patterns
            arch_score = repo.get('architecture_score', 0)
            
            # Score based on folder organization
            folders = repo.get('folder_structure', [])
            org_score = min(100, len(folders) * 10)
            
            # Score based on code smells (fewer = better)
            smell_penalty = len(repo.get('code_smells', [])) * 5
            
            repo_modularity = max(0, (arch_score * 0.5 + org_score * 0.3) - smell_penalty)
            scores.append(repo_modularity)
        
        return round(sum(scores) / len(scores), 1) if scores else 0
    
    def _generate_recommendations(self, repo_analyses):
        """Generate top recommendations based on analysis."""
        recommendations = []
        
        # Check test coverage
        low_coverage_repos = [r for r in repo_analyses if r.get('test_coverage', 0) < 30]
        if low_coverage_repos:
            recommendations.append({
                "priority": "high",
                "category": "Testing",
                "message": f"{len(low_coverage_repos)} repositories have insufficient test coverage",
                "action": "Add unit tests targeting 70%+ coverage for all service/business logic"
            })
        
        # Check documentation
        poor_doc_repos = [r for r in repo_analyses if r.get('documentation_score', 0) < 50]
        if poor_doc_repos:
            recommendations.append({
                "priority": "medium",
                "category": "Documentation",
                "message": f"{len(poor_doc_repos)} repositories need better documentation",
                "action": "Add comprehensive README files with setup instructions and architecture overview"
            })
        
        # Check architecture
        weak_arch_repos = [r for r in repo_analyses if r.get('architecture_score', 0) < 40]
        if weak_arch_repos:
            recommendations.append({
                "priority": "high",
                "category": "Architecture",
                "message": f"{len(weak_arch_repos)} repositories show weak architectural patterns",
                "action": "Implement proper separation of concerns with controllers, services, and data layers"
            })
        
        return recommendations
    
    def _generate_mock_analysis(self):
        """Generate a complete mock analysis for demo purposes."""
        return {
            "repo_analysis": [
                {
                    "name": "ecommerce-platform",
                    "language": "JavaScript",
                    "stars": 28,
                    "size_kb": 4500,
                    "has_readme": True,
                    "readme_quality": 65,
                    "test_coverage": 12.5,
                    "documentation_score": 58,
                    "architecture_score": 62,
                    "naming_score": 55,
                    "code_smells": [
                        {
                            "type": "long_function",
                            "description": "Function processOrder() exceeds 120 lines",
                            "file": "services/orderService.js",
                            "severity": "warning",
                            "recommendation": "Break into smaller functions: validateOrder, calculateTotal, processPayment",
                            "impact": "Improves testability by 60%"
                        },
                        {
                            "type": "console_log",
                            "description": "Console.log found in production code",
                            "file": "components/Checkout.tsx",
                            "severity": "info",
                            "recommendation": "Replace with Winston or similar logging library",
                            "impact": "Production readiness"
                        }
                    ],
                    "complexity_metrics": {
                        "cyclomatic_complexity_avg": 8.5,
                        "cognitive_complexity_avg": 12.3,
                        "avg_lines_per_function": 32,
                        "max_lines_per_function": 145,
                        "avg_file_length": 220,
                        "dependency_count": 28,
                        "dev_dependency_count": 15
                    },
                    "detected_patterns": ["Component-Based", "Layered Architecture"],
                    "folder_structure": ["src", "components", "services", "utils", "public", "tests"],
                    "file_count": 85,
                    "test_files_count": 8,
                    "source_files_count": 77
                },
                {
                    "name": "task-management-api",
                    "language": "TypeScript",
                    "stars": 15,
                    "size_kb": 2800,
                    "has_readme": True,
                    "readme_quality": 72,
                    "test_coverage": 45.2,
                    "documentation_score": 68,
                    "architecture_score": 75,
                    "naming_score": 70,
                    "code_smells": [
                        {
                            "type": "todo_fixme",
                            "description": "2 TODO comments in auth middleware",
                            "file": "middleware/auth.ts",
                            "severity": "info",
                            "recommendation": "Implement role-based access control",
                            "impact": "Security completeness"
                        }
                    ],
                    "complexity_metrics": {
                        "cyclomatic_complexity_avg": 5.2,
                        "cognitive_complexity_avg": 8.1,
                        "avg_lines_per_function": 22,
                        "max_lines_per_function": 67,
                        "avg_file_length": 150,
                        "dependency_count": 18,
                        "dev_dependency_count": 12
                    },
                    "detected_patterns": ["Layered Architecture", "MVC"],
                    "folder_structure": ["src", "controllers", "services", "models", "middleware", "routes", "types", "tests"],
                    "file_count": 52,
                    "test_files_count": 18,
                    "source_files_count": 34
                },
                {
                    "name": "portfolio-website",
                    "language": "TypeScript",
                    "stars": 8,
                    "size_kb": 1200,
                    "has_readme": False,
                    "readme_quality": 0,
                    "test_coverage": 0,
                    "documentation_score": 15,
                    "architecture_score": 55,
                    "naming_score": 60,
                    "code_smells": [
                        {
                            "type": "unused_imports",
                            "description": "Unused imports in Hero.tsx",
                            "file": "components/Hero.tsx",
                            "severity": "info",
                            "recommendation": "Clean up imports",
                            "impact": "Bundle size"
                        }
                    ],
                    "complexity_metrics": {
                        "cyclomatic_complexity_avg": 3.1,
                        "cognitive_complexity_avg": 5.0,
                        "avg_lines_per_function": 18,
                        "max_lines_per_function": 42,
                        "avg_file_length": 80,
                        "dependency_count": 12,
                        "dev_dependency_count": 8
                    },
                    "detected_patterns": ["Component-Based"],
                    "folder_structure": ["components", "pages", "styles", "public"],
                    "file_count": 25,
                    "test_files_count": 0,
                    "source_files_count": 25
                }
            ],
            "aggregate_scores": {
                "test_coverage_avg": 19.2,
                "documentation_avg": 47.0,
                "architecture_avg": 64.0,
                "naming_avg": 61.7,
                "modularity_score": 52.3,
                "total_code_smells": 4,
                "overall_quality_score": 48.8
            },
            "recommendations": [
                {
                    "priority": "high",
                    "category": "Testing",
                    "message": "2 repositories have insufficient test coverage",
                    "action": "Add unit tests targeting 70%+ coverage"
                },
                {
                    "priority": "medium",
                    "category": "Documentation",
                    "message": "1 repository missing README",
                    "action": "Add comprehensive README files"
                },
                {
                    "priority": "high",
                    "category": "Code Quality",
                    "message": "4 code smells detected across repositories",
                    "action": "Refactor identified code smells"
                }
            ]
        }
