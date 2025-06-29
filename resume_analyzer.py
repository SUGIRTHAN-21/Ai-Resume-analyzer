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
        
        # Resume validation patterns - documents should contain these patterns
        self.resume_indicators = [
            r'(?i)\b(resume|curriculum vitae|cv)\b',
            r'(?i)\b(objective|summary|profile)\b',
            r'(?i)\b(phone|email|contact|address)\b',
            r'(?i)\b(bachelor|master|degree|university|college)\b',
            r'(?i)\b(developer|engineer|analyst|manager|intern)\b',
            r'(?i)\b(programming|software|web|technical)\b'
        ]
        
        # Non-resume document indicators
        self.non_resume_indicators = [
            r'(?i)\b(internship letter|offer letter|appointment letter)\b',
            r'(?i)\b(dear|congratulations|pleased to inform)\b',
            r'(?i)\b(company letterhead|official letter)\b',
            r'(?i)\b(terms and conditions|salary|compensation)\b',
            r'(?i)\b(joining date|start date|reporting)\b'
        ]
        
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
    
    def validate_document_type(self, text: str) -> Dict[str, Any]:
        """Validate if document is actually a resume"""
        text_lower = text.lower()
        
        # Check for non-resume indicators first
        non_resume_matches = 0
        for pattern in self.non_resume_indicators:
            if re.search(pattern, text_lower):
                non_resume_matches += 1
        
        # If too many non-resume indicators, reject
        if non_resume_matches >= 2:
            return {
                'is_resume': False,
                'reason': 'Document appears to be an offer letter, internship letter, or other official document, not a resume.'
            }
        
        # Check for resume indicators
        resume_matches = 0
        for pattern in self.resume_indicators:
            if re.search(pattern, text_lower):
                resume_matches += 1
        
        # Need at least 3 resume indicators
        if resume_matches < 3:
            return {
                'is_resume': False,
                'reason': 'Document does not contain sufficient resume characteristics. Please upload a valid resume.'
            }
        
        return {
            'is_resume': True,
            'resume_score': resume_matches
        }
    
    def validate_resume_sections(self, text: str) -> Dict[str, bool]:
        """Validate if resume contains required sections"""
        text_lower = text.lower()
        found_sections = {}
        
        for section, keywords in self.required_keywords.items():
            found = any(keyword in text_lower for keyword in keywords)
            found_sections[section] = found
        
        return found_sections
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from resume"""
        contact_info = {
            'email': '',
            'phone': '',
            'address': ''
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Extract phone
        phone_pattern = r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
        
        # Extract address (basic extraction)
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if any(word in line.lower() for word in ['street', 'avenue', 'road', 'city', 'state']):
                if len(line) > 10 and len(line) < 100:
                    contact_info['address'] = line
                    break
        
        return contact_info
    
    def extract_name(self, text: str) -> str:
        """Extract candidate name from resume"""
        lines = text.split('\n')
        
        # Look for name in first few lines
        for line in lines[:5]:
            line = line.strip()
            if line and len(line.split()) <= 4:  # Names are usually 1-4 words
                # Filter out common non-name patterns
                if not any(word in line.lower() for word in ['email', 'phone', 'address', 'resume', 'cv', '@', 'http']):
                    # Check if it looks like a name (contains alphabetic characters)
                    if re.search(r'^[A-Za-z\s\.]+$', line) and len(line) > 2:
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
            
            # First validate if document is actually a resume
            doc_validation = self.validate_document_type(text)
            if not doc_validation['is_resume']:
                return {
                    'is_valid': False,
                    'error_message': f'Please enter a valid resume only. {doc_validation["reason"]}'
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
            contact_info = self.extract_contact_info(text)
            skills = self.extract_skills(text)
            education = self.extract_education(text)
            experience = self.extract_experience(text)
            projects = self.extract_projects(text)
            
            return {
                'is_valid': True,
                'candidate_name': name,
                'contact_info': contact_info,
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
