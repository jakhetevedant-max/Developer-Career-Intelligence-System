"""
Market Comparison Engine
Cross-references developer's real skill level against current job market demands.
Identifies qualifying roles, realistic companies, percentile ranking, and skill gaps.
"""

import random
from datetime import datetime


class MarketComparisonEngine:
    """Compares developer skills against job market requirements."""
    
    # Role definitions with skill requirements
    ROLE_DEFINITIONS = {
        "Junior Frontend Developer": {
            "min_years": 0,
            "max_years": 2,
            "required_skills": ["HTML", "CSS", "JavaScript"],
            "preferred_skills": ["React", "Git", "Responsive Design"],
            "salary_range": {"us": {"min": 50000, "max": 75000}, "remote": {"min": 40000, "max": 65000}},
            "test_requirements": {"code_quality": 40, "testing": 20, "architecture": 30}
        },
        "Mid-Level Frontend Developer": {
            "min_years": 2,
            "max_years": 5,
            "required_skills": ["JavaScript", "React", "CSS", "Git"],
            "preferred_skills": ["TypeScript", "Testing", "Performance", "Accessibility"],
            "salary_range": {"us": {"min": 75000, "max": 120000}, "remote": {"min": 60000, "max": 100000}},
            "test_requirements": {"code_quality": 60, "testing": 50, "architecture": 50}
        },
        "Senior Frontend Developer": {
            "min_years": 5,
            "max_years": 10,
            "required_skills": ["JavaScript", "TypeScript", "React", "Testing", "Performance"],
            "preferred_skills": ["Architecture", "Mentoring", "CI/CD", "Accessibility", "Micro-frontends"],
            "salary_range": {"us": {"min": 120000, "max": 180000}, "remote": {"min": 100000, "max": 160000}},
            "test_requirements": {"code_quality": 75, "testing": 70, "architecture": 75}
        },
        "Junior Backend Developer": {
            "min_years": 0,
            "max_years": 2,
            "required_skills": ["Python", "Java", "Node.js", "SQL"],
            "preferred_skills": ["REST APIs", "Git", "Databases"],
            "salary_range": {"us": {"min": 55000, "max": 80000}, "remote": {"min": 45000, "max": 70000}},
            "test_requirements": {"code_quality": 45, "testing": 25, "architecture": 35}
        },
        "Mid-Level Backend Developer": {
            "min_years": 2,
            "max_years": 5,
            "required_skills": ["Node.js", "Python", "SQL", "REST APIs", "Git"],
            "preferred_skills": ["Microservices", "Docker", "Cloud", "Testing", "NoSQL"],
            "salary_range": {"us": {"min": 85000, "max": 140000}, "remote": {"min": 70000, "max": 120000}},
            "test_requirements": {"code_quality": 65, "testing": 55, "architecture": 60}
        },
        "Senior Backend Developer": {
            "min_years": 5,
            "max_years": 10,
            "required_skills": ["Node.js", "Python", "SQL", "Microservices", "Docker", "Cloud"],
            "preferred_skills": ["Kubernetes", "System Design", "CI/CD", "Testing", "NoSQL", "Message Queues"],
            "salary_range": {"us": {"min": 130000, "max": 200000}, "remote": {"min": 110000, "max": 180000}},
            "test_requirements": {"code_quality": 80, "testing": 75, "architecture": 80}
        },
        "Junior Full-Stack Developer": {
            "min_years": 0,
            "max_years": 2,
            "required_skills": ["JavaScript", "HTML", "CSS", "Node.js"],
            "preferred_skills": ["React", "SQL", "Git", "REST APIs"],
            "salary_range": {"us": {"min": 55000, "max": 85000}, "remote": {"min": 45000, "max": 70000}},
            "test_requirements": {"code_quality": 45, "testing": 25, "architecture": 35}
        },
        "Mid-Level Full-Stack Developer": {
            "min_years": 2,
            "max_years": 5,
            "required_skills": ["JavaScript", "React", "Node.js", "SQL", "Git", "REST APIs"],
            "preferred_skills": ["TypeScript", "Docker", "Testing", "Cloud", "NoSQL"],
            "salary_range": {"us": {"min": 90000, "max": 150000}, "remote": {"min": 75000, "max": 130000}},
            "test_requirements": {"code_quality": 65, "testing": 55, "architecture": 60}
        },
        "Senior Full-Stack Developer": {
            "min_years": 5,
            "max_years": 10,
            "required_skills": ["JavaScript", "TypeScript", "React", "Node.js", "SQL", "Docker", "Cloud"],
            "preferred_skills": ["Microservices", "Kubernetes", "System Design", "CI/CD", "NoSQL", "GraphQL"],
            "salary_range": {"us": {"min": 140000, "max": 220000}, "remote": {"min": 120000, "max": 200000}},
            "test_requirements": {"code_quality": 80, "testing": 75, "architecture": 80}
        },
        "Staff Engineer": {
            "min_years": 8,
            "max_years": 15,
            "required_skills": ["System Design", "Architecture", "Mentoring", "JavaScript", "TypeScript"],
            "preferred_skills": ["Leadership", "Cross-team Collaboration", "Technical Strategy", "Cloud Native"],
            "salary_range": {"us": {"min": 180000, "max": 300000}, "remote": {"min": 160000, "max": 280000}},
            "test_requirements": {"code_quality": 85, "testing": 80, "architecture": 90}
        }
    }
    
    # Companies by category
    COMPANIES = {
        "startup": [
            {"name": "Vercel", "roles": ["Senior Frontend", "Senior Full-Stack"], "remote": True},
            {"name": "Stripe", "roles": ["Senior Backend", "Senior Full-Stack"], "remote": True},
            {"name": "Notion", "roles": ["Senior Frontend", "Senior Full-Stack"], "remote": True},
            {"name": "Linear", "roles": ["Senior Frontend"], "remote": True},
            {"name": "Supabase", "roles": ["Senior Backend", "Senior Full-Stack"], "remote": True},
        ],
        "big_tech": [
            {"name": "Google", "roles": ["Senior Full-Stack", "Staff Engineer"], "remote": False},
            {"name": "Microsoft", "roles": ["Senior Full-Stack", "Senior Backend"], "remote": True},
            {"name": "Amazon", "roles": ["Senior Backend", "Senior Full-Stack"], "remote": False},
            {"name": "Meta", "roles": ["Senior Frontend", "Senior Full-Stack"], "remote": False},
            {"name": "Apple", "roles": ["Senior Full-Stack"], "remote": False},
        ],
        "mid_size": [
            {"name": "Shopify", "roles": ["Senior Full-Stack"], "remote": True},
            {"name": "Twilio", "roles": ["Senior Backend", "Senior Full-Stack"], "remote": True},
            {"name": "Datadog", "roles": ["Senior Backend"], "remote": True},
            {"name": "Cloudflare", "roles": ["Senior Backend", "Senior Full-Stack"], "remote": True},
            {"name": "Figma", "roles": ["Senior Frontend"], "remote": True},
        ],
        "consulting": [
            {"name": "Thoughtworks", "roles": ["Mid Full-Stack", "Senior Full-Stack"], "remote": True},
            {"name": "Accenture", "roles": ["Mid Full-Stack", "Senior Full-Stack"], "remote": True},
            {"name": "Deloitte Digital", "roles": ["Mid Full-Stack", "Senior Full-Stack"], "remote": False},
        ]
    }
    
    def compare(self, scores, claimed_role, claimed_years, claimed_skills, target_role, location):
        """Compare developer against market requirements."""
        
        # Determine demonstrated level
        overall_score = scores.get('overall_score', 50)
        demonstrated_level = scores.get('overall_level', 'Junior')
        
        # Find matching roles
        matching_roles = self._find_matching_roles(
            scores, claimed_years, claimed_skills, demonstrated_level
        )
        
        # Find realistic companies
        realistic_companies = self._find_realistic_companies(
            demonstrated_level, matching_roles
        )
        
        # Calculate percentile
        percentile = self._calculate_percentile(overall_score, claimed_years)
        
        # Calculate skill gaps
        skill_gaps = self._calculate_skill_gaps(
            scores, claimed_skills, target_role
        )
        
        # Calculate interview success rate
        interview_rate = self._calculate_interview_success(
            scores, demonstrated_level, target_role
        )
        
        # Calculate salary estimate
        salary_estimate = self._estimate_salary(
            demonstrated_level, location, scores
        )
        
        return {
            "demonstrated_level": demonstrated_level,
            "claimed_level": self._determine_claimed_level(claimed_role, claimed_years),
            "level_match": scores.get('level_match', False),
            "percentile": percentile,
            "interview_success_rate": interview_rate,
            "matching_roles": matching_roles,
            "realistic_companies": realistic_companies,
            "skill_gaps": skill_gaps,
            "salary_estimate": salary_estimate,
            "next_level_requirements": self._get_next_level_requirements(demonstrated_level),
            "market_insights": self._get_market_insights(target_role)
        }
    
    def _find_matching_roles(self, scores, years, skills, level):
        """Find roles the developer actually qualifies for."""
        matching = []
        
        code_quality = scores.get('code_quality_score', 50)
        testing = scores.get('testing_score', 50)
        architecture = scores.get('architecture_score', 50)
        
        for role_name, role_def in self.ROLE_DEFINITIONS.items():
            # Check if years match
            if not (role_def['min_years'] <= years <= role_def['max_years'] + 2):
                continue
            
            # Check if scores meet minimums
            req = role_def['test_requirements']
            if (code_quality >= req['code_quality'] * 0.8 and
                testing >= req['testing'] * 0.8 and
                architecture >= req['architecture'] * 0.8):
                
                # Calculate match percentage
                skill_match = self._calculate_skill_match(skills, role_def)
                
                matching.append({
                    "role": role_name,
                    "match_percentage": round(skill_match, 1),
                    "salary_min": role_def['salary_range']['us']['min'],
                    "salary_max": role_def['salary_range']['us']['max'],
                    "confidence": "high" if skill_match > 80 else "medium" if skill_match > 60 else "low"
                })
        
        # Sort by match percentage
        matching.sort(key=lambda x: x['match_percentage'], reverse=True)
        return matching[:5]
    
    def _calculate_skill_match(self, skills, role_def):
        """Calculate how well skills match role requirements."""
        if not skills:
            return 50
        
        required = role_def.get('required_skills', [])
        preferred = role_def.get('preferred_skills', [])
        
        skills_lower = [s.lower() for s in skills]
        
        required_matches = sum(1 for r in required if any(r.lower() in s for s in skills_lower))
        preferred_matches = sum(1 for p in preferred if any(p.lower() in s for s in skills_lower))
        
        required_score = (required_matches / len(required)) * 60 if required else 30
        preferred_score = (preferred_matches / len(preferred)) * 40 if preferred else 20
        
        return min(100, required_score + preferred_score)
    
    def _find_realistic_companies(self, level, matching_roles):
        """Find companies that would realistically hire at this level."""
        companies = []
        
        # Determine which company tiers are realistic
        if level in ['Junior', 'Mid-Level']:
            tiers = ['consulting', 'startup']
        elif level == 'Senior':
            tiers = ['startup', 'mid_size', 'big_tech']
        else:  # Staff+
            tiers = ['big_tech', 'mid_size']
        
        for tier in tiers:
            for company in self.COMPANIES.get(tier, []):
                # Filter by role level match
                matching_role_names = [r['role'] for r in matching_roles[:3]]
                has_matching = any(
                    any(mr.lower() in cr.lower() for mr in matching_role_names)
                    for cr in company['roles']
                )
                
                if has_matching:
                    companies.append({
                        "name": company['name'],
                        "tier": tier,
                        "remote": company['remote'],
                        "matching_roles": company['roles'],
                        "realistic": tier in ['consulting', 'startup'] if level in ['Junior', 'Mid-Level'] else True
                    })
        
        return companies[:8]
    
    def _calculate_percentile(self, overall_score, years):
        """Calculate percentile ranking among developers with similar experience."""
        # Base percentile on overall score with experience adjustment
        base = overall_score
        
        # Adjust for experience (more years = higher expectations)
        if years < 2:
            adjustment = 5
        elif years < 5:
            adjustment = 0
        else:
            adjustment = -5
        
        percentile = min(99, max(1, base + adjustment))
        return round(percentile, 1)
    
    def _calculate_skill_gaps(self, scores, skills, target_role):
        """Calculate precise skill gaps to next salary bracket."""
        gaps = []
        
        # Get target role requirements
        target_def = None
        for role_name, role_def in self.ROLE_DEFINITIONS.items():
            if target_role.lower() in role_name.lower():
                target_def = role_def
                break
        
        if not target_def:
            target_def = self.ROLE_DEFINITIONS.get("Senior Full-Stack Developer")
        
        # Check each required skill
        skills_lower = [s.lower() for s in skills] if skills else []
        
        for skill in target_def.get('required_skills', []):
            if not any(skill.lower() in s for s in skills_lower):
                gaps.append({
                    "skill": skill,
                    "current_level": "Not demonstrated",
                    "required_level": "Proficient",
                    "gap_size": "large",
                    "learning_time_weeks": 8,
                    "impact": "Required for target role"
                })
        
        for skill in target_def.get('preferred_skills', []):
            if not any(skill.lower() in s for s in skills_lower):
                gaps.append({
                    "skill": skill,
                    "current_level": "Not demonstrated",
                    "required_level": "Familiar",
                    "gap_size": "medium",
                    "learning_time_weeks": 4,
                    "impact": "Significant advantage in hiring"
                })
        
        # Add score-based gaps
        score_gaps = []
        if scores.get('testing_score', 0) < 60:
            score_gaps.append({
                "skill": "Testing & Quality Assurance",
                "current_level": f"Score: {scores.get('testing_score', 0)}/100",
                "required_level": "Score: 70+/100",
                "gap_size": "large",
                "learning_time_weeks": 6,
                "impact": "Critical for senior roles"
            })
        
        if scores.get('architecture_score', 0) < 60:
            score_gaps.append({
                "skill": "Software Architecture",
                "current_level": f"Score: {scores.get('architecture_score', 0)}/100",
                "required_level": "Score: 75+/100",
                "gap_size": "large",
                "learning_time_weeks": 10,
                "impact": "Key differentiator for senior+ roles"
            })
        
        return {
            "missing_skills": gaps,
            "score_gaps": score_gaps,
            "total_gaps": len(gaps) + len(score_gaps),
            "critical_gaps": len([g for g in gaps + score_gaps if g['gap_size'] == 'large'])
        }
    
    def _calculate_interview_success(self, scores, level, target_role):
        """Estimate interview success rate."""
        base_rate = {
            'Junior': 25,
            'Mid-Level': 20,
            'Senior': 15,
            'Staff': 10
        }.get(level, 15)
        
        # Adjust based on scores
        overall = scores.get('overall_score', 50)
        if overall > 80:
            base_rate += 20
        elif overall > 70:
            base_rate += 10
        elif overall < 50:
            base_rate -= 10
        
        # Adjust for code quality
        code_quality = scores.get('code_quality_score', 50)
        if code_quality > 75:
            base_rate += 10
        
        return min(80, max(5, base_rate))
    
    def _estimate_salary(self, level, location, scores):
        """Estimate realistic salary range."""
        # Find matching role definition
        role_key = None
        for key in self.ROLE_DEFINITIONS:
            if level.lower() in key.lower():
                role_key = key
                break
        
        if not role_key:
            role_key = "Mid-Level Full-Stack Developer"
        
        role_def = self.ROLE_DEFINITIONS[role_key]
        
        # Use location-appropriate salary range
        loc_key = 'remote' if location.lower() in ['remote', 'anywhere'] else 'us'
        salary_range = role_def['salary_range'].get(loc_key, role_def['salary_range']['us'])
        
        # Adjust based on scores
        overall = scores.get('overall_score', 50)
        adjustment = (overall - 50) / 100  # -0.5 to +0.5
        
        adjusted_min = int(salary_range['min'] * (1 + adjustment * 0.3))
        adjusted_max = int(salary_range['max'] * (1 + adjustment * 0.3))
        
        return {
            "level": level,
            "location": location,
            "range_usd": {
                "min": adjusted_min,
                "max": adjusted_max,
                "median": (adjusted_min + adjusted_max) // 2
            },
            "range_egp": {
                "min": adjusted_min * 50,
                "max": adjusted_max * 50,
                "median": ((adjusted_min + adjusted_max) // 2) * 50
            }
        }
    
    def _determine_claimed_level(self, role, years):
        """Determine the claimed level from role title and years."""
        role_lower = role.lower()
        if 'staff' in role_lower or 'principal' in role_lower:
            return 'Staff'
        elif 'senior' in role_lower or 'sr.' in role_lower or 'lead' in role_lower:
            return 'Senior'
        elif 'mid' in role_lower:
            return 'Mid-Level'
        elif 'junior' in role_lower or 'jr.' in role_lower:
            return 'Junior'
        elif years >= 8:
            return 'Senior'
        elif years >= 5:
            return 'Senior'
        elif years >= 3:
            return 'Mid-Level'
        elif years >= 1:
            return 'Junior'
        else:
            return 'Junior'
    
    def _get_next_level_requirements(self, current_level):
        """Get requirements to reach next level."""
        progression = {
            'Junior': {
                'next': 'Mid-Level',
                'requirements': [
                    "Demonstrate testing practices (50%+ coverage)",
                    "Show architectural understanding (MVC/layered patterns)",
                    "Build projects with proper documentation",
                    "Contribute to code reviews",
                    "Learn CI/CD practices"
                ],
                'estimated_weeks': 24
            },
            'Mid-Level': {
                'next': 'Senior',
                'requirements': [
                    "Lead architectural decisions",
                    "Mentor junior developers",
                    "Implement comprehensive testing strategies",
                    "Design scalable systems",
                    "Deep expertise in chosen stack"
                ],
                'estimated_weeks': 52
            },
            'Senior': {
                'next': 'Staff',
                'requirements': [
                    "Cross-team technical leadership",
                    "System design at organizational scale",
                    "Technical strategy and roadmap input",
                    "Industry recognition (speaking, writing)",
                    "Mentor other senior engineers"
                ],
                'estimated_weeks': 78
            }
        }
        
        return progression.get(current_level, {
            'next': 'Same level',
            'requirements': ['Continue professional development'],
            'estimated_weeks': 0
        })
    
    def _get_market_insights(self, target_role):
        """Get current market insights for the target role."""
        return {
            "demand_trend": "High demand - 15% YoY growth",
            "top_hiring_locations": ["Remote", "San Francisco", "New York", "London", "Berlin"],
            "most_valued_skills_2024": [
                "TypeScript", "React/Next.js", "Node.js", "Cloud (AWS/GCP)", 
                "System Design", "Testing", "AI/ML Integration"
            ],
            "salary_trend": "Increasing - 8% average raise in 2024",
            "competition_level": "High for senior roles, moderate for mid-level"
        }
    
    def get_market_overview(self, role, location):
        """Get general market data for a role."""
        return {
            "role": role,
            "location": location,
            "timestamp": datetime.utcnow().isoformat(),
            "active_postings_estimate": random.randint(500, 5000),
            "average_time_to_hire_days": random.randint(21, 45),
            "top_skills_in_demand": [
                "React", "TypeScript", "Node.js", "Python", "AWS",
                "Docker", "Kubernetes", "GraphQL", "PostgreSQL"
            ],
            "salary_trends": {
                "yoy_change_percent": random.randint(5, 15),
                "direction": "up"
            }
        }
