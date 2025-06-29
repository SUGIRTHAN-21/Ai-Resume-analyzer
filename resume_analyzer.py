import re
import logging
from typing import Dict, List, Any
import fitz  # PyMuPDF
import pdfplumber

class ResumeAnalyzer:
    """Analyzes resume content and extracts key information"""
    
    def __init__(self):
        # Required keywords for validation
        self.required_keywords = {
            'experience': ['experience', 'work experience', 'employment', 'career', 'professional experience', 'work history'],
            'education': ['education', 'academic', 'degree', 'university', 'college', 'school', 'qualification'],
            'skills': ['skills', 'technical skills', 'competencies', 'expertise', 'technologies', 'programming'],
            'projects': ['projects', 'project', 'portfolio', 'work samples', 'achievements']
        }
        
        # Common skill categories
        self.skill_categories = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'sqlite', 'redis'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins'],
            'tools': ['git', 'github', 'gitlab', 'jira', 'confluence', 'slack']
        }
    
    def extract_text_pymupdf(self, file_path: str) -> str:
        """Extract text using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logging.error(f"PyMuPDF extraction failed: {str(e)}")
            return ""
    
    def extract_text_pdfplumber(self, file_path: str) -> str:
        """Extract text using pdfplumber as backup"""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            logging.error(f"pdfplumber extraction failed: {str(e)}")
            return ""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF using available methods"""
        # Try PyMuPDF first
        text = self.extract_text_pymupdf(file_path)
        
        # Fallback to pdfplumber if PyMuPDF fails
        if not text.strip():
            text = self.extract_text_pdfplumber(file_path)
        
        return text.strip()
    
    def validate_resume_sections(self, text: str) -> Dict[str, bool]:
        """Validate if resume contains required sections"""
        text_lower = text.lower()
        found_sections = {}
        
        for section, keywords in self.required_keywords.items():
            found = any(keyword in text_lower for keyword in keywords)
            found_sections[section] = found
        
        return found_sections
    
    def extract_name(self, text: str) -> str:
        """Extract candidate name from resume"""
        lines = text.split('\n')
        
        # Look for name in first few lines
        for line in lines[:5]:
            line = line.strip()
            if line and len(line.split()) <= 4:  # Names are usually 1-4 words
                # Filter out common non-name patterns
                if not any(word in line.lower() for word in ['email', 'phone', 'address', 'resume', 'cv']):
                    # Check if it looks like a name (contains alphabetic characters)
                    if re.search(r'[a-zA-Z]', line):
                        return line
        
        return "Candidate"
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        text_lower = text.lower()
        found_skills = []
        
        for category, skills in self.skill_categories.items():
            for skill in skills:
                if skill in text_lower:
                    found_skills.append(skill.title())
        
        # Also look for skills in dedicated skills section
        skills_section = self.extract_section(text, 'skills')
        if skills_section:
            # Extract comma-separated skills
            skill_matches = re.findall(r'\b[A-Za-z][A-Za-z0-9+#.]*\b', skills_section)
            for skill in skill_matches:
                if len(skill) > 2 and skill.lower() not in ['and', 'the', 'with', 'for']:
                    found_skills.append(skill.title())
        
        return list(set(found_skills))  # Remove duplicates
    
    def extract_section(self, text: str, section_name: str) -> str:
        """Extract specific section content from resume"""
        keywords = self.required_keywords.get(section_name, [section_name])
        
        for keyword in keywords:
            pattern = rf'(?i){re.escape(keyword)}[:\s]*(.+?)(?=\n\s*[A-Z][A-Za-z\s]*:|$)'
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def extract_education(self, text: str) -> str:
        """Extract education information"""
        education_section = self.extract_section(text, 'education')
        
        if not education_section:
            # Look for degree patterns
            degree_pattern = r'(?i)(bachelor|master|phd|doctorate|b\.?[satechm]\.?|m\.?[satechm]\.?|associate)'
            matches = re.findall(degree_pattern + r'[^.\n]*', text)
            if matches:
                education_section = '. '.join(matches)
        
        return education_section
    
    def extract_experience(self, text: str) -> str:
        """Extract work experience information"""
        experience_section = self.extract_section(text, 'experience')
        
        if not experience_section:
            # Look for job title patterns
            job_patterns = [
                r'(?i)(developer|engineer|analyst|manager|coordinator|specialist|consultant)',
                r'(?i)(senior|junior|lead|principal)\s+\w+',
                r'\d{4}\s*[-–]\s*(?:\d{4}|present)'
            ]
            
            for pattern in job_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    experience_section = self.extract_section(text, 'work')
                    break
        
        return experience_section
    
    def extract_projects(self, text: str) -> List[str]:
        """Extract project information"""
        projects_section = self.extract_section(text, 'projects')
        projects = []
        
        if projects_section:
            # Split by common project delimiters
            project_lines = re.split(r'\n\s*(?=\d+\.|\•|\*|-)', projects_section)
            for line in project_lines:
                line = line.strip()
                if line and len(line) > 10:  # Filter out short lines
                    # Extract project name (usually the first part)
                    project_name = line.split('\n')[0].strip()
                    if project_name:
                        projects.append(project_name)
        
        return projects[:5]  # Limit to 5 projects
    
    def analyze_resume(self, file_path: str) -> Dict[str, Any]:
        """Main method to analyze resume"""
        try:
            # Extract text from PDF
            text = self.extract_text(file_path)
            
            if not text:
                return {
                    'is_valid': False,
                    'error_message': 'Unable to extract text from PDF. Please ensure the file is not corrupted or password-protected.'
                }
            
            # Validate required sections
            sections = self.validate_resume_sections(text)
            missing_sections = [section for section, found in sections.items() if not found]
            
            if len(missing_sections) >= 3:  # Allow missing 1-2 sections
                return {
                    'is_valid': False,
                    'error_message': f'Please enter a valid industry resume. Missing key sections: {", ".join(missing_sections).title()}.'
                }
            
            # Extract information
            name = self.extract_name(text)
            skills = self.extract_skills(text)
            education = self.extract_education(text)
            experience = self.extract_experience(text)
            projects = self.extract_projects(text)
            
            return {
                'is_valid': True,
                'candidate_name': name,
                'skills': skills,
                'education': education,
                'experience': experience,
                'projects': projects,
                'sections_found': sections,
                'full_text': text
            }
            
        except Exception as e:
            logging.error(f"Error analyzing resume: {str(e)}")
            return {
                'is_valid': False,
                'error_message': 'An error occurred while analyzing the resume. Please try again with a different file.'
            }
