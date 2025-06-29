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
        
        # Comprehensive technical skills for tech industry
        self.skill_categories = {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'php', 'ruby', 'go', 'rust', 'swift', 
                'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash', 'powershell'
            ],
            'web_technologies': [
                'html', 'css', 'react', 'angular', 'vue', 'vue.js', 'node.js', 'express', 'django', 'flask', 
                'spring', 'laravel', 'bootstrap', 'jquery', 'webpack', 'babel', 'sass', 'less'
            ],
            'databases': [
                'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'sqlite', 'redis', 'cassandra', 'elasticsearch', 
                'dynamodb', 'neo4j', 'firebase', 'supabase'
            ],
            'cloud_devops': [
                'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions', 
                'terraform', 'ansible', 'chef', 'puppet', 'vagrant', 'heroku', 'vercel', 'netlify'
            ],
            'data_science_ml': [
                'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'jupyter', 
                'anaconda', 'spark', 'hadoop', 'kafka', 'airflow', 'machine learning', 'deep learning', 'nlp'
            ],
            'tools_frameworks': [
                'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack', 'trello', 'asana', 
                'figma', 'sketch', 'photoshop', 'illustrator', 'postman', 'swagger', 'rest api', 'graphql'
            ],
            'mobile_development': [
                'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova', 'swift', 'objective-c', 'kotlin'
            ],
            'testing_qa': [
                'selenium', 'cypress', 'jest', 'mocha', 'chai', 'pytest', 'junit', 'testng', 'cucumber', 'postman'
            ]
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
        """Extract only legitimate technical skills relevant to tech industry"""
        text_lower = text.lower()
        found_skills = []
        
        # Create a comprehensive list of all technical skills
        all_tech_skills = []
        for category, skills in self.skill_categories.items():
            all_tech_skills.extend(skills)
        
        # Search for exact matches of technical skills in the text
        for skill in all_tech_skills:
            # Use word boundaries to match exact skills
            pattern = rf'\b{re.escape(skill.lower())}\b'
            if re.search(pattern, text_lower):
                # Preserve original casing for known technical terms
                if skill.lower() in ['html', 'css', 'sql', 'php', 'api', 'nlp', 'aws', 'gcp', 'ios']:
                    found_skills.append(skill.upper())
                elif skill.lower() in ['javascript', 'typescript', 'node.js', 'vue.js']:
                    found_skills.append(skill)
                else:
                    found_skills.append(skill.title())
        
        # Also check for specific technical patterns in the text
        tech_patterns = [
            r'\b(C\+\+|C#|\.NET|REST API|GraphQL)\b',
            r'\b(Machine Learning|Deep Learning|Data Science|AI|ML|NLP)\b',
            r'\b(React\.js|Angular\.js|Vue\.js|Node\.js)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                found_skills.append(match)
        
        # Remove duplicates while preserving order
        unique_skills = []
        seen = set()
        for skill in found_skills:
            skill_lower = skill.lower()
            if skill_lower not in seen:
                unique_skills.append(skill)
                seen.add(skill_lower)
        
        return unique_skills[:12]  # Limit to 12 most relevant technical skills
    
    def extract_section(self, text: str, section_name: str) -> str:
        """Extract specific section content from resume with better formatting"""
        keywords = self.required_keywords.get(section_name, [section_name])
        
        for keyword in keywords:
            # Try multiple patterns for better section extraction
            patterns = [
                rf'(?i){re.escape(keyword)}[:\s]*\n(.+?)(?=\n\s*[A-Z][A-Za-z\s]*\s*:|$)',
                rf'(?i){re.escape(keyword)}[:\s]*(.+?)(?=\n\s*[A-Z][A-Za-z\s]*\s*:|$)',
                rf'(?i){re.escape(keyword)}[:\s\n]*(.+?)(?=\n\n|\n[A-Z][A-Za-z\s]*\s*:|$)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    content = match.group(1).strip()
                    # Clean up the content
                    content = re.sub(r'\n\s*\n', '\n', content)  # Remove extra blank lines
                    content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
                    if len(content) > 20:  # Only return if substantial content
                        return content
        
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
        """Extract and format work experience information"""
        experience_section = self.extract_section(text, 'experience')
        
        if not experience_section:
            # Look for experience patterns in the entire text
            lines = text.split('\n')
            experience_lines = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                # Look for job title patterns
                if re.search(r'(?i)(developer|engineer|analyst|manager|coordinator|specialist|consultant|intern)', line):
                    # Include this line and next few lines as context
                    experience_lines.append(line)
                    for j in range(i+1, min(i+4, len(lines))):
                        if lines[j].strip() and len(lines[j].strip()) > 10:
                            experience_lines.append(lines[j].strip())
                        else:
                            break
            
            if experience_lines:
                experience_section = ' '.join(experience_lines)
        
        # Format the experience section better
        if experience_section:
            # Remove excessive whitespace and format properly
            experience_section = re.sub(r'\s+', ' ', experience_section)
            experience_section = re.sub(r'([.!?])\s*', r'\1 ', experience_section)
            
        return experience_section
    
    def extract_projects(self, text: str) -> List[str]:
        """Extract structured project information"""
        projects_section = self.extract_section(text, 'projects')
        projects = []
        
        if projects_section:
            # Look for project patterns with better parsing
            project_patterns = [
                r'(?i)([^•\n\*-]+?)\s*(?:•|\*|-|\n)\s*(?:algorithms?\s*&?\s*tools?:|technologies?:|tools?:)\s*([^•\n\*-]+?)(?=\s*(?:•|\*|-|\n|outcome:|$))',
                r'(?i)^([^•\n\*-]+?)\s*(?:•|\*|-|\n)',
                r'(?i)([A-Z][^•\n\*-]{10,50})\s*(?:•|\*|-)'
            ]
            
            for pattern in project_patterns:
                matches = re.findall(pattern, projects_section, re.MULTILINE)
                for match in matches:
                    if isinstance(match, tuple):
                        project_name = match[0].strip()
                    else:
                        project_name = match.strip()
                    
                    # Clean project name
                    project_name = re.sub(r'^[\d\.\)\s•\*-]+', '', project_name)
                    project_name = project_name.strip()
                    
                    if (len(project_name) > 5 and len(project_name) < 100 and 
                        not re.search(r'(?i)(algorithms?|tools?|outcome|technologies?)', project_name)):
                        projects.append(project_name)
            
            # If no structured projects found, look for lines that might be project titles
            if not projects:
                lines = projects_section.split('\n')
                for line in lines:
                    line = line.strip()
                    if (len(line) > 10 and len(line) < 80 and 
                        not re.search(r'(?i)(algorithms?|tools?|outcome|technologies?|developed|created|built)', line)):
                        # Remove bullet points and numbering
                        clean_line = re.sub(r'^[\d\.\)\s•\*-]+', '', line)
                        if clean_line.strip():
                            projects.append(clean_line.strip())
        
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
