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
        
        # Extract email with validation
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            email = email_match.group()
            # Additional validation - ensure it's a reasonable email format
            if len(email) > 5 and len(email) < 100 and email.count('@') == 1:
                contact_info['email'] = email
        
        # Extract phone with VERY strict validation - only show if we're 100% certain
        phone_patterns = [
            r'\+\s*91\s+[0-9]{10}',  # Indian format with +91
            r'\+91[0-9]{10}',  # Indian format without space
            r'\+1\s*\([0-9]{3}\)\s*[0-9]{3}[-\s]?[0-9]{4}',  # US format with +1
            r'\([0-9]{3}\)\s*[0-9]{3}[-\s]?[0-9]{4}',  # US format without country code
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                phone = phone_match.group().strip()
                # Extract only digits and country code
                if '+91' in phone:
                    # Indian number - extract digits after +91
                    digits = re.sub(r'[^\d]', '', phone.replace('+91', ''))
                    if len(digits) == 10 and digits[0] in '6789':  # Valid Indian mobile starts with 6,7,8,9
                        contact_info['phone'] = f"+91 {digits}"
                        break
                elif '+1' in phone:
                    # US number - extract digits after +1
                    digits = re.sub(r'[^\d]', '', phone.replace('+1', ''))
                    if len(digits) == 10:
                        contact_info['phone'] = f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
                        break
                else:
                    # No country code - be very conservative
                    digits = re.sub(r'[^\d]', '', phone)
                    if len(digits) == 10 and digits[0] in '6789':  # Assume Indian if starts with 6,7,8,9
                        contact_info['phone'] = f"+91 {digits}"
                        break
                    elif len(digits) == 10 and digits[0] in '2345':  # Assume US if starts with 2,3,4,5
                        contact_info['phone'] = f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
                        break
        
        # If no clear phone pattern found, don't extract anything
        
        # Extract address - ONLY if very clear address patterns
        # Be extremely conservative - only extract if we're 100% sure it's an address
        address_patterns = [
            r'([0-9]+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd),?\s*[A-Za-z\s]+,\s*[A-Z]{2}\s+[0-9]{5})',
            r'([A-Za-z\s]+,\s*[A-Z]{2}\s+[0-9]{5}-[0-9]{4})',  # City, State ZIP+4
        ]
        
        for pattern in address_patterns:
            address_match = re.search(pattern, text)
            if address_match:
                address = address_match.group().strip()
                # Very strict validation - must be clearly an address
                if (len(address) > 20 and len(address) < 80 and
                    ',' in address and  # Must have comma separators
                    re.search(r'[0-9]{5}', address) and  # Must have ZIP code
                    not any(word in address.lower() for word in ['email', 'phone', 'linkedin', 'github', 'http', '@'])):
                    contact_info['address'] = address
                    break
        
        # If no clear address found, don't show anything rather than wrong info
        
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
        """Extract only complete, meaningful project names"""
        projects_section = self.extract_section(text, 'projects')
        projects = []
        
        if projects_section:
            # Look for project titles that are complete sentences/phrases
            # Split by common project separators and clean each potential project
            project_blocks = re.split(r'\n(?=[A-Z])', projects_section)
            
            for block in project_blocks:
                lines = block.strip().split('\n')
                if not lines:
                    continue
                
                # First line should be the project title
                first_line = lines[0].strip()
                
                # Remove bullets and numbering
                first_line = re.sub(r'^[\d\.\)\s•\*-]+', '', first_line)
                first_line = first_line.strip()
                
                # Only accept if it's a complete project name
                if (len(first_line) > 20 and len(first_line) < 100 and
                    not re.search(r'(?i)^(algorithms?|tools?|outcome|technologies?)', first_line) and
                    not any(word in first_line.lower() for word in ['department', 'college', 'university', 'academic projects'])):
                    
                    # Check if it looks like a complete project title
                    if (re.search(r'(?i)(system|application|platform|tool|analyzer|generator|classification|management|detection)', first_line) or
                        re.search(r'(?i)using\s+(machine learning|ai|web|database)', first_line)):
                        projects.append(first_line)
        
        # If no good projects found from section, be very conservative
        # Only return projects if we're confident they're real project names
        if not projects:
            # Don't extract anything rather than show wrong information
            return []
        
        # Final validation - ensure each project makes sense
        validated_projects = []
        for project in projects:
            # Must be a substantial project description
            if (len(project) > 25 and 
                not project.lower().startswith('academic') and
                not project.lower().startswith('department') and
                ' ' in project):  # Must have multiple words
                validated_projects.append(project)
        
        return validated_projects[:3]  # Limit to 3 most substantial projects
    
    def generate_candidate_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Generate a comprehensive 7-8 line paragraph about the candidate"""
        name = analysis_data.get('candidate_name', 'The candidate')
        skills = analysis_data.get('skills', [])
        education = analysis_data.get('education', '')
        experience = analysis_data.get('experience', '')
        projects = analysis_data.get('projects', [])
        
        # Build summary components
        summary_parts = []
        
        # Introduction
        summary_parts.append(f"{name} is a dedicated professional with a strong foundation in technology and programming.")
        
        # Education background
        if education:
            if 'bachelor' in education.lower() or 'master' in education.lower():
                summary_parts.append(f"The candidate holds relevant academic qualifications in computer science or related fields, providing a solid theoretical foundation.")
            else:
                summary_parts.append(f"The candidate has pursued formal education in technology and computer applications.")
        else:
            summary_parts.append(f"The candidate demonstrates strong self-learning capabilities in technology domains.")
        
        # Technical skills
        if skills:
            primary_skills = skills[:5]  # Top 5 skills
            skills_text = ', '.join(primary_skills[:-1]) + f" and {primary_skills[-1]}" if len(primary_skills) > 1 else primary_skills[0]
            summary_parts.append(f"Their technical expertise includes proficiency in {skills_text}, demonstrating versatility across multiple technology stacks.")
        
        # Projects and interests
        if projects:
            if len(projects) >= 2:
                summary_parts.append(f"The candidate has successfully completed {len(projects)} notable projects, including {projects[0]} and {projects[1]}, showcasing practical application of technical skills.")
            else:
                summary_parts.append(f"The candidate has worked on meaningful projects including {projects[0]}, demonstrating hands-on development experience.")
            
            # Analyze project domains for interests
            project_text = ' '.join(projects).lower()
            if 'machine learning' in project_text or 'ai' in project_text:
                summary_parts.append("Their work shows particular interest in artificial intelligence and machine learning technologies.")
            elif 'web' in project_text or 'application' in project_text:
                summary_parts.append("Their focus appears to be on web development and application building.")
            else:
                summary_parts.append("Their project portfolio demonstrates diverse technical interests and problem-solving capabilities.")
        else:
            summary_parts.append("The candidate shows enthusiasm for learning and applying new technologies in practical scenarios.")
        
        # Professional outlook
        if 'intern' in experience.lower() or not experience:
            summary_parts.append("As an emerging professional, they are eager to contribute to challenging projects and grow within a dynamic technology environment.")
        else:
            summary_parts.append("With their combination of technical skills and practical experience, they are well-positioned to contribute effectively to technology teams.")
        
        # Join all parts into a cohesive paragraph
        return ' '.join(summary_parts)
    
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
            
            # Prepare analysis data
            analysis_data = {
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
            
            # Generate comprehensive candidate summary
            analysis_data['candidate_summary'] = self.generate_candidate_summary(analysis_data)
            
            return analysis_data
            
        except Exception as e:
            logging.error(f"Error analyzing resume: {str(e)}")
            return {
                'is_valid': False,
                'error_message': 'An error occurred while analyzing the resume. Please try again with a different file.'
            }
