"""
90-Day Learning Roadmap Generator
Creates personalized improvement plans based on audit findings.
"""

import random
from datetime import datetime, timedelta


class RoadmapGenerator:
    """Generates a 90-day personalized learning roadmap."""
    
    # Learning resources by category
    RESOURCES = {
        "testing": [
            {"type": "course", "title": "JavaScript Testing Fundamentals", "platform": "Testing JavaScript by Kent C. Dodds", "duration": "8 hours"},
            {"type": "practice", "title": "Add tests to your weakest repository", "action": "Start with unit tests for utility functions", "duration": "1 week"},
            {"type": "book", "title": "Unit Testing Principles, Practices, and Patterns", "author": "Vladimir Khorikov", "chapters": "Chapters 1-8"}
        ],
        "architecture": [
            {"type": "course", "title": "Software Architecture & Design Patterns", "platform": "Coursera - University of Alberta", "duration": "4 weeks"},
            {"type": "practice", "title": "Refactor one project to MVC pattern", "action": "Separate controllers, services, and data layers", "duration": "2 weeks"},
            {"type": "book", "title": "Clean Architecture", "author": "Robert C. Martin", "chapters": "Chapters 1-12"}
        ],
        "documentation": [
            {"type": "guide", "title": "Write the Docs - Documentation Guide", "platform": "writethedocs.org", "duration": "2 hours"},
            {"type": "practice", "title": "Write README for all repositories", "action": "Include setup, architecture, and API docs", "duration": "3 days"},
            {"type": "tool", "title": "Set up automated documentation", "action": "Learn JSDoc/Swagger for API documentation", "duration": "1 week"}
        ],
        "security": [
            {"type": "course", "title": "Web Security Fundamentals", "platform": "Udemy - Security", "duration": "6 hours"},
            {"type": "practice", "title": "Fix all critical security issues", "action": "Move secrets to env vars, add input validation", "duration": "1 week"},
            {"type": "guide", "title": "OWASP Top 10", "platform": "owasp.org", "duration": "3 hours"}
        ],
        "performance": [
            {"type": "course", "title": "Web Performance Fundamentals", "platform": "web.dev", "duration": "4 hours"},
            {"type": "practice", "title": "Optimize your portfolio site", "action": "Achieve 90+ Lighthouse score", "duration": "1 week"},
            {"type": "tool", "title": "Learn Chrome DevTools Performance", "action": "Profile and optimize rendering", "duration": "3 days"}
        ],
        "typescript": [
            {"type": "course", "title": "TypeScript Deep Dive", "platform": "basarat.gitbook.io", "duration": "10 hours"},
            {"type": "practice", "title": "Convert JS project to TypeScript", "action": "Start with strict mode enabled", "duration": "2 weeks"},
            {"type": "project", "title": "Build typed API client", "action": "Implement full type safety from API to UI", "duration": "1 week"}
        ],
        "frontend_advanced": [
            {"type": "course", "title": "Advanced React Patterns", "platform": "Epic React by Kent C. Dodds", "duration": "12 hours"},
            {"type": "practice", "title": "Implement custom hooks library", "action": "Extract reusable logic from components", "duration": "1 week"},
            {"type": "project", "title": "Build accessible component library", "action": "WCAG 2.1 AA compliant components", "duration": "2 weeks"}
        ],
        "backend_advanced": [
            {"type": "course", "title": "Node.js Design Patterns", "platform": "Packt Publishing", "duration": "8 hours"},
            {"type": "practice", "title": "Implement microservices architecture", "action": "Split monolith into 3 services", "duration": "3 weeks"},
            {"type": "project", "title": "Build real-time API with WebSockets", "action": "Implement chat or notification system", "duration": "1 week"}
        ],
        "devops": [
            {"type": "course", "title": "Docker and Kubernetes Fundamentals", "platform": "Udemy", "duration": "8 hours"},
            {"type": "practice", "title": "Containerize all projects", "action": "Write Dockerfiles and docker-compose", "duration": "1 week"},
            {"type": "project", "title": "Set up CI/CD pipeline", "action": "GitHub Actions for test and deploy", "duration": "1 week"}
        ],
        "system_design": [
            {"type": "course", "title": "System Design Primer", "platform": "GitHub - donnemartin", "duration": "Self-paced"},
            {"type": "practice", "title": "Design URL shortener", "action": "Draw architecture diagram, justify choices", "duration": "3 days"},
            {"type": "practice", "title": "Design real-time chat system", "action": "Include scaling and failure handling", "duration": "1 week"}
        ]
    }
    
    def generate(self, scores, feedback, market_comparison, target_role):
        """Generate a 90-day learning roadmap."""
        
        # Identify weakest skills from scores
        weak_areas = self._identify_weak_areas(scores, feedback)
        
        # Generate week-by-week plan
        weeks = self._generate_weeks(weak_areas, scores, target_role)
        
        # Generate milestones
        milestones = self._generate_milestones(weeks, weak_areas)
        
        # Generate measurable goals
        goals = self._generate_goals(weak_areas, scores)
        
        # Identify projects to keep/remove
        project_advice = self._analyze_projects(scores, feedback)
        
        return {
            "overview": {
                "duration_days": 90,
                "start_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "end_date": (datetime.utcnow() + timedelta(days=90)).strftime("%Y-%m-%d"),
                "target_role": target_role,
                "focus_areas": [w['area'] for w in weak_areas[:4]],
                "estimated_daily_hours": 2,
                "total_estimated_hours": 180
            },
            "phases": self._organize_into_phases(weeks),
            "weeks": weeks,
            "milestones": milestones,
            "measurable_goals": goals,
            "project_recommendations": project_advice,
            "resources": self._compile_resources(weak_areas),
            "success_metrics": self._define_success_metrics(scores, weak_areas)
        }
    
    def _identify_weak_areas(self, scores, feedback):
        """Identify weakest areas from scores and feedback."""
        areas = []
        
        # From scores
        score_areas = {
            'testing': scores.get('testing_score', 0),
            'architecture': scores.get('architecture_score', 0),
            'documentation': scores.get('documentation_score', 0),
            'code_quality': scores.get('code_quality_score', 0),
            'security': scores.get('security_score', 0),
            'performance': scores.get('performance_score', 0),
        }
        
        for area, score in score_areas.items():
            if score < 70:
                areas.append({
                    'area': area,
                    'current_score': score,
                    'target_score': min(100, score + 25),
                    'priority': 'critical' if score < 40 else 'high' if score < 60 else 'medium'
                })
        
        # From feedback
        feedback_areas = defaultdict(list)
        for item in feedback:
            category = item.get('category', 'general').lower()
            feedback_areas[category].append(item)
        
        # Merge feedback with score areas
        for category, items in feedback_areas.items():
            existing = next((a for a in areas if a['area'] == category), None)
            if existing:
                existing['feedback_count'] = len(items)
            else:
                areas.append({
                    'area': category,
                    'current_score': 50,  # Estimated
                    'target_score': 75,
                    'priority': 'medium',
                    'feedback_count': len(items)
                })
        
        # Sort by priority and score
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        areas.sort(key=lambda x: (priority_order.get(x['priority'], 99), x['current_score']))
        
        return areas
    
    def _generate_weeks(self, weak_areas, scores, target_role):
        """Generate week-by-week learning plan."""
        weeks = []
        
        # Week 1-2: Attack critical weaknesses first
        critical = [a for a in weak_areas if a['priority'] == 'critical']
        high = [a for a in weak_areas if a['priority'] == 'high']
        
        # Week 1
        week1_tasks = []
        if critical:
            area = critical[0]
            week1_tasks.extend(self._get_tasks_for_area(area['area'], 'foundation'))
        elif high:
            area = high[0]
            week1_tasks.extend(self._get_tasks_for_area(area['area'], 'foundation'))
        
        weeks.append({
            "week": 1,
            "theme": "Foundation & Critical Fixes",
            "focus": critical[0]['area'] if critical else (high[0]['area'] if high else "Code Quality"),
            "tasks": week1_tasks if week1_tasks else [
                {"action": "Audit all repositories for critical issues", "deliverable": "Issue list with priorities"},
                {"action": "Set up development environment improvements", "deliverable": "Linters, formatters, pre-commit hooks"}
            ],
            "daily_commitment": "2 hours",
            "milestone": "All critical issues identified and fix plan created"
        })
        
        # Week 2
        week2_tasks = []
        if len(critical) > 1:
            week2_tasks.extend(self._get_tasks_for_area(critical[1]['area'], 'foundation'))
        elif critical:
            week2_tasks.extend(self._get_tasks_for_area(critical[0]['area'], 'practice'))
        elif len(high) > 1:
            week2_tasks.extend(self._get_tasks_for_area(high[1]['area'], 'foundation'))
        
        weeks.append({
            "week": 2,
            "theme": "Deep Dive into Primary Weakness",
            "focus": critical[1]['area'] if len(critical) > 1 else (critical[0]['area'] if critical else "Testing"),
            "tasks": week2_tasks if week2_tasks else [
                {"action": "Complete foundational course", "deliverable": "Course completion certificate"},
                {"action": "Implement fixes in primary project", "deliverable": "PR with improvements"}
            ],
            "daily_commitment": "2 hours",
            "milestone": "Primary weakness area shows measurable improvement"
        })
        
        # Week 3-4: Expand to secondary weaknesses
        for week_num in range(3, 5):
            focus_area = None
            if len(high) >= week_num - 2:
                focus_area = high[week_num - 3]['area'] if week_num - 3 < len(high) else high[-1]['area']
            elif len(critical) > 0:
                focus_area = critical[(week_num - 3) % len(critical)]['area']
            else:
                focus_area = "Code Quality"
            
            weeks.append({
                "week": week_num,
                "theme": f"Building {focus_area.replace('_', ' ').title()} Skills",
                "focus": focus_area,
                "tasks": self._get_tasks_for_area(focus_area, 'intermediate'),
                "daily_commitment": "2 hours",
                "milestone": f"{focus_area.replace('_', ' ').title()} score improves by 15+ points"
            })
        
        # Week 5-8: Skill building phase
        themes = [
            (5, "Testing & Quality Assurance", "testing"),
            (6, "Architecture & Design Patterns", "architecture"),
            (7, "Security Best Practices", "security"),
            (8, "Performance Optimization", "performance"),
        ]
        
        for week_num, theme, default_area in themes:
            # Pick an area that needs work
            area = next((a for a in weak_areas if a['area'] in theme.lower()), None)
            if not area:
                area = {'area': default_area, 'priority': 'medium'}
            
            weeks.append({
                "week": week_num,
                "theme": theme,
                "focus": area['area'],
                "tasks": self._get_tasks_for_area(area['area'], 'intermediate'),
                "daily_commitment": "2 hours",
                "milestone": f"Complete {theme.lower()} implementation in one project"
            })
        
        # Week 9-11: Advanced topics
        advanced_themes = [
            (9, "TypeScript & Type Safety", "typescript"),
            (10, "Advanced Patterns", "frontend_advanced" if "frontend" in target_role.lower() else "backend_advanced"),
            (11, "DevOps & CI/CD", "devops"),
        ]
        
        for week_num, theme, default_area in advanced_themes:
            weeks.append({
                "week": week_num,
                "theme": theme,
                "focus": default_area,
                "tasks": self._get_tasks_for_area(default_area, 'advanced'),
                "daily_commitment": "2-3 hours",
                "milestone": f"Production-ready {theme.lower()} implementation"
            })
        
        # Week 12: Polish and portfolio
        weeks.append({
            "week": 12,
            "theme": "Portfolio Polish & Final Review",
            "focus": "portfolio",
            "tasks": [
                {"action": "Update all README files with new improvements", "deliverable": "Documented repositories"},
                {"action": "Run final audit on all projects", "deliverable": "Audit report showing improvements"},
                {"action": "Deploy updated portfolio", "deliverable": "Live portfolio with all improvements"},
                {"action": "Write blog post about learning journey", "deliverable": "Published technical article"}
            ],
            "daily_commitment": "3 hours",
            "milestone": "Portfolio demonstrates measurable skill improvement"
        })
        
        # Week 13: Final push (bonus)
        weeks.append({
            "week": 13,
            "theme": "Market Preparation",
            "focus": "career",
            "tasks": [
                {"action": "Update resume with new skills and projects", "deliverable": "Updated resume"},
                {"action": "Practice system design interviews", "deliverable": "3 mock interviews completed"},
                {"action": "Apply to 5 target companies", "deliverable": "Applications submitted"}
            ],
            "daily_commitment": "2 hours",
            "milestone": "Ready for senior-level interviews"
        })
        
        return weeks
    
    def _get_tasks_for_area(self, area, level):
        """Get learning tasks for a specific area and level."""
        area_normalized = area.lower().replace(' ', '_')
        
        resources = self.RESOURCES.get(area_normalized, self.RESOURCES.get('code_quality', []))
        
        tasks = []
        for resource in resources[:3]:
            task = {
                "action": resource.get('title', resource.get('action', 'Study')),
                "deliverable": resource.get('action', 'Complete exercise') if resource.get('type') == 'practice' else f"Finish {resource.get('title', 'module')}",
                "resource": resource,
                "level": level
            }
            tasks.append(task)
        
        return tasks
    
    def _generate_milestones(self, weeks, weak_areas):
        """Generate key milestones for the roadmap."""
        milestones = []
        
        # 30-day milestone
        milestones.append({
            "day": 30,
            "title": "Foundation Complete",
            "description": "All critical weaknesses identified and initial fixes implemented",
            "deliverables": [
                "Critical security issues fixed",
                "Test coverage improved by 20%",
                "Documentation added to all repos"
            ],
            "success_criteria": "No critical issues remaining in any repository"
        })
        
        # 60-day milestone
        milestones.append({
            "day": 60,
            "title": "Skill Building Progress",
            "description": "Intermediate skills developed in primary weak areas",
            "deliverables": [
                "One project fully tested (70%+ coverage)",
                "One project refactored with proper architecture",
                "Security best practices implemented"
            ],
            "success_criteria": "Overall quality score improved by 15+ points"
        })
        
        # 90-day milestone
        milestones.append({
            "day": 90,
            "title": "Portfolio Ready",
            "description": "Demonstrable skill improvement across all weak areas",
            "deliverables": [
                "Portfolio reflects senior-level practices",
                "All projects have tests, docs, and clean architecture",
                "Technical blog post published"
            ],
            "success_criteria": "Ready for senior-level role interviews"
        })
        
        return milestones
    
    def _generate_goals(self, weak_areas, scores):
        """Generate measurable goals."""
        goals = []
        
        for area in weak_areas[:4]:
            current = area.get('current_score', 50)
            target = min(100, current + 25)
            
            goals.append({
                "area": area['area'].replace('_', ' ').title(),
                "current": current,
                "target": target,
                "measurement_method": f"Automated audit score improvement",
                "deadline_days": 90,
                "priority": area.get('priority', 'medium')
            })
        
        # Overall goal
        overall = scores.get('overall_score', 50)
        goals.append({
            "area": "Overall Developer Level",
            "current": f"{overall}/100",
            "target": f"{min(100, overall + 20)}/100",
            "measurement_method": "Complete re-audit after 90 days",
            "deadline_days": 90,
            "priority": "high"
        })
        
        return goals
    
    def _analyze_projects(self, scores, feedback):
        """Analyze which projects to keep, improve, or remove."""
        advice = []
        
        # Projects with critical issues should be fixed or removed
        critical_repos = set()
        for item in feedback:
            if item.get('severity') == 'critical' and item.get('repo'):
                critical_repos.add(item.get('repo'))
        
        for repo in critical_repos:
            advice.append({
                "project": repo,
                "recommendation": "URGENT: Fix critical issues or remove from resume",
                "action": "Address all critical security and quality issues before showcasing",
                "impact": "Currently damaging your profile"
            })
        
        # Projects with good quality should be highlighted
        advice.append({
            "project": "Best repository",
            "recommendation": "Lead with your strongest project",
            "action": "Ensure README, tests, and documentation are perfect",
            "impact": "First impression for recruiters"
        })
        
        # General advice
        advice.append({
            "project": "All projects",
            "recommendation": "Maintain consistent quality across all visible work",
            "action": "Every public repo should represent your current skill level",
            "impact": "Recruiters check multiple repositories"
        })
        
        return advice
    
    def _compile_resources(self, weak_areas):
        """Compile learning resources for weak areas."""
        resources = []
        
        for area in weak_areas[:4]:
            area_key = area['area'].lower().replace(' ', '_')
            area_resources = self.RESOURCES.get(area_key, [])
            
            resources.append({
                "area": area['area'].replace('_', ' ').title(),
                "resources": area_resources[:3]
            })
        
        return resources
    
    def _define_success_metrics(self, scores, weak_areas):
        """Define how success will be measured."""
        return {
            "primary_metrics": [
                {"metric": "Overall audit score", "current": scores.get('overall_score', 50), "target": min(100, scores.get('overall_score', 50) + 20)},
                {"metric": "Test coverage average", "current": scores.get('testing_score', 0), "target": 70},
                {"metric": "Architecture score", "current": scores.get('architecture_score', 0), "target": 75},
            ],
            "secondary_metrics": [
                {"metric": "Critical issues count", "current": len([a for a in weak_areas if a['priority'] == 'critical']), "target": 0},
                {"metric": "Documentation score", "current": scores.get('documentation_score', 0), "target": 70},
                {"metric": "Code quality score", "current": scores.get('code_quality_score', 0), "target": 75},
            ],
            "validation_method": "Re-run this audit after 90 days to measure improvement"
        }
    
    def _organize_into_phases(self, weeks):
        """Organize weeks into phases."""
        return [
            {
                "phase": 1,
                "name": "Critical Fixes (Weeks 1-2)",
                "description": "Address all critical issues in existing projects",
                "weeks": [1, 2],
                "focus": "Damage control and quick wins"
            },
            {
                "phase": 2,
                "name": "Foundation Building (Weeks 3-6)",
                "description": "Build foundational skills in weakest areas",
                "weeks": [3, 4, 5, 6],
                "focus": "Testing, architecture, and documentation"
            },
            {
                "phase": 3,
                "name": "Skill Expansion (Weeks 7-10)",
                "description": "Develop advanced skills and new technologies",
                "weeks": [7, 8, 9, 10],
                "focus": "Security, performance, TypeScript, advanced patterns"
            },
            {
                "phase": 4,
                "name": "Portfolio Polish (Weeks 11-13)",
                "description": "Polish portfolio and prepare for market",
                "weeks": [11, 12, 13],
                "focus": "DevOps, portfolio deployment, interview prep"
            }
        ]
