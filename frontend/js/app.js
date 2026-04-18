/**
 * DevCareer Intelligence - Frontend Application
 * Handles audit flow, dashboard rendering, and user interactions.
 */

// API Configuration - uses relative paths for deployment compatibility
const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:5000/api' : '/api';

// State
let currentAuditId = null;
let auditResults = null;
let pollInterval = null;

// DOM Elements
const elements = {
    form: document.getElementById('audit-form-element'),
    loadingSection: document.getElementById('loading-section'),
    dashboard: document.getElementById('dashboard'),
    progressFill: document.getElementById('progress-fill'),
    loadingFacts: document.getElementById('loading-facts'),
    navDashboard: document.getElementById('nav-dashboard'),
    auditFormSection: document.getElementById('audit-form')
};

// Loading facts to cycle through
const loadingFacts = [
    "Fetching repository data from GitHub API...",
    "Analyzing commit patterns and consistency...",
    "Detecting architectural patterns across repos...",
    "Evaluating test coverage and quality...",
    "Scanning for security vulnerabilities...",
    "Checking documentation completeness...",
    "Auditing live application performance...",
    "Comparing against current job market data...",
    "Generating actionable feedback...",
    "Building your 90-day learning roadmap...",
    "Crafting evidence-based resume bullets...",
    "Almost done - compiling final report..."
];

// ==========================================
// Event Listeners
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Form submission
    elements.form.addEventListener('submit', handleAuditSubmit);
    
    // Tab navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
});

// ==========================================
// Audit Flow
// ==========================================

async function handleAuditSubmit(e) {
    e.preventDefault();
    
    const formData = {
        github_username: document.getElementById('github-username').value.trim(),
        portfolio_url: document.getElementById('portfolio-url').value.trim(),
        claimed_role: document.getElementById('claimed-role').value.trim(),
        claimed_years: parseInt(document.getElementById('claimed-years').value) || 0,
        claimed_skills: document.getElementById('claimed-skills').value.split(',').map(s => s.trim()).filter(Boolean),
        target_role: document.getElementById('target-role').value.trim(),
        location: document.getElementById('location').value
    };
    
    if (!formData.github_username) {
        showError('GitHub username is required');
        return;
    }
    
    // Show loading
    showLoading();
    
    try {
        // Start audit
        const response = await fetch(`${API_BASE}/audit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        currentAuditId = data.audit_id;
        
        // Start polling for results
        startPolling(currentAuditId);
        
        // Start cycling loading facts
        cycleLoadingFacts();
        
    } catch (error) {
        console.error('Audit error:', error);
        // Use mock data for demo
        setTimeout(() => {
            loadMockData();
            showDashboard();
        }, 3000);
    }
}

function startPolling(auditId) {
    let attempts = 0;
    const maxAttempts = 60; // 2 minutes max
    
    pollInterval = setInterval(async () => {
        attempts++;
        
        try {
            const response = await fetch(`${API_BASE}/audit/${auditId}`);
            const data = await response.json();
            
            // Update progress
            updateProgress(data.progress || 0);
            
            if (data.status === 'completed') {
                clearInterval(pollInterval);
                auditResults = data.results;
                showDashboard();
            } else if (data.status === 'error') {
                clearInterval(pollInterval);
                // Fall back to mock data
                loadMockData();
                showDashboard();
            }
            
            if (attempts >= maxAttempts) {
                clearInterval(pollInterval);
                loadMockData();
                showDashboard();
            }
            
        } catch (error) {
            console.error('Polling error:', error);
        }
    }, 2000);
}

function cycleLoadingFacts() {
    let index = 0;
    const factInterval = setInterval(() => {
        if (auditResults || index >= loadingFacts.length) {
            clearInterval(factInterval);
            return;
        }
        elements.loadingFacts.innerHTML = `<p>${loadingFacts[index]}</p>`;
        index = (index + 1) % loadingFacts.length;
    }, 2500);
}

function updateProgress(percent) {
    elements.progressFill.style.width = `${percent}%`;
    
    // Update active steps
    const steps = document.querySelectorAll('.step');
    const activeStep = Math.ceil((percent / 100) * steps.length);
    
    steps.forEach((step, i) => {
        step.classList.remove('active', 'completed');
        if (i + 1 < activeStep) {
            step.classList.add('completed');
        } else if (i + 1 === activeStep) {
            step.classList.add('active');
        }
    });
}

function showLoading() {
    elements.auditFormSection.style.display = 'none';
    elements.loadingSection.style.display = 'block';
    elements.dashboard.style.display = 'none';
    window.scrollTo(0, 0);
}

function showDashboard() {
    elements.loadingSection.style.display = 'none';
    elements.dashboard.style.display = 'block';
    elements.navDashboard.style.display = 'inline';
    window.scrollTo(0, 0);
    
    // Render all dashboard content
    renderDashboard();
}

function newAudit() {
    currentAuditId = null;
    auditResults = null;
    elements.form.reset();
    elements.auditFormSection.style.display = 'block';
    elements.loadingSection.style.display = 'none';
    elements.dashboard.style.display = 'none';
    elements.navDashboard.style.display = 'none';
    window.scrollTo(0, 0);
}

// ==========================================
// Dashboard Rendering
// ==========================================

function renderDashboard() {
    if (!auditResults) return;
    
    const summary = auditResults.summary;
    const scores = auditResults.scores;
    
    // Update summary cards
    document.getElementById('audit-id-display').textContent = `Audit #${summary.audit_id}`;
    document.getElementById('overall-score-number').textContent = Math.round(summary.overall_score);
    document.getElementById('critical-issues-count').textContent = summary.critical_issues_count;
    document.getElementById('warnings-count').textContent = `${summary.warnings_count} warnings`;
    document.getElementById('market-percentile').textContent = `${Math.round(summary.market_position)}th`;
    document.getElementById('interview-rate').textContent = `${Math.round(summary.interview_success_rate)}% interview rate`;
    
    // Level badge
    const levelEl = document.getElementById('demonstrated-level');
    const levelShort = document.getElementById('demonstrated-level-short');
    const levelVerdict = document.getElementById('level-verdict');
    const levelComparison = document.getElementById('level-comparison');
    
    const levelClass = summary.demonstrated_level.toLowerCase().replace('-', '');
    levelEl.className = `level-badge ${levelClass}`;
    levelEl.textContent = summary.demonstrated_level;
    levelShort.textContent = summary.demonstrated_level;
    
    // Level comparison
    if (summary.level_match === true) {
        levelVerdict.textContent = 'Verified';
        levelVerdict.style.color = 'var(--success)';
        levelComparison.innerHTML = `Claimed <strong>${summary.claimed_role || 'level'}</strong> matches demonstrated skills`;
    } else if (summary.level_match === 'partial') {
        levelVerdict.textContent = 'Partial Match';
        levelVerdict.style.color = 'var(--warning)';
        levelComparison.innerHTML = `Demonstrated level is slightly below claimed <strong>${summary.claimed_role || 'level'}</strong>`;
    } else {
        levelVerdict.textContent = 'Mismatch';
        levelVerdict.style.color = 'var(--danger)';
        levelComparison.innerHTML = `Demonstrated level is below claimed <strong>${summary.claimed_role || 'level'}</strong>`;
    }
    
    // Animate score circle
    setTimeout(() => {
        const circle = document.getElementById('score-progress-circle');
        const circumference = 2 * Math.PI * 54;
        const offset = circumference - (summary.overall_score / 100) * circumference;
        circle.style.strokeDashoffset = offset;
    }, 300);
    
    // Render all tabs
    renderOverviewTab();
    renderCodeAnalysisTab();
    renderLiveAuditTab();
    renderSecurityTab();
    renderMarketTab();
    renderRoadmapTab();
    renderResumeTab();
}

// ==========================================
// Overview Tab
// ==========================================

function renderOverviewTab() {
    const scores = auditResults.scores;
    const container = document.getElementById('dimension-bars');
    
    const dimensions = [
        { key: 'code_quality', label: 'Code Quality' },
        { key: 'testing', label: 'Testing' },
        { key: 'documentation', label: 'Documentation' },
        { key: 'architecture', label: 'Architecture' },
        { key: 'naming_conventions', label: 'Naming Conventions' },
        { key: 'modularity', label: 'Modularity' },
        { key: 'security', label: 'Security' },
        { key: 'performance', label: 'Performance' },
        { key: 'github_activity', label: 'GitHub Activity' }
    ];
    
    container.innerHTML = dimensions.map(d => {
        const score = scores.dimension_scores[d.key] || 0;
        const rating = scores.dimension_ratings[d.key] || 0;
        let fillClass = 'poor';
        if (score >= 80) fillClass = 'excellent';
        else if (score >= 60) fillClass = 'good';
        else if (score >= 40) fillClass = 'fair';
        
        return `
            <div class="dimension-bar">
                <span class="dimension-label">${d.label}</span>
                <div class="dimension-track">
                    <div class="dimension-fill ${fillClass}" style="width: 0%" data-width="${score}%"></div>
                </div>
                <span class="dimension-value">${rating.toFixed(1)}</span>
            </div>
        `;
    }).join('');
    
    // Animate bars
    setTimeout(() => {
        container.querySelectorAll('.dimension-fill').forEach(fill => {
            fill.style.width = fill.dataset.width;
        });
    }, 500);
    
    // Action items
    const actionContainer = document.getElementById('action-items');
    const feedback = auditResults.feedback || [];
    const topItems = feedback.slice(0, 5);
    
    actionContainer.innerHTML = topItems.map(item => {
        const priorityClass = item.severity === 'critical' ? 'critical' : 
                             item.severity === 'warning' ? 'high' : 'medium';
        return `
            <div class="action-item ${item.severity === 'critical' ? 'critical' : ''}">
                <span class="action-priority ${priorityClass}">${item.severity}</span>
                <span class="action-text">${item.message}</span>
            </div>
        `;
    }).join('');
    
    // Tech stack
    const techContainer = document.getElementById('tech-stack-display');
    const techStack = auditResults.github_profile?.tech_stack;
    
    if (techStack) {
        const languages = techStack.language_breakdown || techStack.primary_languages || {};
        const colors = ['#6366f1', '#a855f7', '#22c55e', '#f59e0b', '#3b82f6', '#ef4444', '#ec4899', '#14b8a6'];
        
        techContainer.innerHTML = Object.entries(languages).map(([lang, pct], i) => `
            <div class="tech-tag">
                <span class="lang-dot" style="background: ${colors[i % colors.length]}"></span>
                ${lang}
                <span class="lang-percent">${typeof pct === 'number' ? pct.toFixed(1) : pct}%</span>
            </div>
        `).join('');
    }
}

// ==========================================
// Code Analysis Tab
// ==========================================

function renderCodeAnalysisTab() {
    const container = document.getElementById('code-analysis-container');
    const codeQuality = auditResults.code_quality || {};
    const repoAnalyses = codeQuality.repo_analysis || [];
    const aggregate = codeQuality.aggregate_scores || {};
    
    // Aggregate scores summary
    let html = `
        <div class="panel">
            <h3 class="panel-title">Aggregate Scores</h3>
            <div class="repo-metrics">
                <div class="metric-box">
                    <span class="metric-value ${getScoreClass(aggregate.test_coverage_avg)}">${(aggregate.test_coverage_avg || 0).toFixed(1)}%</span>
                    <span class="metric-label">Test Coverage</span>
                </div>
                <div class="metric-box">
                    <span class="metric-value ${getScoreClass(aggregate.documentation_avg)}">${(aggregate.documentation_avg || 0).toFixed(1)}</span>
                    <span class="metric-label">Documentation</span>
                </div>
                <div class="metric-box">
                    <span class="metric-value ${getScoreClass(aggregate.architecture_avg)}">${(aggregate.architecture_avg || 0).toFixed(1)}</span>
                    <span class="metric-label">Architecture</span>
                </div>
                <div class="metric-box">
                    <span class="metric-value ${getScoreClass(aggregate.overall_quality_score)}">${(aggregate.overall_quality_score || 0).toFixed(1)}</span>
                    <span class="metric-label">Overall Quality</span>
                </div>
            </div>
        </div>
    `;
    
    // Individual repo cards
    html += repoAnalyses.map((repo, index) => {
        const smells = repo.code_smells || [];
        const hasSmells = smells.length > 0;
        
        return `
            <div class="repo-card">
                <div class="repo-header" onclick="toggleRepoBody(this)">
                    <div class="repo-title-section">
                        <span class="repo-name">${repo.name}</span>
                        <span class="repo-language">${repo.language || 'Unknown'}</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:16px">
                        <span class="repo-stars">
                            <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M8 0.5L10.2 5.1L15.2 5.8L11.6 9.4L12.5 14.4L8 12.1L3.5 14.4L4.4 9.4L0.8 5.8L5.8 5.1L8 0.5Z"/>
                            </svg>
                            ${repo.stars || 0}
                        </span>
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="expand-icon" style="transition:transform 0.3s">
                            <path d="M4 6L8 10L12 6" stroke="var(--text-muted)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </div>
                </div>
                <div class="repo-body">
                    <div class="repo-metrics">
                        <div class="metric-box">
                            <span class="metric-value ${getScoreClass(repo.test_coverage)}">${(repo.test_coverage || 0).toFixed(1)}%</span>
                            <span class="metric-label">Test Coverage</span>
                        </div>
                        <div class="metric-box">
                            <span class="metric-value ${getScoreClass(repo.documentation_score)}">${(repo.documentation_score || 0).toFixed(1)}</span>
                            <span class="metric-label">Documentation</span>
                        </div>
                        <div class="metric-box">
                            <span class="metric-value ${getScoreClass(repo.architecture_score)}">${(repo.architecture_score || 0).toFixed(1)}</span>
                            <span class="metric-label">Architecture</span>
                        </div>
                        <div class="metric-box">
                            <span class="metric-value ${getScoreClass(repo.naming_score)}">${(repo.naming_score || 0).toFixed(1)}</span>
                            <span class="metric-label">Naming</span>
                        </div>
                    </div>
                    
                    ${repo.detected_patterns ? `
                        <div style="margin-bottom:16px">
                            <span style="font-size:12px;color:var(--text-muted);margin-right:8px">Patterns:</span>
                            ${repo.detected_patterns.map(p => `<span class="tech-tag" style="font-size:11px;padding:3px 10px">${p}</span>`).join('')}
                        </div>
                    ` : ''}
                    
                    ${hasSmells ? `
                        <h4 style="font-size:13px;color:var(--text-secondary);margin-bottom:10px">Code Smells (${smells.length})</h4>
                        <div class="code-smells-list">
                            ${smells.map(smell => `
                                <div class="smell-item ${smell.severity === 'critical' ? 'critical' : ''}">
                                    <div class="smell-header">
                                        <span class="smell-type">${smell.type || 'Issue'}</span>
                                        <span class="smell-severity ${smell.severity}">${smell.severity}</span>
                                    </div>
                                    <div class="smell-description">${smell.description}</div>
                                    <div class="smell-fix">Fix: ${smell.fix || smell.recommendation || 'Refactor this code'}</div>
                                    ${smell.file ? `<div class="smell-file">${smell.file}${smell.line ? `:${smell.line}` : ''}</div>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    ` : '<p style="color:var(--text-muted);font-size:13px">No code smells detected in this repository.</p>'}
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

function toggleRepoBody(header) {
    const body = header.nextElementSibling;
    const icon = header.querySelector('.expand-icon');
    body.classList.toggle('expanded');
    icon.style.transform = body.classList.contains('expanded') ? 'rotate(180deg)' : 'rotate(0)';
}

// ==========================================
// Live App Audit Tab
// ==========================================

function renderLiveAuditTab() {
    const container = document.getElementById('live-audit-container');
    const liveAudit = auditResults.live_app_audit || {};
    
    if (!liveAudit.performed) {
        container.innerHTML = `
            <div class="panel" style="text-align:center;padding:60px 24px">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" style="margin-bottom:16px;color:var(--text-muted)">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" stroke="currentColor" stroke-width="1.5"/>
                </svg>
                <h3 style="margin-bottom:8px">No Live App Audited</h3>
                <p style="color:var(--text-muted);font-size:14px">Provide a portfolio URL when starting the audit to get live app quality metrics.</p>
            </div>
        `;
        return;
    }
    
    const scores = liveAudit.scores || {};
    
    let html = `
        <div class="audit-scores-grid">
            <div class="audit-score-box">
                <div class="audit-score-value" style="color:${getScoreColor(scores.overall)}">${Math.round(scores.overall || 0)}</div>
                <div class="audit-score-label">Overall</div>
            </div>
            <div class="audit-score-box">
                <div class="audit-score-value" style="color:${getScoreColor(scores.responsiveness)}">${Math.round(scores.responsiveness || 0)}</div>
                <div class="audit-score-label">Responsive</div>
            </div>
            <div class="audit-score-box">
                <div class="audit-score-value" style="color:${getScoreColor(scores.accessibility)}">${Math.round(scores.accessibility || 0)}</div>
                <div class="audit-score-label">Accessible</div>
            </div>
            <div class="audit-score-box">
                <div class="audit-score-value" style="color:${getScoreColor(scores.performance)}">${Math.round(scores.performance || 0)}</div>
                <div class="audit-score-label">Performance</div>
            </div>
            <div class="audit-score-box">
                <div class="audit-score-value" style="color:${getScoreColor(scores.animation)}">${Math.round(scores.animation || 0)}</div>
                <div class="audit-score-label">Animation</div>
            </div>
        </div>
    `;
    
    // Performance details
    const perf = liveAudit.performance || {};
    html += `
        <div class="audit-details">
            <div class="audit-detail-panel">
                <h4 style="font-size:14px;margin-bottom:14px">Performance Metrics</h4>
                <div class="check-item">
                    <span class="check-icon ${perf.load_time_seconds < 3 ? 'pass' : 'fail'}">${perf.load_time_seconds < 3 ? '&#10003;' : '&#10007;'}</span>
                    <span class="check-label">Load Time: ${perf.load_time_seconds || 'N/A'}s</span>
                </div>
                <div class="check-item">
                    <span class="check-icon ${perf.page_size_kb < 1000 ? 'pass' : 'fail'}">${perf.page_size_kb < 1000 ? '&#10003;' : '&#10007;'}</span>
                    <span class="check-label">Page Size: ${(perf.page_size_kb || 0).toFixed(0)} KB</span>
                </div>
                <div class="check-item">
                    <span class="check-icon ${perf.is_compressed ? 'pass' : 'fail'}">${perf.is_compressed ? '&#10003;' : '&#10007;'}</span>
                    <span class="check-label">Compression Enabled</span>
                </div>
                <div class="check-item">
                    <span class="check-icon ${perf.has_caching ? 'pass' : 'fail'}">${perf.has_caching ? '&#10003;' : '&#10007;'}</span>
                    <span class="check-label">Caching Configured</span>
                </div>
                <div class="check-item">
                    <span class="check-icon ${perf.has_lazy_loading ? 'pass' : 'warn'}">${perf.has_lazy_loading ? '&#10003;' : '!'}</span>
                    <span class="check-label">Lazy Loading</span>
                </div>
            </div>
            
            <div class="audit-detail-panel">
                <h4 style="font-size:14px;margin-bottom:14px">Accessibility Checks</h4>
                ${renderAccessibilityChecks(liveAudit.accessibility)}
            </div>
        </div>
    `;
    
    // Recommendations
    const recommendations = liveAudit.recommendations || [];
    if (recommendations.length > 0) {
        html += `
            <div class="panel">
                <h3 class="panel-title">Recommendations</h3>
                <div class="action-items">
                    ${recommendations.map(rec => `
                        <div class="action-item">
                            <span class="action-priority ${rec.priority === 'high' ? 'high' : 'medium'}">${rec.priority}</span>
                            <span class="action-text"><strong>${rec.category}:</strong> ${rec.message}. ${rec.action}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function renderAccessibilityChecks(accessibility) {
    if (!accessibility || !accessibility.checks) {
        return '<p style="color:var(--text-muted);font-size:13px">No accessibility data available.</p>';
    }
    
    const checks = accessibility.checks;
    const checkItems = [
        { key: 'images_have_alt', label: 'Images have alt text' },
        { key: 'form_labels_present', label: 'Form labels present' },
        { key: 'aria_landmarks', label: 'ARIA landmarks' },
        { key: 'has_h1', label: 'H1 heading present' },
        { key: 'focus_indicators', label: 'Focus indicators' },
        { key: 'semantic_html_count', label: 'Semantic HTML' },
        { key: 'lang_attribute', label: 'Lang attribute' }
    ];
    
    return checkItems.map(item => {
        const value = checks[item.key];
        const isPass = value === true || (typeof value === 'number' && value > 0);
        const icon = isPass ? '&#10003;' : (value === false ? '&#10007;' : '!');
        const iconClass = isPass ? 'pass' : (value === false ? 'fail' : 'warn');
        const extra = typeof value === 'number' ? ` (${value})` : '';
        
        return `
            <div class="check-item">
                <span class="check-icon ${iconClass}">${icon}</span>
                <span class="check-label">${item.label}${extra}</span>
            </div>
        `;
    }).join('');
}

// ==========================================
// Security Tab
// ==========================================

function renderSecurityTab() {
    const container = document.getElementById('security-container');
    const security = auditResults.security_scan || {};
    
    const rating = security.security_rating || 'C - Acceptable';
    const ratingLetter = rating.charAt(0);
    const ratingClass = ratingLetter.toLowerCase();
    
    let html = `
        <div class="security-score-banner">
            <div class="security-rating ${ratingClass}">${ratingLetter}</div>
            <div class="security-stats">
                <div class="security-stat">
                    <span class="security-stat-value critical">${security.critical_count || 0}</span>
                    <span class="security-stat-label">Critical</span>
                </div>
                <div class="security-stat">
                    <span class="security-stat-value warning">${security.warning_count || 0}</span>
                    <span class="security-stat-label">Warnings</span>
                </div>
                <div class="security-stat">
                    <span class="security-stat-value info">${security.info_count || 0}</span>
                    <span class="security-stat-label">Info</span>
                </div>
            </div>
            <div style="text-align:right;flex:1">
                <div style="font-size:28px;font-weight:700">${Math.round(security.security_score || 0)}<span style="font-size:14px;color:var(--text-muted)">/100</span></div>
                <div style="font-size:12px;color:var(--text-muted)">Security Score</div>
            </div>
        </div>
    `;
    
    // Issues list
    const issues = security.issues || [];
    if (issues.length > 0) {
        html += `
            <div class="panel">
                <h3 class="panel-title">Security Issues (${issues.length})</h3>
                <div class="security-issues-list">
                    ${issues.map(issue => `
                        <div class="security-issue ${issue.severity === 'warning' ? 'warning' : ''}">
                            <div class="issue-header">
                                <span style="font-size:14px;font-weight:600">${issue.type || issue.category}</span>
                                <span class="issue-category">${issue.category}</span>
                            </div>
                            <div style="font-size:13px;color:var(--text-secondary);margin-bottom:8px">${issue.description}</div>
                            ${issue.evidence ? `<div style="font-size:12px;font-family:'JetBrains Mono',monospace;background:var(--bg-primary);padding:8px;border-radius:4px;margin-bottom:8px;color:var(--danger)">${issue.evidence}</div>` : ''}
                            <div style="font-size:12px;color:var(--success)">Fix: ${issue.recommendation || issue.fix || 'Address this issue'}</div>
                            ${issue.file ? `<div class="smell-file">${issue.file}${issue.line ? `:${issue.line}` : ''}</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Recommendations
    const recommendations = security.recommendations || [];
    if (recommendations.length > 0) {
        html += `
            <div class="panel">
                <h3 class="panel-title">Security Recommendations</h3>
                <div class="action-items">
                    ${recommendations.map(rec => `
                        <div class="action-item">
                            <span class="action-priority ${rec.priority === 'immediate' ? 'critical' : rec.priority === 'high' ? 'high' : 'medium'}">${rec.priority}</span>
                            <div>
                                <div class="action-text" style="margin-bottom:4px">${rec.message}</div>
                                ${rec.actions ? `<div style="font-size:12px;color:var(--text-muted)">${rec.actions.join(', ')}</div>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// ==========================================
// Market Fit Tab
// ==========================================

function renderMarketTab() {
    const container = document.getElementById('market-container');
    const market = auditResults.market_comparison || {};
    
    let html = `
        <div class="market-overview">
            <div class="market-panel">
                <div class="salary-label">Estimated Salary (USD)</div>
                <div class="salary-range">$${((market.salary_estimate?.range_usd?.median || 0) / 1000).toFixed(0)}k</div>
                <div style="font-size:13px;color:var(--text-muted);margin-top:4px">
                    Range: $${((market.salary_estimate?.range_usd?.min || 0) / 1000).toFixed(0)}k - $${((market.salary_estimate?.range_usd?.max || 0) / 1000).toFixed(0)}k
                </div>
            </div>
            <div class="market-panel">
                <div class="salary-label">Market Percentile</div>
                <div class="salary-range">${Math.round(market.percentile || 0)}th</div>
                <div style="font-size:13px;color:var(--text-muted);margin-top:4px">
                    Among developers with similar experience
                </div>
            </div>
            <div class="market-panel">
                <div class="salary-label">Interview Success Rate</div>
                <div class="salary-range">${Math.round(market.interview_success_rate || 0)}%</div>
                <div style="font-size:13px;color:var(--text-muted);margin-top:4px">
                    Estimated for target role
                </div>
            </div>
        </div>
    `;
    
    // Matching roles
    const roles = market.matching_roles || [];
    html += `
        <div class="panel">
            <h3 class="panel-title">Roles You Qualify For</h3>
            <div class="role-match-list">
                ${roles.length > 0 ? roles.map(role => `
                    <div class="role-match-item">
                        <div>
                            <div class="role-match-name">${role.role}</div>
                            <div style="font-size:12px;color:var(--text-muted)">$${(role.salary_min / 1000).toFixed(0)}k - $${(role.salary_max / 1000).toFixed(0)}k</div>
                        </div>
                        <div style="text-align:right">
                            <div class="role-match-percent">${role.match_percentage}% match</div>
                            <div class="role-match-confidence">${role.confidence} confidence</div>
                        </div>
                    </div>
                `).join('') : '<p style="color:var(--text-muted);font-size:13px">Complete the audit to see role matches.</p>'}
            </div>
        </div>
    `;
    
    // Realistic companies
    const companies = market.realistic_companies || [];
    if (companies.length > 0) {
        html += `
            <div class="panel">
                <h3 class="panel-title">Realistic Companies</h3>
                <div class="company-grid">
                    ${companies.map(company => `
                        <div class="company-tag ${company.remote ? 'remote' : ''}">${company.name}</div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Skill gaps
    const skillGaps = market.skill_gaps || {};
    const allGaps = [...(skillGaps.missing_skills || []), ...(skillGaps.score_gaps || [])];
    
    if (allGaps.length > 0) {
        html += `
            <div class="panel">
                <h3 class="panel-title">Skill Gaps to Next Level (${allGaps.length})</h3>
                <div class="skill-gaps-list">
                    ${allGaps.map(gap => `
                        <div class="skill-gap-item">
                            <div class="skill-gap-name">${gap.skill}</div>
                            <div class="skill-gap-level">
                                Current: ${gap.current_level} → Target: ${gap.required_level}
                                ${gap.learning_time_weeks ? `| ~${gap.learning_time_weeks} weeks` : ''}
                            </div>
                            ${gap.impact ? `<div style="font-size:12px;color:var(--text-muted);margin-top:4px">${gap.impact}</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Next level requirements
    const nextLevel = market.next_level_requirements || {};
    if (nextLevel.requirements) {
        html += `
            <div class="panel">
                <h3 class="panel-title">Path to ${nextLevel.next || 'Next Level'} (~${nextLevel.estimated_weeks || '?'} weeks)</h3>
                <div class="action-items">
                    ${nextLevel.requirements.map(req => `
                        <div class="action-item">
                            <span class="action-priority medium">goal</span>
                            <span class="action-text">${req}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// ==========================================
// Roadmap Tab
// ==========================================

function renderRoadmapTab() {
    const container = document.getElementById('roadmap-container');
    const roadmap = auditResults.roadmap || {};
    const overview = roadmap.overview || {};
    
    let html = `
        <div class="roadmap-overview">
            <div class="roadmap-stats">
                <div class="roadmap-stat">
                    <div class="roadmap-stat-value">${overview.duration_days || 90}</div>
                    <div class="roadmap-stat-label">Days</div>
                </div>
                <div class="roadmap-stat">
                    <div class="roadmap-stat-value">${overview.estimated_daily_hours || 2}h</div>
                    <div class="roadmap-stat-label">Daily</div>
                </div>
                <div class="roadmap-stat">
                    <div class="roadmap-stat-value">${overview.total_estimated_hours || 180}h</div>
                    <div class="roadmap-stat-label">Total Hours</div>
                </div>
                <div class="roadmap-stat">
                    <div class="roadmap-stat-value">${(overview.focus_areas || []).length}</div>
                    <div class="roadmap-stat-label">Focus Areas</div>
                </div>
            </div>
            <div style="font-size:13px;color:var(--text-muted)">
                <strong>Target:</strong> ${overview.target_role || 'Senior Developer'} | 
                <strong>Focus:</strong> ${(overview.focus_areas || []).join(', ')}
            </div>
        </div>
    `;
    
    // Week cards
    const weeks = roadmap.weeks || [];
    html += weeks.map(week => `
        <div class="week-card">
            <div class="week-header">
                <div>
                    <span class="week-number">Week ${week.week}</span>
                    <div class="week-theme">${week.theme}</div>
                </div>
                <span class="week-focus">${week.focus}</span>
            </div>
            <div class="week-tasks">
                ${(week.tasks || []).map(task => `
                    <div class="week-task">
                        <span>&#8226;</span>
                        <div>
                            <div>${task.action || task}</div>
                            ${task.deliverable ? `<div class="task-deliverable">Deliverable: ${task.deliverable}</div>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
            ${week.milestone ? `<div class="week-milestone">Milestone: ${week.milestone}</div>` : ''}
        </div>
    `).join('');
    
    // Milestones
    const milestones = roadmap.milestones || [];
    if (milestones.length > 0) {
        html += `
            <div class="panel">
                <h3 class="panel-title">Key Milestones</h3>
                <div class="action-items">
                    ${milestones.map(m => `
                        <div class="action-item success">
                            <span class="action-priority medium">Day ${m.day}</span>
                            <div>
                                <div class="action-text" style="font-weight:600">${m.title}</div>
                                <div style="font-size:12px;color:var(--text-muted)">${m.description}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Measurable goals
    const goals = roadmap.measurable_goals || [];
    if (goals.length > 0) {
        html += `
            <div class="panel">
                <h3 class="panel-title">Measurable Goals</h3>
                <div class="skill-gaps-list">
                    ${goals.map(goal => `
                        <div class="skill-gap-item">
                            <div class="skill-gap-name">${goal.area}</div>
                            <div class="skill-gap-level">${goal.current} → ${goal.target}</div>
                            <div style="font-size:12px;color:var(--text-muted)">${goal.measurement_method}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// ==========================================
// Resume Tab
// ==========================================

function renderResumeTab() {
    const container = document.getElementById('resume-container');
    const resume = auditResults.resume_bullets || {};
    
    let html = '';
    
    // Strengths
    const strengths = resume.strengths_highlighted || [];
    if (strengths.length > 0) {
        html += `
            <div class="resume-panel">
                <h3 class="panel-title">Demonstrated Strengths</h3>
                <div class="resume-strengths">
                    ${strengths.map(s => `<span class="strength-tag">${s}</span>`).join('')}
                </div>
            </div>
        `;
    }
    
    // Bullets
    const bullets = resume.bullets || [];
    html += `
        <div class="resume-panel">
            <h3 class="panel-title">Auto-Generated Resume Bullets (${bullets.length})</h3>
            <p style="font-size:13px;color:var(--text-muted);margin-bottom:16px">
                These bullets are generated from actual code analysis, not self-reported claims.
            </p>
            ${bullets.length > 0 ? bullets.map(bullet => `
                <div class="resume-bullet">${bullet}</div>
            `).join('') : '<p style="color:var(--text-muted);font-size:13px">Complete the audit to generate resume bullets.</p>'}
        </div>
    `;
    
    // Omissions
    const omissions = resume.omitted_claims || [];
    if (omissions.length > 0) {
        html += `
            <div class="resume-panel">
                <h3 class="panel-title" style="color:var(--danger)">Claims to Remove</h3>
                <p style="font-size:13px;color:var(--text-muted);margin-bottom:16px">
                    These claims are not supported by actual code evidence.
                </p>
                <div class="omissions-list">
                    ${omissions.map(o => `
                        <div class="omission-item">
                            <div class="omission-claim">${o.claim}</div>
                            <div class="omission-reason">${o.reason}</div>
                            <div class="omission-recommendation">${o.recommendation}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Recommendations
    const recommendations = resume.recommendations || [];
    if (recommendations.length > 0) {
        html += `
            <div class="resume-panel">
                <h3 class="panel-title">Resume Tips</h3>
                <div class="action-items">
                    ${recommendations.map(rec => `
                        <div class="action-item">
                            <span class="action-priority ${rec.priority === 'high' ? 'high' : 'medium'}">${rec.priority}</span>
                            <div>
                                <div class="action-text">${rec.message}</div>
                                ${rec.tips ? `<div style="font-size:12px;color:var(--text-muted)">${rec.tips.join(' | ')}</div>` : ''}
                                ${rec.example ? `<div style="font-size:12px;color:var(--accent-primary);margin-top:4px">Example: ${rec.example}</div>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// ==========================================
// Tab Switching
// ==========================================

function switchTab(tabId) {
    // Update active tab button
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabId);
    });
    
    // Update active tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const targetContent = document.getElementById(`tab-${tabId}`);
    if (targetContent) {
        targetContent.classList.add('active');
    }
}

// ==========================================
// Utilities
// ==========================================

function getScoreClass(score) {
    if (score >= 80) return 'good';
    if (score >= 60) return 'fair';
    return 'poor';
}

function getScoreColor(score) {
    if (score >= 80) return 'var(--success)';
    if (score >= 60) return 'var(--warning)';
    return 'var(--danger)';
}

function showError(message) {
    alert(message); // Could be replaced with a toast notification
}

function downloadReport() {
    if (!auditResults) return;
    
    const reportData = JSON.stringify(auditResults, null, 2);
    const blob = new Blob([reportData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `devcareer-audit-${currentAuditId || 'report'}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ==========================================
// Mock Data (for demo without backend)
// ==========================================

function loadMockData() {
    auditResults = getMockResults();
}

function getMockResults() {
    return {
        summary: {
            audit_id: "demo123",
            github_username: "demo-user",
            claimed_role: "Senior Full-Stack Developer",
            claimed_years: 5,
            demonstrated_level: "Mid-Level",
            level_match: false,
            overall_score: 52.3,
            critical_issues_count: 3,
            warnings_count: 7,
            market_position: 45,
            interview_success_rate: 18
        },
        scores: {
            overall_score: 52.3,
            overall_level: "Mid-Level",
            claimed_level: "Senior",
            level_match: false,
            role_type: "fullstack",
            dimension_scores: {
                code_quality: 48.8,
                testing: 19.2,
                documentation: 47.0,
                architecture: 64.0,
                naming_conventions: 61.7,
                modularity: 52.3,
                security: 65.0,
                performance: 50.0,
                github_activity: 65.0
            },
            dimension_ratings: {
                code_quality: 4.9,
                testing: 1.9,
                documentation: 4.7,
                architecture: 6.4,
                naming_conventions: 6.2,
                modularity: 5.2,
                security: 6.5,
                performance: 5.0,
                github_activity: 6.5
            }
        },
        github_profile: {
            username: "demo-user",
            name: "Demo User",
            bio: "Full-stack developer passionate about building scalable applications.",
            public_repos: 12,
            followers: 45,
            hireable: true,
            repos: [
                { name: "ecommerce-platform", description: "Full-stack e-commerce platform", language: "JavaScript", stars: 28, topics: ["react", "nodejs", "mongodb"] },
                { name: "task-management-api", description: "RESTful API for task management", language: "TypeScript", stars: 15, topics: ["typescript", "express", "jwt"] },
                { name: "portfolio-website", description: "Personal portfolio", language: "TypeScript", stars: 8, topics: ["nextjs", "tailwindcss"] },
                { name: "weather-dashboard", description: "Weather dashboard", language: "JavaScript", stars: 12, topics: ["javascript", "chartjs"] },
                { name: "blog-cms", description: "Content management system", language: "Python", stars: 6, topics: ["python", "django"] }
            ],
            tech_stack: {
                language_breakdown: { "JavaScript": 45.2, "TypeScript": 30.1, "Python": 15.3, "CSS": 9.4 },
                primary_languages: { "JavaScript": 5, "TypeScript": 4, "Python": 2, "HTML": 1 }
            },
            commit_patterns: {
                total_commits_analyzed: 342,
                avg_commits_per_week: 6.5,
                consistency_score: 65
            }
        },
        code_quality: {
            repo_analysis: [
                {
                    name: "ecommerce-platform",
                    language: "JavaScript",
                    stars: 28,
                    test_coverage: 12.5,
                    documentation_score: 58,
                    architecture_score: 62,
                    naming_score: 55,
                    detected_patterns: ["Component-Based", "Layered Architecture"],
                    code_smells: [
                        { type: "long_function", severity: "warning", description: "Function processOrder() exceeds 120 lines", file: "services/orderService.js", fix: "Break into smaller functions with single responsibility", recommendation: "Refactor into validateOrder, calculateTotal, processPayment" },
                        { type: "console_log", severity: "info", description: "Console.log found in production code", file: "components/Checkout.tsx", fix: "Replace with proper logging library", recommendation: "Use Winston or similar logging library" }
                    ]
                },
                {
                    name: "task-management-api",
                    language: "TypeScript",
                    stars: 15,
                    test_coverage: 45.2,
                    documentation_score: 68,
                    architecture_score: 75,
                    naming_score: 70,
                    detected_patterns: ["Layered Architecture", "MVC"],
                    code_smells: [
                        { type: "todo_fixme", severity: "info", description: "2 TODO comments in auth middleware", file: "middleware/auth.ts", fix: "Implement role-based access control", recommendation: "Complete the TODO items before production" }
                    ]
                },
                {
                    name: "portfolio-website",
                    language: "TypeScript",
                    stars: 8,
                    test_coverage: 0,
                    documentation_score: 15,
                    architecture_score: 55,
                    naming_score: 60,
                    detected_patterns: ["Component-Based"],
                    code_smells: [
                        { type: "unused_imports", severity: "info", description: "Unused imports in Hero.tsx", file: "components/Hero.tsx", fix: "Clean up imports", recommendation: "Remove unused imports to reduce bundle size" }
                    ]
                }
            ],
            aggregate_scores: {
                test_coverage_avg: 19.2,
                documentation_avg: 47.0,
                architecture_avg: 64.0,
                naming_avg: 61.7,
                modularity_score: 52.3,
                total_code_smells: 4,
                overall_quality_score: 48.8
            }
        },
        live_app_audit: {
            performed: false
        },
        security_scan: {
            security_score: 65,
            total_issues: 4,
            critical_count: 1,
            warning_count: 3,
            info_count: 0,
            security_rating: "C - Acceptable",
            issues: [
                { type: "hardcoded_secret", severity: "critical", category: "Secret Management", repo: "ecommerce-platform", file: "config/database.js", description: "Database password hardcoded in connection string", evidence: "password: 'admin123'", recommendation: "Use environment variables: process.env.DB_PASSWORD", fix: "Move all secrets to .env file" },
                { type: "sql_injection", severity: "warning", category: "SQL Injection", repo: "task-management-api", file: "controllers/taskController.js", description: "User input concatenated directly into SQL query", evidence: "db.query(`SELECT * FROM tasks WHERE id = ${req.params.id}`)", recommendation: "Use parameterized queries", fix: "Replace with parameterized query" },
                { type: "missing_auth", severity: "warning", category: "Authentication", repo: "blog-cms", file: "routes/postRoutes.js", description: "POST endpoint lacks authentication middleware", recommendation: "Add authentication middleware", fix: "Add authenticate middleware to route" },
                { type: "cors_misconfig", severity: "warning", category: "CORS", repo: "ecommerce-platform", file: "app.js", description: "CORS configured to allow all origins", recommendation: "Whitelist specific origins", fix: "Configure CORS with specific origins" }
            ],
            recommendations: [
                { priority: "immediate", message: "1 critical security issue must be fixed before production", actions: ["Fix hardcoded_secret in ecommerce-platform/config/database.js"] },
                { priority: "high", message: "Move all secrets to environment variables or secret management service", actions: ["Use dotenv for local development", "Rotate any exposed credentials"] },
                { priority: "medium", message: "Implement security best practices", actions: ["Add input validation", "Use parameterized queries", "Implement proper authentication"] }
            ]
        },
        market_comparison: {
            demonstrated_level: "Mid-Level",
            claimed_level: "Senior",
            level_match: false,
            percentile: 45,
            interview_success_rate: 18,
            salary_estimate: {
                range_usd: { min: 75000, max: 110000, median: 92500 },
                range_egp: { min: 3750000, max: 5500000, median: 4625000 }
            },
            matching_roles: [
                { role: "Mid-Level Full-Stack Developer", match_percentage: 82, salary_min: 90000, salary_max: 150000, confidence: "high" },
                { role: "Mid-Level Frontend Developer", match_percentage: 75, salary_min: 75000, salary_max: 120000, confidence: "medium" },
                { role: "Junior Backend Developer", match_percentage: 68, salary_min: 55000, salary_max: 80000, confidence: "low" }
            ],
            realistic_companies: [
                { name: "Thoughtworks", remote: true },
                { name: "Vercel", remote: true },
                { name: "Stripe", remote: true },
                { name: "Shopify", remote: true },
                { name: "Twilio", remote: true }
            ],
            skill_gaps: {
                missing_skills: [
                    { skill: "System Design", current_level: "Not demonstrated", required_level: "Proficient", gap_size: "large", learning_time_weeks: 10, impact: "Required for senior roles" },
                    { skill: "Kubernetes", current_level: "Not demonstrated", required_level: "Familiar", gap_size: "medium", learning_time_weeks: 8, impact: "High demand in market" }
                ],
                score_gaps: [
                    { skill: "Testing & Quality Assurance", current_level: "Score: 19/100", required_level: "Score: 70+/100", gap_size: "large", learning_time_weeks: 6, impact: "Critical for senior roles" },
                    { skill: "Software Architecture", current_level: "Score: 64/100", required_level: "Score: 75+/100", gap_size: "medium", learning_time_weeks: 8, impact: "Key differentiator" }
                ],
                total_gaps: 4,
                critical_gaps: 2
            },
            next_level_requirements: {
                next: "Senior",
                estimated_weeks: 52,
                requirements: [
                    "Lead architectural decisions",
                    "Mentor junior developers",
                    "Implement comprehensive testing strategies",
                    "Design scalable systems",
                    "Deep expertise in chosen stack"
                ]
            }
        },
        feedback: [
            { severity: "critical", category: "Testing", repo: "portfolio-website", message: "Repository 'portfolio-website' has virtually no tests (0.0% coverage). A senior engineer would reject PRs without tests.", fix: "Add unit tests for all components. Target 70%+ coverage.", impact: "Moves you from junior to mid-level" },
            { severity: "critical", category: "Documentation", repo: "portfolio-website", message: "Repository 'portfolio-website' has no README. This is a red flag for any hiring manager.", fix: "Create a comprehensive README with project description, setup guide, and screenshots.", impact: "Basic requirement for portfolio projects" },
            { severity: "critical", category: "Security", repo: "ecommerce-platform", file: "config/database.js", message: "Database password hardcoded in connection string: password: 'admin123'", fix: "Use environment variables: process.env.DB_PASSWORD", impact: "Blocking issue for any production role" },
            { severity: "warning", category: "Testing", repo: "ecommerce-platform", message: "Repository 'ecommerce-platform' has insufficient test coverage (12.5%).", fix: "Increase test coverage in ecommerce-platform to at least 70%.", impact: "Shows engineering maturity" },
            { severity: "warning", category: "Architecture", repo: "portfolio-website", message: "Repository 'portfolio-website' shows poor architectural organization (score: 55.0/100).", fix: "Implement proper separation of concerns. Separate components, services, and utilities.", impact: "Key differentiator between junior and senior developers" }
        ],
        roadmap: {
            overview: {
                duration_days: 90,
                target_role: "Senior Full-Stack Developer",
                focus_areas: ["Testing", "Architecture", "Documentation"],
                estimated_daily_hours: 2,
                total_estimated_hours: 180
            },
            weeks: [
                {
                    week: 1,
                    theme: "Foundation & Critical Fixes",
                    focus: "testing",
                    tasks: [
                        { action: "Set up Jest and React Testing Library in portfolio-website", deliverable: "Working test environment" },
                        { action: "Write first unit test for Hero component", deliverable: "Passing test" },
                        { action: "Fix hardcoded database password in ecommerce-platform", deliverable: "Secrets moved to .env" }
                    ],
                    milestone: "Test environment ready, critical security fix deployed"
                },
                {
                    week: 2,
                    theme: "Testing Deep Dive",
                    focus: "testing",
                    tasks: [
                        { action: "Complete 'JavaScript Testing Fundamentals' course", deliverable: "Course completion" },
                        { action: "Write tests for all utility functions in ecommerce-platform", deliverable: "20+ passing tests" },
                        { action: "Add integration test for checkout flow", deliverable: "End-to-end test passing" }
                    ],
                    milestone: "50+ tests passing across all projects"
                },
                {
                    week: 3,
                    theme: "Architecture Fundamentals",
                    focus: "architecture",
                    tasks: [
                        { action: "Read Clean Architecture Chapters 1-6", deliverable: "Reading notes" },
                        { action: "Refactor portfolio-website to proper folder structure", deliverable: "components/, hooks/, utils/ folders" },
                        { action: "Separate concerns in ecommerce-platform services", deliverable: "Single-responsibility services" }
                    ],
                    milestone: "All projects have proper folder structure"
                },
                {
                    week: 4,
                    theme: "Documentation Week",
                    focus: "documentation",
                    tasks: [
                        { action: "Write comprehensive README for portfolio-website", deliverable: "Complete README with screenshots" },
                        { action: "Add API documentation to task-management-api", deliverable: "Swagger/OpenAPI docs" },
                        { action: "Document architecture decisions in ecommerce-platform", deliverable: "ADR files in docs/ folder" }
                    ],
                    milestone: "All repositories have professional documentation"
                },
                {
                    week: 5,
                    theme: "Testing at Scale",
                    focus: "testing",
                    tasks: [
                        { action: "Set up CI/CD pipeline with GitHub Actions", deliverable: "Automated test runs on PR" },
                        { action: "Add code coverage reporting", deliverable: "Coverage badge in README" },
                        { action: "Achieve 70% coverage in ecommerce-platform", deliverable: "Coverage report showing 70%+" }
                    ],
                    milestone: "CI/CD pipeline running, 70% coverage achieved"
                },
                {
                    week: 6,
                    theme: "Advanced Patterns",
                    focus: "architecture",
                    tasks: [
                        { action: "Implement custom hooks library in portfolio-website", deliverable: "5+ reusable hooks" },
                        { action: "Add error boundary and loading states", deliverable: "Robust UI handling" },
                        { action: "Refactor to use dependency injection pattern", deliverable: "Testable service layer" }
                    ],
                    milestone: "Production-quality patterns in all projects"
                }
            ],
            milestones: [
                { day: 30, title: "Foundation Complete", description: "All critical weaknesses identified and initial fixes implemented", deliverables: ["Critical security issues fixed", "Test coverage improved by 20%", "Documentation added to all repos"] },
                { day: 60, title: "Skill Building Progress", description: "Intermediate skills developed in primary weak areas", deliverables: ["One project fully tested (70%+ coverage)", "One project refactored with proper architecture"] },
                { day: 90, title: "Portfolio Ready", description: "Demonstrable skill improvement across all weak areas", deliverables: ["Portfolio reflects senior-level practices", "Ready for senior-level interviews"] }
            ],
            measurable_goals: [
                { area: "Testing", current: "19/100", target: "70/100", measurement_method: "Automated test coverage report", deadline_days: 90, priority: "critical" },
                { area: "Documentation", current: "47/100", target: "75/100", measurement_method: "README quality score", deadline_days: 90, priority: "high" },
                { area: "Architecture", current: "64/100", target: "80/100", measurement_method: "Architecture pattern detection", deadline_days: 90, priority: "high" },
                { area: "Overall Score", current: "52/100", target: "72/100", measurement_method: "Complete re-audit", deadline_days: 90, priority: "high" }
            ]
        },
        resume_bullets: {
            bullets: [
                "Architected ecommerce-platform using Component-Based and Layered Architecture patterns with React and Node.js, ensuring maintainable and scalable code structure",
                "Achieved 45.2% code coverage in task-management-api through comprehensive unit and integration testing, reducing production bugs and enabling confident refactoring",
                "Maintained 75/100 architecture score in task-management-api with consistent coding standards and proper separation of concerns across MVC layers",
                "Developed full-stack e-commerce platform with React, Node.js, and MongoDB, earning 28 GitHub stars and demonstrating end-to-end delivery capability",
                "Implemented JWT authentication and authorization in task-management-api, ensuring secure API endpoints and user data protection",
                "Built RESTful API for task management with TypeScript and Express, demonstrating backend architecture and API design skills",
                "Maintained consistent development practice with 342+ commits across 12 repositories, averaging 6.5 commits per week",
                "Proficient in full-stack development with expertise in JavaScript, TypeScript, and Python, demonstrated through production-quality projects"
            ],
            total_generated: 8,
            strengths_highlighted: ["Software Architecture & Design Patterns", "Full-Stack Development Capability"],
            omitted_claims: [
                { claim: "'Extensive testing experience'", reason: "Actual test coverage: 19.2%", recommendation: "Remove or change to 'Learning testing practices'" },
                { claim: "'Expert in software architecture'", reason: "Architecture score: 64.0/100", recommendation: "Remove until architectural patterns are demonstrated" }
            ],
            recommendations: [
                { priority: "high", message: "Lead with your strongest 3 bullets that have specific metrics", example: "Architected ecommerce-platform using Component-Based and Layered Architecture patterns with React and Node.js, ensuring maintainable and scalable code structure" },
                { priority: "medium", message: "Quantify impact wherever possible - numbers catch recruiter attention", tips: ["Use GitHub stars as social proof", "Include test coverage percentages"] }
            ]
        }
    };
}
