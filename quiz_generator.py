import re
import random
from typing import List, Dict, Any

class QuizGenerator:
    """Generates tailored interview questions based on resume analysis"""
    
    def __init__(self):
        # Question templates for different categories
        self.question_templates = {
            'technical_skills': [
                "Can you explain your experience with {skill} and how you've used it in your projects?",
                "What challenges have you faced while working with {skill} and how did you overcome them?",
                "How would you rate your proficiency in {skill} and what projects demonstrate this?",
                "Describe a specific instance where {skill} was crucial to completing a project successfully.",
                "What best practices do you follow when working with {skill}?"
            ],
            'experience': [
                "Tell me about your role as {position} and your key responsibilities.",
                "What was your most significant achievement in your {position} role?",
                "How did you handle challenges and deadlines in your {position} position?",
                "What methodologies or processes did you implement in your {position} role?"
            ],
            'projects': [
                "Walk me through the {project} project - what was your role and what technologies did you use?",
                "What was the most challenging aspect of the {project} project and how did you solve it?",
                "How did you ensure the quality and success of the {project} project?",
                "What would you do differently if you were to restart the {project} project today?",
                "Can you explain the architecture and technical decisions made in the {project} project?"
            ],
            'soft_skills': [
                "How do you handle working under pressure and tight deadlines?",
                "Describe a time when you had to work with a difficult team member.",
                "How do you stay updated with the latest technologies and industry trends?",
                "What motivates you to excel in your professional work?",
                "How do you approach problem-solving when faced with a complex technical issue?"
            ],
            'education': [
                "How has your {degree} education prepared you for this role?",
                "What was your favorite subject or project during your {degree} studies?",
                "How do you apply the theoretical knowledge from your {degree} to practical work?"
            ]
        }
    
    def extract_positions(self, experience_text: str) -> List[str]:
        """Extract job positions from experience text"""
        if not experience_text:
            return []
        
        # Common job title patterns
        position_patterns = [
            r'(?i)(software|web|mobile|frontend|backend|full-stack|data|machine learning|ai|devops|cloud)\s+(developer|engineer|architect|analyst|scientist)',
            r'(?i)(senior|junior|lead|principal|associate)\s+\w+\s+(developer|engineer|analyst|manager)',
            r'(?i)(project|product|engineering|technical|development)\s+(manager|lead|coordinator)',
            r'(?i)(intern|trainee|consultant|specialist)\s+\w*',
            r'(?i)\b(developer|engineer|analyst|manager|coordinator|specialist|consultant|architect|designer)\b'
        ]
        
        positions = []
        for pattern in position_patterns:
            matches = re.findall(pattern, experience_text)
            for match in matches:
                if isinstance(match, tuple):
                    position = ' '.join(match)
                else:
                    position = match
                positions.append(position.title())
        
        return list(set(positions))[:3]  # Limit to 3 positions
    
    def extract_degree_info(self, education_text: str) -> List[str]:
        """Extract degree information from education text"""
        if not education_text:
            return []
        
        degree_patterns = [
            r'(?i)(bachelor|master|phd|doctorate)(?:\s+of|\s+in|\s+of\s+science|\s+of\s+arts|\s+of\s+engineering|\s+of\s+technology)?\s+([^.\n,]+)',
            r'(?i)(b\.?[satechm]\.?|m\.?[satechm]\.?|associate)\s+([^.\n,]+)',
            r'(?i)(diploma|certificate)\s+in\s+([^.\n,]+)'
        ]
        
        degrees = []
        for pattern in degree_patterns:
            matches = re.findall(pattern, education_text)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    degree = f"{match[0]} {match[1]}".strip()
                    degrees.append(degree.title())
        
        return list(set(degrees))[:2]  # Limit to 2 degrees
    
    def clean_project_name(self, project: str) -> str:
        """Clean and extract project name"""
        # Remove numbering, bullets, and extra formatting
        project = re.sub(r'^[\d\.\)\•\*\-\s]+', '', project)
        
        # Take first line or first sentence
        lines = project.split('\n')
        if lines:
            project = lines[0]
        
        sentences = project.split('.')
        if sentences:
            project = sentences[0]
        
        # Limit length
        if len(project) > 60:
            project = project[:60] + "..."
        
        return project.strip()
    
    def generate_skill_questions(self, skills: List[str], count: int) -> List[str]:
        """Generate questions based on skills"""
        if not skills or count <= 0:
            return []
        
        questions = []
        selected_skills = random.sample(skills, min(len(skills), count))
        
        for skill in selected_skills:
            template = random.choice(self.question_templates['technical_skills'])
            question = template.format(skill=skill)
            questions.append(question)
        
        return questions
    
    def generate_experience_questions(self, experience_text: str, count: int) -> List[str]:
        """Generate questions based on work experience"""
        if not experience_text or count <= 0:
            return []
        
        positions = self.extract_positions(experience_text)
        if not positions:
            return []
        
        questions = []
        for i in range(min(count, len(positions))):
            position = positions[i % len(positions)]
            template = random.choice(self.question_templates['experience'])
            question = template.format(position=position)
            questions.append(question)
        
        return questions
    
    def generate_project_questions(self, projects: List[str], count: int) -> List[str]:
        """Generate exactly 2 technical questions per project"""
        if not projects or count <= 0:
            return []
        
        questions = []
        num_projects = count // 2  # Since we need 2 questions per project
        selected_projects = projects[:num_projects]
        
        for project in selected_projects:
            clean_project = self.clean_project_name(project)
            
            # Generate exactly 2 different technical questions per project
            used_templates = []
            for _ in range(2):
                available_templates = [t for t in self.question_templates['projects'] if t not in used_templates]
                if not available_templates:
                    available_templates = self.question_templates['projects']
                
                template = random.choice(available_templates)
                used_templates.append(template)
                question = template.format(project=clean_project)
                questions.append(question)
        
        return questions
    
    def generate_education_questions(self, education_text: str, count: int) -> List[str]:
        """Generate questions based on education"""
        if not education_text or count <= 0:
            return []
        
        degrees = self.extract_degree_info(education_text)
        if not degrees:
            return []
        
        questions = []
        for i in range(min(count, len(degrees))):
            degree = degrees[i % len(degrees)]
            template = random.choice(self.question_templates['education'])
            question = template.format(degree=degree)
            questions.append(question)
        
        return questions
    
    def generate_soft_skill_questions(self, count: int) -> List[str]:
        """Generate soft skill questions"""
        if count <= 0:
            return []
        
        questions = random.sample(self.question_templates['soft_skills'], min(count, len(self.question_templates['soft_skills'])))
        return questions
    
    def generate_questions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate exactly 10 tailored interview questions"""
        all_questions = []
        
        skills = analysis_result.get('skills', [])
        experience = analysis_result.get('experience', '')
        projects = analysis_result.get('projects', [])
        education = analysis_result.get('education', '')
        
        # Determine question distribution based on available content
        total_questions = 10
        
        # STRICT REQUIREMENT: Exactly 2 technical questions per project
        project_questions = 0
        if projects:
            project_questions = len(projects) * 2  # Exactly 2 per project, no max limit
        
        # Distribute remaining questions
        remaining = max(0, total_questions - project_questions)
        
        # If projects take more than 10 questions, limit to first 5 projects (10 questions)
        if project_questions > 10:
            projects = projects[:5]  # Limit to 5 projects
            project_questions = 10
            remaining = 0
        
        # Skills get priority for remaining questions
        skill_questions = min(len(skills), max(0, remaining // 2)) if skills and remaining > 0 else 0
        remaining -= skill_questions
        
        # Experience questions
        experience_questions = min(2, remaining // 2) if experience and remaining > 0 else 0
        remaining -= experience_questions
        
        # Education questions
        education_questions = min(1, remaining) if education and remaining > 0 else 0
        remaining -= education_questions
        
        # Soft skills fill the rest
        soft_skill_questions = remaining
        
        # Generate questions for each category
        if project_questions > 0:
            all_questions.extend(self.generate_project_questions(projects, project_questions))
        
        if skill_questions > 0:
            all_questions.extend(self.generate_skill_questions(skills, skill_questions))
        
        if experience_questions > 0:
            all_questions.extend(self.generate_experience_questions(experience, experience_questions))
        
        if education_questions > 0:
            all_questions.extend(self.generate_education_questions(education, education_questions))
        
        if soft_skill_questions > 0:
            all_questions.extend(self.generate_soft_skill_questions(soft_skill_questions))
        
        # Ensure we have exactly 10 questions
        if len(all_questions) < 10:
            # Add more soft skill questions if needed
            additional_needed = 10 - len(all_questions)
            additional_soft = self.generate_soft_skill_questions(additional_needed)
            all_questions.extend(additional_soft)
        elif len(all_questions) > 10:
            # Trim to exactly 10 questions, preserving project questions
            all_questions = all_questions[:10]
        
        # Do NOT shuffle to maintain project question grouping
        return all_questions
