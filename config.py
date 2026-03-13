"""
Configuration Settings
AI Resume Analyzer Application
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Flask Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.environ.get('FLASK_ENV') == 'development'
TESTING = False

# File Upload Configuration
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'uploads'))
REPORTS_FOLDER = os.environ.get('REPORTS_FOLDER', os.path.join(BASE_DIR, 'reports'))
DATA_FOLDER = os.environ.get('DATA_FOLDER', os.path.join(BASE_DIR, 'data'))

# File restrictions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

# Server Configuration
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5000))

# Database Configuration (for future use)
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///resume_analyzer.db')

# Security Configuration
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Logging Configuration
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')

# Application Settings
APP_TITLE = 'AI Resume Analyzer'
APP_DESCRIPTION = 'Analyze resumes and evaluate candidate suitability for job roles'
APP_VERSION = '1.0.0'

# Skills Configuration
SKILLS_FILE = os.path.join(DATA_FOLDER, 'skills.json')
SUGGESTIONS_FILE = os.path.join(DATA_FOLDER, 'suggestions.json')

# Pagination
ITEMS_PER_PAGE = 20

# ATS Scoring Weights
ATS_WEIGHTS = {
    'contact_info': 0.10,
    'formatting': 0.15,
    'keywords': 0.25,
    'structure': 0.20,
    'content_quality': 0.15,
    'length': 0.10,
    'special_characters': 0.05
}

# Resume Score Weights
RESUME_SCORE_WEIGHTS = {
    'skill_match': 0.60,
    'ats_score': 0.40
}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
