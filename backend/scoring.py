"""
Scoring Engine
Calculates comprehensive scores across all dimensions and determines demonstrated level.
"""


class ScoringEngine:
    """Calculates developer skill scores across multiple dimensions."""
    
    # Score thresholds for each level
    LEVEL_THRESHOLDS = {
        'Junior': {'min': 0, 'max': 45},
        'Mid-Level': {'min': 45, 'max': 65},
        'Senior': {'min': 65, 'max': 82},
        'Staff': {'min': 82, 'max': 100},
    }
    
    # Role type weights
    ROLE_WEIGHTS = {
        'frontend': {
            'code_quality': 0.20,
            'testing': 0.15,
            'documentation': 0.10,
            'architecture': 0.15,
            'naming_conventions': 0.10,
            'modularity': 0.15,
            'security': 0.05,
            'performance': 0.10
        },
        'backend': {
            'code_quality': 0.15,
            'testing': 0.20,
            'documentation': 0.10,
            'architecture': 0.20,
            'naming_conventions': 0.10,
            'modularity': 0.10,
            'security': 0.10,
            'performance': 0.05
        },
        'fullstack': {
            'code_quality': 0.15,
            'testing': 0.15,
            'documentation': 0.10,
            'architecture': 0.18,
            'naming_conventions': 0.10,
            'modularity': 0.12,
            'security': 0.10,
            'performance': 0.10
        },
        'default': {
            'code_quality': 0.15,
            'testing': 0.15,
            'documentation': 0.10,
            'architecture': 0.18,
            'naming_conventions': 0.10,
            'modularity': 0.12,
            'security': 0.10,
            'performance': 0.10
        }
    }
    
    def calculate_all_scores(self, github_data, code_quality, live_audit, security_results, 
                            claimed_role, claimed_years):
        """Calculate all dimension scores and overall level."""
        
        # Determine role type for weighting
        role_type = self._detect_role_type(claimed_role)
        weights = self.ROLE_WEIGHTS.get(role_type, self.ROLE_WEIGHTS['default'])
        
        # Calculate individual dimension scores
        code_quality_score = self._calculate_code_quality_score(code_quality)
        testing_score = self._calculate_testing_score(code_quality)
        documentation_score = self._calculate_documentation_score(code_quality, github_data)
        architecture_score = self._calculate_architecture_score(code_quality)
        naming_score = self._calculate_naming_score(code_quality)
        modularity_score = self._calculate_modularity_score(code_quality)
        security_score = self._calculate_security_score(security_results)
        performance_score = self._calculate_performance_score(live_audit)
        
        # Calculate GitHub activity score
        activity_score = self._calculate_activity_score(github_data)
        
        # Weighted overall score
        overall_score = (
            code_quality_score * weights['code_quality'] +
            testing_score * weights['testing'] +
            documentation_score * weights['documentation'] +
            architecture_score * weights['architecture'] +
            naming_score * weights['naming_conventions'] +
            modularity_score * weights['modularity'] +
            security_score * weights['security'] +
            performance_score * weights['performance']
        )
        
        # Determine demonstrated level
        demonstrated_level = self._determine_level(overall_score)
        
        # Check if claimed level matches demonstrated level
        claimed_level = self._parse_claimed_level(claimed_role, claimed_years)
        level_match = self._check_level_match(demonstrated_level, claimed_level)
        
        # Calculate individual dimension ratings (1-10)
        dimension_ratings = {
            'code_quality': self._score_to_rating(code_quality_score),
            'testing': self._score_to_rating(testing_score),
            'documentation': self._score_to_rating(documentation_score),
            'architecture': self._score_to_rating(architecture_score),
            'naming_conventions': self._score_to_rating(naming_score),
            'modularity': self._score_to_rating(modularity_score),
            'security': self._score_to_rating(security_score),
            'performance': self._score_to_rating(performance_score),
            'github_activity': self._score_to_rating(activity_score)
        }
        
        return {
            'overall_score': round(overall_score, 1),
            'overall_level': demonstrated_level,
            'claimed_level': claimed_level,
            'level_match': level_match,
            'role_type': role_type,
            'dimension_scores': {
                'code_quality': round(code_quality_score, 1),
                'testing': round(testing_score, 1),
                'documentation': round(documentation_score, 1),
                'architecture': round(architecture_score, 1),
                'naming_conventions': round(naming_score, 1),
                'modularity': round(modularity_score, 1),
                'security': round(security_score, 1),
                'performance': round(performance_score, 1),
                'github_activity': round(activity_score, 1)
            },
            'dimension_ratings': dimension_ratings,
            'weights_used': weights
        }
    
    def _detect_role_type(self, claimed_role):
        """Detect role type from claimed role string."""
        role_lower = claimed_role.lower()
        if 'frontend' in role_lower or 'front-end' in role_lower or 'ui' in role_lower:
            return 'frontend'
        elif 'backend' in role_lower or 'back-end' in role_lower or 'api' in role_lower:
            return 'backend'
        elif 'full' in role_lower or 'fullstack' in role_lower:
            return 'fullstack'
        return 'default'
    
    def _calculate_code_quality_score(self, code_quality):
        """Calculate code quality score from analysis."""
        aggregate = code_quality.get('aggregate_scores', {})
        
        # Base score from overall quality
        base = aggregate.get('overall_quality_score', 50)
        
        # Adjust for code smells
        smell_count = aggregate.get('total_code_smells', 0)
        smell_penalty = min(20, smell_count * 3)
        
        score = base - smell_penalty
        return max(0, min(100, score))
    
    def _calculate_testing_score(self, code_quality):
        """Calculate testing practices score."""
        aggregate = code_quality.get('aggregate_scores', {})
        
        coverage = aggregate.get('test_coverage_avg', 0)
        
        # Score based on coverage
        if coverage >= 80:
            score = 90 + (coverage - 80) * 0.5
        elif coverage >= 60:
            score = 70 + (coverage - 60) * 1.0
        elif coverage >= 40:
            score = 50 + (coverage - 40) * 1.0
        elif coverage >= 20:
            score = 30 + (coverage - 20) * 1.0
        else:
            score = coverage * 1.5
        
        return max(0, min(100, score))
    
    def _calculate_documentation_score(self, code_quality, github_data):
        """Calculate documentation quality score."""
        aggregate = code_quality.get('aggregate_scores', {})
        
        base = aggregate.get('documentation_avg', 50)
        
        # Check if bio exists
        bio = github_data.get('bio', '')
        if bio and len(bio) > 20:
            base += 5
        
        return max(0, min(100, base))
    
    def _calculate_architecture_score(self, code_quality):
        """Calculate architecture quality score."""
        aggregate = code_quality.get('aggregate_scores', {})
        
        arch = aggregate.get('architecture_avg', 50)
        modularity = aggregate.get('modularity_score', 50)
        
        # Weight architecture higher
        score = arch * 0.6 + modularity * 0.4
        
        return max(0, min(100, score))
    
    def _calculate_naming_score(self, code_quality):
        """Calculate naming conventions score."""
        aggregate = code_quality.get('aggregate_scores', {})
        
        return aggregate.get('naming_avg', 50)
    
    def _calculate_modularity_score(self, code_quality):
        """Calculate modularity score."""
        aggregate = code_quality.get('aggregate_scores', {})
        
        return aggregate.get('modularity_score', 50)
    
    def _calculate_security_score(self, security_results):
        """Calculate security practices score."""
        if not security_results or not security_results.get('issues'):
            # No security scan performed
            return 50
        
        score = security_results.get('security_score', 50)
        return score
    
    def _calculate_performance_score(self, live_audit):
        """Calculate performance score from live app audit."""
        if not live_audit or not live_audit.get('performed'):
            return 50  # Neutral if no audit
        
        scores = live_audit.get('scores', {})
        if not scores:
            return 50
        
        # Average of performance-related scores
        perf = scores.get('performance', 50)
        animation = scores.get('animation', 50)
        interaction = scores.get('interaction', 50)
        
        return (perf + animation + interaction) / 3
    
    def _calculate_activity_score(self, github_data):
        """Calculate GitHub activity score."""
        commit_patterns = github_data.get('commit_patterns', {})
        
        avg_commits = commit_patterns.get('avg_commits_per_week', 0)
        total_commits = commit_patterns.get('total_commits_analyzed', 0)
        consistency = commit_patterns.get('consistency_score', 0)
        
        # Score based on commit frequency
        if avg_commits >= 10:
            commit_score = 90
        elif avg_commits >= 7:
            commit_score = 80
        elif avg_commits >= 4:
            commit_score = 65
        elif avg_commits >= 2:
            commit_score = 45
        else:
            commit_score = 25
        
        # Factor in consistency and total
        score = (commit_score * 0.5 + consistency * 0.3 + 
                min(100, total_commits / 10) * 0.2)
        
        return min(100, score)
    
    def _determine_level(self, overall_score):
        """Determine demonstrated level from overall score."""
        for level, thresholds in sorted(self.LEVEL_THRESHOLDS.items(), 
                                       key=lambda x: x[1]['min']):
            if thresholds['min'] <= overall_score < thresholds['max']:
                return level
        
        # If score is at max, return highest level
        return 'Staff'
    
    def _parse_claimed_level(self, claimed_role, claimed_years):
        """Parse claimed level from role and years."""
        role_lower = claimed_role.lower()
        
        if 'staff' in role_lower or 'principal' in role_lower:
            return 'Staff'
        elif 'senior' in role_lower or 'sr.' in role_lower or 'lead' in role_lower:
            return 'Senior'
        elif 'mid' in role_lower:
            return 'Mid-Level'
        elif 'junior' in role_lower or 'jr.' in role_lower:
            return 'Junior'
        
        # Infer from years
        if claimed_years >= 8:
            return 'Senior'
        elif claimed_years >= 5:
            return 'Senior'
        elif claimed_years >= 3:
            return 'Mid-Level'
        elif claimed_years >= 1:
            return 'Junior'
        
        return 'Junior'
    
    def _check_level_match(self, demonstrated, claimed):
        """Check if demonstrated level matches claimed level."""
        level_order = {'Junior': 1, 'Mid-Level': 2, 'Senior': 3, 'Staff': 4}
        
        demo_val = level_order.get(demonstrated, 0)
        claimed_val = level_order.get(claimed, 0)
        
        if demo_val >= claimed_val:
            return True
        elif claimed_val - demo_val <= 1:
            return 'partial'  # One level off
        else:
            return False
    
    def _score_to_rating(self, score):
        """Convert 0-100 score to 1-10 rating."""
        return round(max(1, min(10, score / 10)), 1)
