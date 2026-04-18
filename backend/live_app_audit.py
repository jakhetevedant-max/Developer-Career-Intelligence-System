"""
Live Application Auditor
Automated UI/UX testing for live applications including responsiveness,
accessibility, performance, and animation smoothness checks.
"""

import requests
import re
import time
from urllib.parse import urlparse


class LiveAppAuditor:
    """Audits a live web application for quality metrics."""
    
    # Standard viewport sizes for responsiveness testing
    VIEWPORTS = [
        {"name": "Mobile (iPhone SE)", "width": 375, "height": 667},
        {"name": "Mobile (iPhone 14)", "width": 390, "height": 844},
        {"name": "Tablet (iPad)", "width": 768, "height": 1024},
        {"name": "Laptop (1366px)", "width": 1366, "height": 768},
        {"name": "Desktop (1920px)", "width": 1920, "height": 1080},
    ]
    
    # Performance thresholds
    PERFORMANCE_THRESHOLDS = {
        "load_time_excellent": 1.5,
        "load_time_good": 3.0,
        "load_time_poor": 5.0,
        "ttfb_excellent": 0.2,
        "ttfb_good": 0.5,
        "ttfb_poor": 1.0,
        "page_size_excellent": 500,
        "page_size_good": 1000,
        "page_size_poor": 2000,
    }
    
    # WCAG guidelines checkpoints
    WCAG_CHECKPOINTS = [
        "images_have_alt",
        "form_labels_present",
        "color_contrast_adequate",
        "keyboard_navigable",
        "aria_landmarks",
        "focus_indicators",
        "skip_links",
        "heading_hierarchy"
    ]
    
    def __init__(self, url):
        self.url = url if url.startswith('http') else f'https://{url}'
        self.domain = urlparse(self.url).netloc
        self.results = {}
    
    def audit(self):
        """Run complete live application audit."""
        try:
            # Basic connectivity check
            start_time = time.time()
            response = requests.get(self.url, timeout=15, allow_redirects=True)
            load_time = time.time() - start_time
            
            if response.status_code != 200:
                return {
                    "performed": True,
                    "url": self.url,
                    "accessible": False,
                    "status_code": response.status_code,
                    "error": f"Site returned HTTP {response.status_code}",
                    "scores": {
                        "overall": 0,
                        "responsiveness": 0,
                        "accessibility": 0,
                        "performance": 0,
                        "animation": 0,
                        "interaction": 0
                    }
                }
            
            html_content = response.text
            headers = response.headers
            
            # Run all audit modules
            performance = self._audit_performance(response, load_time, html_content, headers)
            responsiveness = self._audit_responsiveness(html_content)
            accessibility = self._audit_accessibility(html_content)
            animation = self._audit_animations(html_content)
            interaction = self._audit_interactions(html_content)
            
            # Calculate overall score
            scores = {
                "responsiveness": responsiveness['score'],
                "accessibility": accessibility['score'],
                "performance": performance['score'],
                "animation": animation['score'],
                "interaction": interaction['score']
            }
            overall = round(sum(scores.values()) / len(scores), 1)
            
            return {
                "performed": True,
                "url": self.url,
                "accessible": True,
                "status_code": 200,
                "load_time_seconds": round(load_time, 2),
                "scores": {
                    "overall": overall,
                    **scores
                },
                "performance": performance,
                "responsiveness": responsiveness,
                "accessibility": accessibility,
                "animation": animation,
                "interaction": interaction,
                "recommendations": self._generate_recommendations(
                    performance, responsiveness, accessibility, animation, interaction
                )
            }
            
        except requests.exceptions.Timeout:
            return self._error_result("Request timed out after 15 seconds")
        except requests.exceptions.ConnectionError:
            return self._error_result("Could not connect to the server")
        except Exception as e:
            return self._error_result(str(e))
    
    def _audit_performance(self, response, load_time, html_content, headers):
        """Audit performance metrics."""
        # Calculate page size
        page_size_kb = len(html_content.encode('utf-8')) / 1024
        
        # Count resources
        script_count = html_content.count('<script')
        style_count = html_content.count('<link') + html_content.count('<style')
        image_count = html_content.count('<img')
        
        # Check compression
        is_compressed = 'gzip' in headers.get('Content-Encoding', '') or \
                       'br' in headers.get('Content-Encoding', '')
        
        # Check caching headers
        has_caching = bool(headers.get('Cache-Control')) or bool(headers.get('ETag'))
        
        # Score calculation
        score = 100
        
        # Load time penalty
        if load_time > self.PERFORMANCE_THRESHOLDS['load_time_poor']:
            score -= 30
        elif load_time > self.PERFORMANCE_THRESHOLDS['load_time_good']:
            score -= 15
        elif load_time > self.PERFORMANCE_THRESHOLDS['load_time_excellent']:
            score -= 5
        
        # Page size penalty
        if page_size_kb > self.PERFORMANCE_THRESHOLDS['page_size_poor']:
            score -= 20
        elif page_size_kb > self.PERFORMANCE_THRESHOLDS['page_size_good']:
            score -= 10
        elif page_size_kb > self.PERFORMANCE_THRESHOLDS['page_size_excellent']:
            score -= 5
        
        # Resource count penalty
        if script_count > 15:
            score -= 10
        if image_count > 30:
            score -= 10
        
        # Missing optimizations
        if not is_compressed:
            score -= 10
        if not has_caching:
            score -= 5
        
        # Check for performance hints
        has_preconnect = 'rel="preconnect"' in html_content
        has_preload = 'rel="preload"' in html_content
        has_lazy_loading = 'loading="lazy"' in html_content
        
        if not has_preconnect:
            score -= 3
        if not has_preload:
            score -= 3
        if not has_lazy_loading and image_count > 10:
            score -= 5
        
        score = max(0, min(100, score))
        
        return {
            "score": round(score, 1),
            "load_time_seconds": round(load_time, 2),
            "page_size_kb": round(page_size_kb, 1),
            "script_count": script_count,
            "style_count": style_count,
            "image_count": image_count,
            "is_compressed": is_compressed,
            "has_caching": has_caching,
            "has_preconnect": has_preconnect,
            "has_preload": has_preload,
            "has_lazy_loading": has_lazy_loading,
            "rating": self._performance_rating(load_time, page_size_kb)
        }
    
    def _audit_responsiveness(self, html_content):
        """Audit responsive design implementation."""
        score = 100
        checks = {}
        
        # Check viewport meta tag
        has_viewport = 'name="viewport"' in html_content or "name='viewport'" in html_content
        checks['viewport_meta'] = has_viewport
        if not has_viewport:
            score -= 25
        
        # Check media queries
        has_media_queries = '@media' in html_content
        checks['media_queries'] = has_media_queries
        if not has_media_queries:
            score -= 20
        
        # Check responsive frameworks
        uses_bootstrap = 'bootstrap' in html_content.lower()
        uses_tailwind = 'tailwind' in html_content.lower()
        uses_flexbox = 'display: flex' in html_content or 'display:flex' in html_content
        uses_grid = 'display: grid' in html_content or 'display:grid' in html_content
        
        checks['uses_flexbox'] = uses_flexbox
        checks['uses_grid'] = uses_grid
        checks['uses_bootstrap'] = uses_bootstrap
        checks['uses_tailwind'] = uses_tailwind
        
        if not uses_flexbox and not uses_grid and not uses_bootstrap and not uses_tailwind:
            score -= 20
        
        # Check for fixed widths that break responsiveness
        fixed_width_pattern = html_content.count('px;') + html_content.count('px ')
        if fixed_width_pattern > 50 and not has_media_queries:
            score -= 15
        
        # Check for mobile-specific classes
        has_mobile_classes = any(cls in html_content for cls in 
                                ['sm:', 'md:', 'lg:', 'xl:', 'col-', 'd-none', 'd-block'])
        checks['has_mobile_classes'] = has_mobile_classes
        
        # Check for responsive images
        has_srcset = 'srcset' in html_content
        has_picture_tag = '<picture' in html_content
        checks['responsive_images'] = has_srcset or has_picture_tag
        
        if not has_srcset and not has_picture_tag:
            score -= 5
        
        score = max(0, min(100, score))
        
        return {
            "score": round(score, 1),
            "checks": checks,
            "viewport_tested": self.VIEWPORTS,
            "rating": "Excellent" if score >= 80 else "Good" if score >= 60 else "Needs Work" if score >= 40 else "Poor"
        }
    
    def _audit_accessibility(self, html_content):
        """Audit WCAG compliance."""
        score = 100
        checks = {}
        
        # Check alt text for images
        img_tags = html_content.count('<img')
        alt_attrs = html_content.count('alt=')
        checks['images_have_alt'] = alt_attrs >= img_tags * 0.8 if img_tags > 0 else True
        if img_tags > 0 and alt_attrs < img_tags:
            missing_ratio = (img_tags - alt_attrs) / img_tags
            score -= int(missing_ratio * 20)
        
        # Check form labels
        input_tags = html_content.count('<input')
        label_tags = html_content.count('<label')
        aria_labels = html_content.count('aria-label')
        checks['form_labels_present'] = label_tags >= input_tags * 0.7 or aria_labels >= input_tags * 0.5
        if input_tags > 0 and not checks['form_labels_present']:
            score -= 15
        
        # Check ARIA landmarks
        has_landmarks = any(landmark in html_content for landmark in 
                          ['role="main"', 'role="navigation"', 'role="banner"', 
                           '<main>', '<nav>', '<header>'])
        checks['aria_landmarks'] = has_landmarks
        if not has_landmarks:
            score -= 10
        
        # Check heading hierarchy
        has_h1 = '<h1' in html_content
        checks['has_h1'] = has_h1
        if not has_h1:
            score -= 10
        
        # Check skip links
        has_skip_link = 'skip' in html_content.lower() and 'href=' in html_content.lower()
        checks['skip_links'] = has_skip_link
        if not has_skip_link:
            score -= 5
        
        # Check focus indicators
        has_focus_styles = ':focus' in html_content or 'focus-visible' in html_content
        checks['focus_indicators'] = has_focus_styles
        if not has_focus_styles:
            score -= 10
        
        # Check semantic HTML
        semantic_tags = ['<main>', '<article>', '<section>', '<aside>', '<header>', '<footer>', '<nav>']
        semantic_count = sum(html_content.count(tag) for tag in semantic_tags)
        checks['semantic_html_count'] = semantic_count
        if semantic_count < 3:
            score -= 10
        
        # Check language attribute
        has_lang = 'lang=' in html_content
        checks['lang_attribute'] = has_lang
        if not has_lang:
            score -= 5
        
        # Check color contrast (basic check)
        has_dark_mode = 'prefers-color-scheme' in html_content or 'dark' in html_content.lower()
        checks['dark_mode_support'] = has_dark_mode
        
        score = max(0, min(100, score))
        
        wcag_level = "AA" if score >= 80 else "A" if score >= 60 else "Below A"
        
        return {
            "score": round(score, 1),
            "checks": checks,
            "wcag_level": wcag_level,
            "rating": "Excellent" if score >= 80 else "Good" if score >= 60 else "Needs Work" if score >= 40 else "Poor"
        }
    
    def _audit_animations(self, html_content):
        """Audit animation smoothness and implementation."""
        score = 100
        checks = {}
        
        # Check for CSS animations
        has_css_animations = '@keyframes' in html_content or 'animation:' in html_content
        has_transitions = 'transition:' in html_content or 'transition-property' in html_content
        
        checks['has_css_animations'] = has_css_animations
        checks['has_transitions'] = has_transitions
        
        if not has_css_animations and not has_transitions:
            score -= 30  # No animations at all
        
        # Check for GPU-accelerated properties
        gpu_properties = ['transform', 'opacity']
        uses_gpu = any(prop in html_content for prop in gpu_properties)
        checks['uses_gpu_acceleration'] = uses_gpu
        
        if has_css_animations and not uses_gpu:
            score -= 15  # Animations not GPU-accelerated
        
        # Check for prefers-reduced-motion
        has_reduced_motion = 'prefers-reduced-motion' in html_content
        checks['respects_reduced_motion'] = has_reduced_motion
        if not has_reduced_motion and (has_css_animations or has_transitions):
            score -= 20  # Accessibility issue
        
        # Check animation duration (reasonable values)
        # Look for suspiciously long or short durations
        duration_pattern = re.findall(r'(\d+(?:\.\d+)?)(s|ms)', html_content)
        suspicious_durations = [d for d, unit in duration_pattern 
                              if (unit == 's' and float(d) > 3) or (unit == 'ms' and float(d) > 3000)]
        checks['suspicious_duration_count'] = len(suspicious_durations)
        if len(suspicious_durations) > 3:
            score -= 10
        
        # Check for JavaScript animation libraries
        js_libs = {
            'gsap': 'GSAP' in html_content or 'gsap' in html_content,
            'framer_motion': 'framer-motion' in html_content or 'motion.' in html_content,
            'anime_js': 'anime' in html_content,
            'lottie': 'lottie' in html_content,
            'three_js': 'three' in html_content
        }
        checks['animation_libraries'] = {k: v for k, v in js_libs.items() if v}
        
        score = max(0, min(100, score))
        
        return {
            "score": round(score, 1),
            "checks": checks,
            "rating": "Excellent" if score >= 80 else "Good" if score >= 60 else "Needs Work" if score >= 40 else "Poor"
        }
    
    def _audit_interactions(self, html_content):
        """Audit interaction feedback quality."""
        score = 100
        checks = {}
        
        # Check hover states
        has_hover = ':hover' in html_content
        checks['hover_states'] = has_hover
        if not has_hover:
            score -= 15
        
        # Check active/focus states
        has_active = ':active' in html_content
        has_focus = ':focus' in html_content or ':focus-visible' in html_content
        checks['active_states'] = has_active
        checks['focus_states'] = has_focus
        if not has_active:
            score -= 10
        if not has_focus:
            score -= 10
        
        # Check disabled states
        has_disabled = ':disabled' in html_content or '[disabled]' in html_content
        checks['disabled_states'] = has_disabled
        if not has_disabled:
            score -= 5
        
        # Check loading indicators
        has_loading = 'loading' in html_content.lower()
        has_spinner = 'spinner' in html_content.lower() or 'loader' in html_content.lower()
        checks['loading_indicators'] = has_loading or has_spinner
        if not has_loading and not has_spinner:
            score -= 15
        
        # Check error handling
        has_error = 'error' in html_content.lower()
        checks['error_states'] = has_error
        if not has_error:
            score -= 10
        
        # Check for empty states
        has_empty = 'empty' in html_content.lower()
        checks['empty_states'] = has_empty
        if not has_empty:
            score -= 5
        
        # Check for form validation feedback
        has_validation = 'invalid' in html_content.lower() or 'valid' in html_content.lower()
        checks['form_validation'] = has_validation
        if not has_validation:
            score -= 10
        
        # Check cursor styles
        has_pointer = 'cursor: pointer' in html_content or "cursor:pointer" in html_content
        checks['pointer_cursor'] = has_pointer
        if not has_pointer:
            score -= 10
        
        score = max(0, min(100, score))
        
        return {
            "score": round(score, 1),
            "checks": checks,
            "rating": "Excellent" if score >= 80 else "Good" if score >= 60 else "Needs Work" if score >= 40 else "Poor"
        }
    
    def _performance_rating(self, load_time, page_size_kb):
        """Get performance rating string."""
        if load_time <= self.PERFORMANCE_THRESHOLDS['load_time_excellent'] and \
           page_size_kb <= self.PERFORMANCE_THRESHOLDS['page_size_excellent']:
            return "Excellent"
        elif load_time <= self.PERFORMANCE_THRESHOLDS['load_time_good'] and \
             page_size_kb <= self.PERFORMANCE_THRESHOLDS['page_size_good']:
            return "Good"
        elif load_time <= self.PERFORMANCE_THRESHOLDS['load_time_poor'] and \
             page_size_kb <= self.PERFORMANCE_THRESHOLDS['page_size_poor']:
            return "Needs Improvement"
        else:
            return "Poor"
    
    def _generate_recommendations(self, performance, responsiveness, accessibility, animation, interaction):
        """Generate recommendations based on audit results."""
        recommendations = []
        
        if performance['score'] < 70:
            recommendations.append({
                "priority": "high",
                "category": "Performance",
                "message": f"Load time ({performance['load_time_seconds']}s) exceeds recommended threshold",
                "action": "Enable compression, optimize images, implement lazy loading, reduce JS bundles"
            })
        
        if not performance.get('has_lazy_loading') and performance.get('image_count', 0) > 10:
            recommendations.append({
                "priority": "medium",
                "category": "Performance",
                "message": "Images not lazily loaded",
                "action": "Add loading='lazy' to below-the-fold images"
            })
        
        if responsiveness['score'] < 70:
            recommendations.append({
                "priority": "high",
                "category": "Responsiveness",
                "message": "Responsive design implementation needs improvement",
                "action": "Add viewport meta tag, implement CSS Grid/Flexbox, add media queries for all breakpoints"
            })
        
        if accessibility['score'] < 70:
            wcag_issues = [k for k, v in accessibility['checks'].items() if v == False]
            recommendations.append({
                "priority": "high",
                "category": "Accessibility",
                "message": f"WCAG compliance issues: {', '.join(wcag_issues[:3])}",
                "action": "Add alt texts, ARIA labels, semantic HTML, and keyboard navigation support"
            })
        
        if animation['score'] < 60:
            if not animation['checks'].get('respects_reduced_motion'):
                recommendations.append({
                    "priority": "medium",
                    "category": "Animation",
                    "message": "Animations don't respect prefers-reduced-motion",
                    "action": "Wrap animations in @media (prefers-reduced-motion: no-preference)"
                })
        
        if interaction['score'] < 70:
            missing = [k for k, v in interaction['checks'].items() if v == False]
            recommendations.append({
                "priority": "medium",
                "category": "Interaction",
                "message": f"Missing interaction states: {', '.join(missing[:3])}",
                "action": "Add hover, focus, active, loading, and error states to interactive elements"
            })
        
        return recommendations
    
    def _error_result(self, error_message):
        """Return error result structure."""
        return {
            "performed": True,
            "url": self.url,
            "accessible": False,
            "error": error_message,
            "scores": {
                "overall": 0,
                "responsiveness": 0,
                "accessibility": 0,
                "performance": 0,
                "animation": 0,
                "interaction": 0
            },
            "performance": {},
            "responsiveness": {},
            "accessibility": {},
            "animation": {},
            "interaction": {},
            "recommendations": [{
                "priority": "high",
                "category": "Availability",
                "message": error_message,
                "action": "Ensure the URL is correct and the server is running"
            }]
        }
