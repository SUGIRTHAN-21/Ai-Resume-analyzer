import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from resume_analyzer import ResumeAnalyzer
from quiz_generator import QuizGenerator

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    """Handle resume upload and analysis"""
    try:
        # Check if file was uploaded
        if 'resume' not in request.files:
            return jsonify({
                'error': 'No file uploaded. Please select a PDF file.',
                'type': 'upload_error'
            }), 400
        
        file = request.files['resume']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({
                'error': 'No file selected. Please choose a PDF file.',
                'type': 'upload_error'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type. Only PDF files are supported.',
                'type': 'validation_error'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Initialize analyzers
        resume_analyzer = ResumeAnalyzer()
        quiz_generator = QuizGenerator()
        
        # Extract and analyze resume
        analysis_result = resume_analyzer.analyze_resume(file_path)
        
        if not analysis_result['is_valid']:
            # Clean up uploaded file
            os.remove(file_path)
            return jsonify({
                'error': analysis_result['error_message'],
                'type': 'validation_error'
            }), 400
        
        # Generate interview questions
        questions = quiz_generator.generate_questions(analysis_result)
        
        # Clean up uploaded file after processing
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'questions': questions
        })
        
    except Exception as e:
        logging.error(f"Error processing resume: {str(e)}")
        # Clean up file if it exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({
            'error': 'An error occurred while processing your resume. Please try again.',
            'type': 'processing_error'
        }), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'error': 'File too large. Maximum file size is 16MB.',
        'type': 'size_error'
    }), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
