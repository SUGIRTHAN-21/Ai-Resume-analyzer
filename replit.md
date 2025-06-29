# Resume Analyzer & Interview Question Generator

## Overview

This is a Flask-based web application that analyzes PDF resumes and generates tailored interview questions. The system extracts key information from uploaded resumes including skills, experience, education, and projects, then creates personalized interview questions based on the candidate's background.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **File Processing**: Dual PDF extraction approach using PyMuPDF (fitz) and pdfplumber for maximum compatibility
- **Text Analysis**: Custom pattern matching and natural language processing for resume parsing
- **Session Management**: Flask sessions with configurable secret key
- **File Handling**: Secure file upload with validation and size limits

### Frontend Architecture
- **Templating**: Jinja2 templates with Flask
- **Styling**: Custom CSS with dark theme design
- **JavaScript**: Vanilla JavaScript for client-side interactions
- **UI Components**: File upload interface, loading states, error handling, and results display

### Security Measures
- File type validation (PDF only)
- Secure filename handling with Werkzeug
- File size limits (16MB maximum)
- Proxy fix middleware for deployment compatibility

## Key Components

### 1. Resume Analyzer (`resume_analyzer.py`)
- **Purpose**: Extracts and analyzes text content from PDF resumes
- **Key Features**:
  - Dual PDF extraction methods for reliability
  - Skill categorization (programming, web, database, cloud, tools)
  - Keyword validation for resume quality assessment
  - Text preprocessing and cleaning

### 2. Quiz Generator (`quiz_generator.py`)
- **Purpose**: Creates tailored interview questions based on resume analysis
- **Question Categories**:
  - Technical skills questions
  - Experience-based questions
  - Project-specific questions
  - Soft skills questions
  - Education-related questions
- **Dynamic Content**: Questions are personalized using extracted resume data

### 3. Flask Application (`app.py`)
- **Routes**:
  - `/` - Main application interface
  - `/analyze` - Resume upload and analysis endpoint
- **File Management**: Handles uploads to designated folder with validation
- **Error Handling**: Comprehensive error responses for various failure scenarios

### 4. Frontend Interface
- **Upload Interface**: Drag-and-drop file upload with validation
- **Results Display**: Structured presentation of analysis and questions
- **Responsive Design**: Mobile-friendly interface
- **Loading States**: Visual feedback during processing

## Data Flow

1. **File Upload**: User selects PDF resume file through web interface
2. **Validation**: Client-side and server-side validation of file type and size
3. **Text Extraction**: Dual-method PDF text extraction for maximum compatibility
4. **Content Analysis**: Resume analyzer processes text to extract key information
5. **Question Generation**: Quiz generator creates personalized interview questions
6. **Response Delivery**: Results sent back to frontend as JSON
7. **Display**: Frontend renders analysis results and questions

## External Dependencies

### Python Packages
- **Flask**: Web framework and templating
- **PyMuPDF (fitz)**: Primary PDF text extraction
- **pdfplumber**: Backup PDF text extraction
- **Werkzeug**: Security utilities and file handling

### Frontend Dependencies
- **Font Awesome**: Icon library for UI elements
- **Custom CSS**: No external CSS frameworks used

### File System
- **uploads/**: Directory for temporary file storage during processing
- **static/**: Static assets (CSS, JavaScript)
- **templates/**: HTML template files

## Deployment Strategy

- **Environment Variables**: Configurable session secret key
- **Proxy Support**: ProxyFix middleware for reverse proxy deployments
- **Static Assets**: Served through Flask's static file handling
- **File Management**: Automatic upload directory creation
- **Logging**: Configurable logging for debugging and monitoring

## Changelog

- June 29, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.