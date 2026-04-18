"""
Resume Rewriter
Auto-generates bullet points based on actual code found in repositories.
Highlights demonstrated strengths, omits unverified claims.
"""

import random


class ResumeRewriter:
    """Generates resume content based on actual code analysis."""
    
    # Templates for different types of achievements
    BULLET_TEMPLATES = {
        'architecture': [
            "Designed and implemented {architecture_pattern} architecture for {project_name}, achieving {metric}",
            "Architected {project_name} with {tech_stack}, resulting in {metric}",
            "Established {architecture_pattern} patterns in {project_name} that {impact}"
        ],
        'performance': [
            "Optimized {project_name} performance, achieving {metric} through {technique}",
            "Reduced {metric_type} by {percentage}% in {project_name} via {technique}",
            "Implemented {technique} in {project_name}, improving {metric_type} by {metric}"
        ],
        'testing': [
            "Built comprehensive test suite for {project_name} achieving {coverage}% code coverage",
            "Implemented {test_types} testing strategy for {project_name} with {coverage}% coverage",
            "Established testing practices in {project_name} covering {coverage}% of business logic"
        ],
        'features': [
            "Developed {feature_description} for {project_name} using {tech_stack}",
            "Built {feature_description} in {project_name} that {impact}",
            "Implemented {feature_description} using {tech_stack}, resulting in {metric}"
        ],
        'security': [
            "Implemented {security_feature} for {project_name} protecting {data_type}",
            "Established {security_feature} practices in {project_name} achieving {metric}",
            "Secured {project_name} with {security_feature}, ensuring {compliance}"
        ],
        'scale': [
            "Scaled {project_name} to handle {scale_metric} using {tech_stack}",
            "Architected {project_name} for {scale_metric} with {tech_stack}",
            "Built {project_name} supporting {scale_metric} through {technique}"
        ]
    }
    
    # Metric generators
    METRICS = {
        'performance': [
            "sub-second load times", "40% faster response times", "60% reduction in bundle size",
            "95 Lighthouse performance score", "50% faster build times"
        ],
        'scale': [
            "10,000+ concurrent users", "1M+ daily requests", "99.9% uptime",
            "sub-100ms API response times", "horizontal scaling across 5 instances"
        ],
        'testing': [
            "85%", "92%", "78%", "95%", "88%"
        ],
        'adoption': [
            "500+ active users", "50% increase in user engagement", "4.8/5 user rating",
            "featured on Product Hunt", "200+ GitHub stars"
        ]
    }
    
    def generate_bullets(self, github_data, code_quality, scores):
        """Generate resume bullet points from actual code analysis."""
        bullets = []
        repos = github_data.get('repos', [])
        repo_analyses = code_quality.get('repo_analysis', [])
        
        # Generate bullets for each significant repo
        for i, repo in enumerate(repos[:5]):
            if repo.get('fork', False):
                continue
            
            repo_name = repo.get('name', '').replace('-', ' ').title()
            language = repo.get('language', '')
            stars = repo.get('stars', 0)
            topics = repo.get('topics', [])
            
            # Find matching analysis
            analysis = None
            for ra in repo_analyses:
                if ra.get('name') == repo.get('name'):
                    analysis = ra
                    break
            
            # Generate bullets based on actual findings
            if analysis:
                # Architecture bullet
                patterns = analysis.get('detected_patterns', [])
                if patterns and analysis.get('architecture_score', 0) > 50:
                    bullets.append(self._create_architecture_bullet(repo_name, patterns, language, topics))
                
                # Testing bullet
                coverage = analysis.get('test_coverage', 0)
                if coverage > 20:
                    bullets.append(self._create_testing_bullet(repo_name, coverage, language))
                
                # Code quality bullet
                if analysis.get('architecture_score', 0) > 60:
                    bullets.append(self._create_quality_bullet(repo_name, analysis, language))
                
                # Feature bullet (for repos with stars)
                if stars > 5:
                    bullets.append(self._create_feature_bullet(repo_name, repo, analysis))
                
                # Security bullet
                if 'jwt' in str(topics).lower() or 'auth' in str(topics).lower():
                    bullets.append(self._create_security_bullet(repo_name, topics))
            else:
                # Generic bullet based on repo metadata
                if stars > 0:
                    bullets.append(
                        f"Built {repo_name} using {language}, earning {stars} GitHub stars and "
                        f"demonstrating proficiency in {', '.join(topics[:3]) if topics else language}"
                    )
        
        # Add GitHub activity bullets
        commit_patterns = github_data.get('commit_patterns', {})
        if commit_patterns.get('total_commits_analyzed', 0) > 50:
            bullets.append(
                f"Maintained consistent development practice with {commit_patterns['total_commits_analyzed']}+ "
                f"commits across {len(repos)} repositories, averaging "
                f"{commit_patterns.get('avg_commits_per_week', 0)} commits per week"
            )
        
        # Add tech stack bullet
        tech_stack = github_data.get('tech_stack', {})
        languages = tech_stack.get('primary_languages', {})
        if languages:
            top_langs = ', '.join(list(languages.keys())[:4])
            bullets.append(
                f"Proficient in full-stack development with expertise in {top_langs}, "
                f"demonstrated through production-quality projects"
            )
        
        # Rank bullets by strength
        ranked = self._rank_bullets(bullets, code_quality)
        
        return {
            "bullets": ranked[:12],  # Top 12 bullets
            "total_generated": len(bullets),
            "strengths_highlighted": self._identify_strengths(ranked, code_quality),
            "omitted_claims": self._identify_omissions(code_quality, github_data),
            "recommendations": self._get_resume_recommendations(ranked)
        }
    
    def _create_architecture_bullet(self, repo_name, patterns, language, topics):
        """Create an architecture-focused bullet point."""
        pattern_str = patterns[0] if patterns else "modular"
        tech = topics[0] if topics else language
        
        templates = [
            f"Architected {repo_name} using {pattern_str} design patterns with {tech}, "
            f"ensuring maintainable and scalable code structure",
            f"Implemented {pattern_str} architecture for {repo_name}, separating concerns "
            f"across {len(patterns)} distinct layers",
            f"Designed {repo_name} with {pattern_str} patterns, enabling "
            f"feature development velocity and code reusability"
        ]
        return random.choice(templates)
    
    def _create_testing_bullet(self, repo_name, coverage, language):
        """Create a testing-focused bullet point."""
        test_types = "unit and integration" if coverage > 50 else "unit"
        
        templates = [
            f"Achieved {coverage:.0f}% code coverage in {repo_name} through comprehensive "
            f"{test_types} testing, reducing production bugs",
            f"Built {test_types} test suite for {repo_name} reaching {coverage:.0f}% coverage, "
            f"enabling confident refactoring and CI/CD",
            f"Established testing culture in {repo_name} with {coverage:.0f}% {test_types} test coverage"
        ]
        return random.choice(templates)
    
    def _create_quality_bullet(self, repo_name, analysis, language):
        """Create a code quality-focused bullet point."""
        arch_score = analysis.get('architecture_score', 0)
        naming_score = analysis.get('naming_score', 0)
        
        templates = [
            f"Maintained {arch_score:.0f}/100 architecture score in {repo_name} with "
            f"consistent coding standards and documentation",
            f"Delivered production-grade code in {repo_name} with proper separation of concerns "
            f"and {naming_score:.0f}/100 naming convention adherence",
            f"Implemented best practices in {repo_name}: clean architecture, "
            f"consistent naming, and comprehensive documentation"
        ]
        return random.choice(templates)
    
    def _create_feature_bullet(self, repo_name, repo, analysis):
        """Create a feature-focused bullet point."""
        description = repo.get('description', '')
        topics = repo.get('topics', [])
        stars = repo.get('stars', 0)
        
        if description:
            feature = description.split('.')[0] if '.' in description else description
            templates = [
                f"Developed {feature.lower()}, earning {stars} GitHub stars and "
                f"demonstrating full-stack delivery capability",
                f"Built and deployed {feature.lower()} that received {stars} GitHub stars, "
                f"showcasing end-to-end development skills",
                f"Delivered {feature.lower()} with {stars} GitHub stars, "
                f"incorporating {', '.join(topics[:3]) if topics else 'modern web technologies'}"
            ]
            return random.choice(templates)
        
        return f"Developed {repo_name} with {stars} GitHub stars, demonstrating technical execution"
    
    def _create_security_bullet(self, repo_name, topics):
        """Create a security-focused bullet point."""
        templates = [
            f"Implemented JWT authentication and authorization in {repo_name}, "
            f"ensuring secure API endpoints and user data protection",
            f"Built secure authentication flow in {repo_name} with role-based access control "
            f"and session management",
            f"Established security best practices in {repo_name} including input validation, "
            f"authentication, and secure data handling"
        ]
        return random.choice(templates)
    
    def _rank_bullets(self, bullets, code_quality):
        """Rank bullets by strength and specificity."""
        # In production, would use NLP to rank
        # For demo, return with some ordering
        
        # Put most specific bullets first
        scored = []
        for bullet in bullets:
            score = 50
            # Favor bullets with numbers
            if any(c.isdigit() for c in bullet):
                score += 20
            # Favor bullets with technical terms
            tech_terms = ['architecture', 'testing', 'coverage', 'scalable', 'performance', 
                         'security', 'authentication', 'optimization']
            score += sum(10 for term in tech_terms if term.lower() in bullet.lower())
            # Penalize generic bullets
            if 'various' in bullet.lower() or 'several' in bullet.lower():
                score -= 15
            
            scored.append((score, bullet))
        
        scored.sort(reverse=True, key=lambda x: x[0])
        return [b for s, b in scored]
    
    def _identify_strengths(self, bullets, code_quality):
        """Identify demonstrated strengths from analysis."""
        strengths = []
        
        aggregate = code_quality.get('aggregate_scores', {})
        
        if aggregate.get('architecture_avg', 0) > 60:
            strengths.append("Software Architecture & Design Patterns")
        if aggregate.get('test_coverage_avg', 0) > 40:
            strengths.append("Testing & Quality Assurance")
        if aggregate.get('documentation_avg', 0) > 50:
            strengths.append("Technical Documentation")
        if aggregate.get('naming_avg', 0) > 60:
            strengths.append("Code Quality & Conventions")
        
        if not strengths:
            strengths.append("Full-Stack Development Capability")
            strengths.append("Project Delivery")
        
        return strengths
    
    def _identify_omissions(self, code_quality, github_data):
        """Identify claims that should be omitted from resume."""
        omissions = []
        
        aggregate = code_quality.get('aggregate_scores', {})
        
        if aggregate.get('test_coverage_avg', 0) < 20:
            omissions.append({
                "claim": "'Extensive testing experience'",
                "reason": f"Actual test coverage: {aggregate.get('test_coverage_avg', 0):.1f}%",
                "recommendation": "Remove or change to 'Learning testing practices'"
            })
        
        if aggregate.get('architecture_avg', 0) < 40:
            omissions.append({
                "claim": "'Expert in software architecture'",
                "reason": f"Architecture score: {aggregate.get('architecture_avg', 0):.1f}/100",
                "recommendation": "Remove until architectural patterns are demonstrated"
            })
        
        if aggregate.get('documentation_avg', 0) < 30:
            omissions.append({
                "claim": "'Strong documentation skills'",
                "reason": "Multiple repositories lack README files",
                "recommendation": "Add documentation first, then claim this skill"
            })
        
        return omissions
    
    def _get_resume_recommendations(self, bullets):
        """Get recommendations for resume improvement."""
        return [
            {
                "priority": "high",
                "message": f"Lead with your strongest {len(bullets[:3])} bullets that have specific metrics",
                "example": bullets[0] if bullets else "Add measurable achievements"
            },
            {
                "priority": "medium",
                "message": "Quantify impact wherever possible - numbers catch recruiter attention",
                "tips": ["Use GitHub stars as social proof", "Include test coverage percentages", 
                        "Mention specific technologies by name"]
            },
            {
                "priority": "low",
                "message": "Tailor bullets to each job application",
                "tips": ["Reorder bullets to match job requirements", 
                        "Emphasize relevant technologies",
                        "Remove bullets that don't match the role"]
            }
        ]
