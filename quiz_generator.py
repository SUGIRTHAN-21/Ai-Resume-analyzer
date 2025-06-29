import re
import random
from typing import List, Dict, Any

class QuizGenerator:
    """Generates tailored interview questions based on resume analysis"""
    
    def __init__(self):
        # Diverse question pools for generating unique questions
        self.question_generators = {
            'technical_deep_dive': [
                "Compare {skill1} and {skill2} - when would you choose one over the other?",
                "If you had to teach {skill} to a junior developer, what would be your approach?",
                "What's the most complex problem you've solved using {skill}?",
                "How do you debug issues when working with {skill}?",
                "What are the performance considerations when using {skill} in production?",
                "Describe the learning curve you experienced with {skill}.",
                "What libraries or frameworks complement {skill} in your workflow?"
            ],
            'project_specifics': [
                "What inspired you to build {project}?",
                "How did you validate the requirements for {project}?",
                "What was your testing strategy for {project}?",
                "How did you handle data management in {project}?",
                "What performance optimizations did you implement in {project}?",
                "How did you ensure user experience in {project}?",
                "What security considerations did you address in {project}?"
            ],
            'problem_solving': [
                "Describe a time when you had to learn a new technology quickly for a project.",
                "How do you approach breaking down complex technical problems?",
                "Tell me about a bug that took you the longest to fix.",
                "How do you balance technical debt with feature development?",
                "Describe your process for code reviews and quality assurance.",
                "How do you handle conflicting technical requirements?",
                "What's your approach to choosing between multiple technical solutions?"
            ],
            'industry_knowledge': [
                "What emerging technologies in your field excite you the most?",
                "How do you evaluate new tools before adopting them in projects?",
                "What's your perspective on current industry best practices?",
                "How do you contribute to the developer community?",
                "What resources do you use to stay current with technology trends?",
                "How do you approach technical documentation and knowledge sharing?",
                "What's your experience with agile development methodologies?"
            ],
            'practical_scenarios': [
                "How would you optimize a slow-performing application?",
                "Describe your approach to building scalable systems.",
                "How do you handle version control and collaboration in team projects?",
                "What's your strategy for handling production incidents?",
                "How do you approach API design and integration?",
                "Describe your experience with cloud platforms and deployment.",
                "How do you ensure accessibility in your applications?"
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
    
    def generate_unique_questions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate 10 completely unique and diverse interview questions"""
        skills = analysis_result.get('skills', [])
        projects = analysis_result.get('projects', [])
        
        all_questions = []
        used_question_types = set()
        
        # Generate exactly 2 unique questions per project
        if projects:
            for project in projects[:3]:  # Max 3 projects for 6 questions
                project_questions = self.generate_diverse_project_questions(project, used_question_types)
                all_questions.extend(project_questions[:2])  # Exactly 2 per project
        
        # Fill remaining slots with diverse technical and general questions
        remaining_slots = 10 - len(all_questions)
        
        # Generate diverse skill-based questions
        if skills and remaining_slots > 0:
            skill_questions = self.generate_diverse_skill_questions(skills, remaining_slots // 2, used_question_types)
            all_questions.extend(skill_questions)
            remaining_slots = 10 - len(all_questions)
        
        # Fill any remaining slots with problem-solving and industry questions
        if remaining_slots > 0:
            general_questions = self.generate_diverse_general_questions(remaining_slots, used_question_types)
            all_questions.extend(general_questions)
        
        # Ensure exactly 10 questions
        return all_questions[:10]
    
    def generate_diverse_project_questions(self, project: str, used_types: set) -> List[str]:
        """Generate 2 completely different questions for a project"""
        questions = []
        available_categories = [cat for cat in ['project_specifics', 'technical_deep_dive', 'problem_solving'] 
                               if cat not in used_types]
        
        if not available_categories:
            available_categories = ['project_specifics', 'problem_solving']
        
        # Select 2 different question categories
        selected_categories = random.sample(available_categories, min(2, len(available_categories)))
        
        for category in selected_categories:
            question_templates = self.question_generators[category]
            template = random.choice(question_templates)
            
            if '{project}' in template:
                question = template.format(project=project)
            else:
                # For general templates, prefix with project context
                question = f"Regarding your {project} project: {template}"
            
            questions.append(question)
            used_types.add(category)
        
        return questions
    
    def generate_diverse_skill_questions(self, skills: List[str], count: int, used_types: set) -> List[str]:
        """Generate diverse skill-based questions"""
        questions = []
        
        for i in range(min(count, len(skills))):
            skill = skills[i]
            
            # Choose from available question types
            available_categories = [cat for cat in ['technical_deep_dive', 'practical_scenarios'] 
                                   if cat not in used_types or len(used_types) > 3]
            
            if available_categories:
                category = random.choice(available_categories)
                templates = self.question_generators[category]
                template = random.choice(templates)
                
                if '{skill}' in template:
                    question = template.format(skill=skill)
                elif '{skill1}' in template and len(skills) > 1:
                    skill2 = random.choice([s for s in skills if s != skill])
                    question = template.format(skill1=skill, skill2=skill2)
                else:
                    question = f"Considering your {skill} experience: {template}"
                
                questions.append(question)
                used_types.add(category)
        
        return questions
    
    def generate_diverse_general_questions(self, count: int, used_types: set) -> List[str]:
        """Generate diverse general interview questions"""
        questions = []
        
        available_categories = [cat for cat in ['problem_solving', 'industry_knowledge', 'practical_scenarios'] 
                               if cat not in used_types]
        
        if not available_categories:
            available_categories = ['problem_solving', 'industry_knowledge']
        
        for i in range(count):
            category = available_categories[i % len(available_categories)]
            templates = self.question_generators[category]
            template = random.choice(templates)
            questions.append(template)
            used_types.add(category)
        
        return questions
    
    def generate_questions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Main method to generate questions - calls the new unique generator"""
        return self.generate_unique_questions(analysis_result)
