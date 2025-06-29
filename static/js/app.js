// Resume Analyzer Application JavaScript
class ResumeAnalyzer {
    constructor() {
        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.form = document.getElementById('upload-form');
        this.fileInput = document.getElementById('resume-file');
        this.analyzeBtn = document.getElementById('analyze-btn');
        this.loading = document.getElementById('loading');
        this.errorMessage = document.getElementById('error-message');
        this.resultsSection = document.getElementById('results-section');
        this.analysisContent = document.getElementById('analysis-content');
        this.questionsContent = document.getElementById('questions-content');
    }

    bindEvents() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.fileInput.addEventListener('change', () => this.handleFileChange());
    }

    handleFileChange() {
        const file = this.fileInput.files[0];
        if (file) {
            // Validate file type
            if (file.type !== 'application/pdf') {
                this.showError('Please select a PDF file only.');
                this.fileInput.value = '';
                return;
            }

            // Validate file size (16MB max)
            const maxSize = 16 * 1024 * 1024; // 16MB in bytes
            if (file.size > maxSize) {
                this.showError('File size must be less than 16MB.');
                this.fileInput.value = '';
                return;
            }

            this.hideError();
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const file = this.fileInput.files[0];
        if (!file) {
            this.showError('Please select a PDF file to analyze.');
            return;
        }

        this.showLoading();
        this.hideError();
        this.hideResults();

        try {
            const formData = new FormData();
            formData.append('resume', file);

            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.displayResults(data.analysis, data.questions);
            } else {
                this.showError(data.error || 'An error occurred while processing your resume.');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            this.hideLoading();
        }
    }

    displayResults(analysis, questions) {
        this.displayAnalysis(analysis);
        this.displayQuestions(questions);
        this.showResults();
    }

    displayAnalysis(analysis) {
        const { candidate_name, contact_info = {}, skills, education, experience, projects, candidate_summary } = analysis;
        
        let html = `
            <div class="candidate-info">
                <div class="candidate-name">${this.escapeHtml(candidate_name)}</div>
                
                <div class="info-section">
                    <h4>Contact Details</h4>
                    <div class="info-content">
                        ${contact_info.email ? `<p><strong>Email:</strong> ${this.escapeHtml(contact_info.email)}</p>` : ''}
                        ${contact_info.phone ? `<p><strong>Phone:</strong> ${this.escapeHtml(contact_info.phone)}</p>` : ''}
                        ${contact_info.address ? `<p><strong>Address:</strong> ${this.escapeHtml(contact_info.address)}</p>` : ''}
                        ${!contact_info.email && !contact_info.phone && !contact_info.address ? '<p>No contact information found.</p>' : ''}
                    </div>
                </div>
                
                <div class="info-section">
                    <h4>Candidate Summary</h4>
                    <div class="info-content">
                        ${candidate_summary ? 
                            `<p>${this.escapeHtml(candidate_summary)}</p>` : 
                            '<p>This candidate\'s resume has been thoroughly analyzed for technical competencies, professional background, and project experience. The following sections provide a detailed breakdown of their qualifications and capabilities.</p>'
                        }
                    </div>
                </div>
                
                <div class="info-section">
                    <h4>Education Background</h4>
                    <div class="info-content">
                        ${education ? this.escapeHtml(education) : 'No education information found.'}
                    </div>
                </div>
                
                <div class="info-section">
                    <h4>Professional Experience</h4>
                    <div class="info-content">
                        ${experience ? 
                            `<p>${this.formatExperience(experience)}</p>` : 
                            '<p>The candidate appears to be seeking entry-level opportunities or has primarily academic experience.</p>'
                        }
                    </div>
                </div>
                
                <div class="info-section">
                    <h4>Technical Skills</h4>
                    <div class="info-content">
                        ${skills && skills.length > 0 ? 
                            `<div class="skills-list">
                                ${skills.map(skill => `<span class="skill-tag">${this.escapeHtml(skill)}</span>`).join('')}
                            </div>` : 
                            'No specific technical skills identified.'
                        }
                    </div>
                </div>
        `;

        if (projects && projects.length > 0) {
            // Filter out invalid project entries
            const validProjects = projects.filter(project => 
                project && 
                project.length > 5 && 
                !project.toLowerCase().includes('department') &&
                !project.toLowerCase().includes('college') &&
                !project.toLowerCase().includes('university')
            );
            
            if (validProjects.length > 0) {
                html += `
                    <div class="info-section">
                        <h4>Key Projects</h4>
                        <div class="info-content">
                            <p>Notable projects completed by the candidate:</p>
                            <ul>
                                ${validProjects.map(project => `<li><strong>${this.escapeHtml(project)}</strong></li>`).join('')}
                            </ul>
                        </div>
                    </div>
                `;
            }
        }

        html += '</div>';
        this.analysisContent.innerHTML = html;
    }

    displayQuestions(questions) {
        if (!questions || questions.length === 0) {
            this.questionsContent.innerHTML = '<p>No questions could be generated.</p>';
            return;
        }

        const html = `
            <ol class="questions-list">
                ${questions.map(question => `
                    <li class="question-item">
                        <div class="question-text">${this.escapeHtml(question)}</div>
                    </li>
                `).join('')}
            </ol>
        `;
        
        this.questionsContent.innerHTML = html;
    }

    showLoading() {
        this.loading.style.display = 'block';
        this.analyzeBtn.disabled = true;
        this.analyzeBtn.textContent = 'Analyzing...';
    }

    hideLoading() {
        this.loading.style.display = 'none';
        this.analyzeBtn.disabled = false;
        this.analyzeBtn.textContent = 'Analyze Resume';
    }

    showError(message) {
        this.errorMessage.innerHTML = `
            <strong>Error:</strong> ${this.escapeHtml(message)}
        `;
        this.errorMessage.style.display = 'block';
    }

    hideError() {
        this.errorMessage.style.display = 'none';
    }

    showResults() {
        this.resultsSection.style.display = 'block';
        this.resultsSection.classList.add('show');
        // Scroll to results
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    hideResults() {
        this.resultsSection.style.display = 'none';
        this.resultsSection.classList.remove('show');
    }

    formatExperience(experience) {
        // Clean up and summarize experience text
        let cleaned = experience.replace(/\s+/g, ' ').trim();
        
        // If it's too long, provide a summary
        if (cleaned.length > 200) {
            cleaned = cleaned.substring(0, 200) + '...';
        }
        
        // Add professional context if it looks like academic projects
        if (cleaned.toLowerCase().includes('machine learning') || 
            cleaned.toLowerCase().includes('project') || 
            cleaned.toLowerCase().includes('academic')) {
            return `The candidate has academic and project experience ${cleaned.toLowerCase()}`;
        }
        
        return cleaned;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new ResumeAnalyzer();
});

// Handle file drag and drop
document.addEventListener('DOMContentLoaded', function() {
    const uploadSection = document.querySelector('.upload-section');
    const fileInput = document.getElementById('resume-file');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadSection.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadSection.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadSection.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        uploadSection.style.borderColor = '#4ade80';
        uploadSection.style.backgroundColor = '#1f2937';
    }

    function unhighlight(e) {
        uploadSection.style.borderColor = '#4a5568';
        uploadSection.style.backgroundColor = '#2a2a2a';
    }

    uploadSection.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change'));
        }
    }
});
