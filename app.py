"""
AI Resume Analyzer - Main Flask Application
Analyzes resumes and matches skills with job requirements
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import re
from datetime import datetime
from werkzeug.utils import secure_filename

# Import our custom modules
from utils.resume_parser import extract_text_from_resume
from utils.skill_matcher import match_skills
from utils.ats_calculator import calculate_ats_score


# Create Flask application
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_keywords(text, count=15):
    """Extract important keywords from text"""
    # Common action verbs and technical keywords
    keywords = []
    action_verbs = [
        'developed', 'designed', 'implemented', 'managed', 'led', 'created',
        'built', 'analyzed', 'improved', 'optimized', 'coordinated', 'directed',
        'collaborated', 'established', 'increased', 'reduced', 'achieved',
        'maintained', 'supervised', 'trained', 'mentored', 'delivered'
    ]
    
    text_lower = text.lower()
    for verb in action_verbs:
        if verb in text_lower:
            keywords.append(verb.capitalize())
    
    # Extract capitalized words (potential company/tech names)
    capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    keywords.extend(capitalized[:10])
    
    # Remove duplicates and return top N
    keywords = list(dict.fromkeys(keywords))
    return keywords[:count]


def generate_improvement_tips(resume_text, ats_results, skill_results):
    """Generate detailed improvement tips based on analysis"""
    tips = []
    
    # Keyword-based tips
    if ats_results.get('keyword_count', 0) < 10:
        tips.append({
            'priority': 'high',
            'title': 'Add More Action Verbs',
            'description': 'Include action verbs like "developed", "managed", "led" to make your achievements stand out.',
            'impact': 'Improves ATS score by up to 15%'
        })
    
    # Section-based tips
    sections_present = ats_results.get('sections_present', {})
    missing_sections = [s.replace('_', ' ').title() for s, present in sections_present.items() if not present]
    if missing_sections:
        tips.append({
            'priority': 'high',
            'title': 'Add Missing Resume Sections',
            'description': f'Add these sections: {", ".join(missing_sections)}',
            'impact': 'Improves ATS score by up to 20%'
        })
    
    # Skill gap tips
    missing_skills = skill_results.get('missing_skills', [])[:3]
    if missing_skills:
        tips.append({
            'priority': 'medium',
            'title': 'Learn High-Demand Skills',
            'description': f'Focus on: {", ".join(missing_skills)}. These are crucial for your target role.',
            'impact': f'Can increase job match by up to 30%'
        })
    
    # Length-based tips
    words = len(resume_text.split())
    if words < 200:
        tips.append({
            'priority': 'medium',
            'title': 'Expand Your Resume',
            'description': 'Add more details about your accomplishments, projects, and responsibilities.',
            'impact': 'Improves readability and ATS compatibility'
        })
    elif words > 1000:
        tips.append({
            'priority': 'low',
            'title': 'Condense Your Resume',
            'description': 'Aim for 200-600 words. Remove unnecessary details.',
            'impact': 'Improves readability'
        })
    
    # Contact info tips
    if '@' not in resume_text:
        tips.append({
            'priority': 'high',
            'title': 'Add Contact Information',
            'description': 'Include your email address and phone number.',
            'impact': 'Essential for recruiters to reach you'
        })
    
    return tips


def load_job_roles():
    """Load available job roles from skills.json"""
    try:
        with open('data/skills.json', 'r') as f:
            data = json.load(f)
            return list(data.get('job_roles', {}).keys())
    except:
        return []


@app.route('/')
def index():
    """Display homepage with upload form"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_resume():
    """
    Handle resume upload and analysis
    
    Expected form data:
    - resume: Resume file (PDF or DOCX)
    - job_description: Job description text
    """
    
    try:
        # Validate request has resume file
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        # Validate request has job description
        if 'job_description' not in request.form:
            return jsonify({'error': 'No job description provided'}), 400
        
        # Get file from request
        resume_file = request.files['resume']
        job_description = request.form.get('job_description', '').strip()
        
        # Validate file was selected
        if resume_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file is allowed type
        if not allowed_file(resume_file.filename):
            return jsonify({'error': 'Only PDF and DOCX files are allowed'}), 400
        
        # Validate job description is not empty
        if not job_description:
            return jsonify({'error': 'Job description cannot be empty'}), 400
        
        # Save resume file
        filename = secure_filename(resume_file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        resume_file.save(filepath)
        
        # ===== STEP 1: Extract text from resume =====
        resume_text = extract_text_from_resume(filepath)
        
        # ===== STEP 2: Match skills =====
        skill_results = match_skills(resume_text, job_description)
        
        matched_skills = skill_results['matched_skills']
        missing_skills = skill_results['missing_skills']
        match_percentage = skill_results['match_percentage']
        
        # ===== STEP 3: Calculate ATS score =====
        ats_results = calculate_ats_score(resume_text, skill_match_percentage=match_percentage)
        ats_score = ats_results['ats_score']
        
        # ===== STEP 4: Calculate overall resume score =====
        resume_score = (match_percentage * 0.6) + (ats_score * 0.4)
        resume_score = round(resume_score, 2)
        
        # ===== STEP 5: Determine job suitability =====
        if resume_score >= 80:
            suitability = "Excellent - Highly Suitable"
            status_color = "success"
        elif resume_score >= 60:
            suitability = "Good - Suitable"
            status_color = "info"
        elif resume_score >= 40:
            suitability = "Fair - Moderately Suitable"
            status_color = "warning"
        else:
            suitability = "Poor - Not Very Suitable"
            status_color = "danger"
        
        # ===== STEP 6: Generate improvement suggestions =====
        suggestions = []
        
        # Suggestion for missing skills
        if missing_skills:
            top_missing = missing_skills[:3]
            suggestions.append(f"Learn the following skills: {', '.join(top_missing)}")
        
        # Suggestion for resume length
        words = len(resume_text.split())
        if words < 200:
            suggestions.append("Expand your resume - it should be at least 200 words")
        elif words > 1000:
            suggestions.append("Shorten your resume - aim for under 1000 words")
        
        # Suggestion for keywords
        sections_present = ats_results['sections_present']
        missing_sections = [s for s, present in sections_present.items() if not present]
        if missing_sections:
            suggestions.append(f"Add missing sections: {', '.join(missing_sections)}")
        
        # Suggestion for contact info
        if '@' not in resume_text:
            suggestions.append("Add your email address to the resume")
        
        # ===== STEP 7: Extract keywords for highlighting =====
        keywords = extract_keywords(resume_text)
        
        # ===== STEP 8: Generate detailed improvement tips =====
        improvement_tips = generate_improvement_tips(resume_text, ats_results, skill_results)
        
        # ===== STEP 9: Prepare visualization data for charts =====
        chart_data = {
            'skill_breakdown': {
                'matched': len(matched_skills),
                'missing': len(missing_skills)
            },
            'score_breakdown': {
                'skill_match': round(match_percentage, 1),
                'ats': round(ats_score, 1),
                'resume': round(resume_score, 1)
            },
            'ats_components': {
                'length': round(ats_results.get('components', {}).get('length_score', 0), 1),
                'sections': round(ats_results.get('components', {}).get('section_score', 0), 1),
                'keywords': round(ats_results.get('components', {}).get('keyword_score', 0), 1),
                'contact': round(ats_results.get('components', {}).get('contact_info_score', 0), 1)
            }
        }
        
        # ===== STEP 10: Prepare response =====
        result = {
            'filename': filename,
            'resume_score': resume_score,
            'ats_score': ats_score,
            'skill_match_percentage': match_percentage,
            'suitability': suitability,
            'status_color': status_color,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'suggestions': suggestions,
            'keywords': keywords,
            'improvement_tips': improvement_tips,
            'chart_data': chart_data,
            'word_count': words,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save report to file
        report_path = os.path.join(REPORTS_FOLDER, filename + '.json')
        with open(report_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        return jsonify(result), 200
    
    except FileNotFoundError as e:
        return jsonify({'error': f'File error: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': f'Invalid file format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error processing resume: {str(e)}'}), 500


@app.route('/result/<filename>')
def result(filename):
    """Display analysis results for a resume"""
    try:
        # Load report from file
        report_path = os.path.join(REPORTS_FOLDER, filename + '.json')
        
        if not os.path.exists(report_path):
            return render_template('index.html'), 404
        
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        return render_template('result.html', result=report_data)
    
    except Exception as e:
        return render_template('index.html'), 404


@app.route('/dashboard')
def dashboard():
    """Display dashboard with all analyzed resumes"""
    try:
        reports = []
        
        # Load all reports from reports folder
        if os.path.exists(REPORTS_FOLDER):
            for filename in os.listdir(REPORTS_FOLDER):
                if filename.endswith('.json'):
                    filepath = os.path.join(REPORTS_FOLDER, filename)
                    with open(filepath, 'r') as f:
                        report_data = json.load(f)
                        reports.append(report_data)
        
        # Sort by timestamp (newest first)
        reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return render_template('dashboard.html', reports=reports)
    
    except Exception as e:
        return render_template('dashboard.html', reports=[])


@app.route('/api/download/<filename>')
def download_report(filename):
    """Download a report as JSON file"""
    try:
        report_path = os.path.join(REPORTS_FOLDER, filename + '.json')
        
        if not os.path.exists(report_path):
            return jsonify({'error': 'Report not found'}), 404
        
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        return jsonify(report_data), 200
    
    except Exception as e:
        return jsonify({'error': f'Error downloading report: {str(e)}'}), 500


@app.route('/compare')
def compare():
    """Display page for comparing multiple job roles"""
    job_roles = load_job_roles()
    return render_template('compare.html', job_roles=job_roles)


@app.route('/api/compare-roles', methods=['POST'])
def compare_roles():
    """Compare resume against multiple job roles"""
    try:
        data = request.get_json()
        
        if 'resume_file' not in data or 'job_roles' not in data:
            return jsonify({'error': 'Missing required data'}), 400
        
        resume_file = data['resume_file']
        selected_roles = data['job_roles']
        
        # Load existing resume text from uploaded file
        filepath = os.path.join(UPLOAD_FOLDER, resume_file)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Resume file not found'}), 400
        
        resume_text = extract_text_from_resume(filepath)
        
        # Analyze against each selected job role
        comparison_results = []
        
        try:
            with open('data/skills.json', 'r') as f:
                skills_data = json.load(f)
                job_roles_data = skills_data.get('job_roles', {})
        except:
            return jsonify({'error': 'Skills database not found'}), 500
        
        for role in selected_roles:
            if role not in job_roles_data:
                continue
            
            # Create job description from role requirements
            role_skills = job_roles_data[role].get('required_skills', [])
            job_description = f"Requirements: {', '.join(role_skills)}"
            
            # Calculate match
            skill_match = match_skills(resume_text, job_description)
            ats_score_result = calculate_ats_score(resume_text, skill_match['match_percentage'])
            
            match_percentage = skill_match['match_percentage']
            ats_score = ats_score_result['ats_score']
            resume_score = (match_percentage * 0.6) + (ats_score * 0.4)
            
            comparison_results.append({
                'role': role.replace('_', ' ').title(),
                'resume_score': round(resume_score, 2),
                'skill_match': round(match_percentage, 2),
                'ats_score': round(ats_score, 2),
                'matched_skills': skill_match['matched_skills'][:5],
                'missing_skills': skill_match['missing_skills'][:3]
            })
        
        # Sort by resume score
        comparison_results.sort(key=lambda x: x['resume_score'], reverse=True)
        
        return jsonify({
            'comparison': comparison_results,
            'best_match': comparison_results[0]['role'] if comparison_results else None
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Comparison error: {str(e)}'}), 500


@app.route('/api/generate-report/<filename>')
def generate_report(filename):
    """Generate a detailed analysis report as downloadable file"""
    try:
        # Load existing report
        report_path = os.path.join(REPORTS_FOLDER, filename + '.json')
        if not os.path.exists(report_path):
            return jsonify({'error': 'Report not found'}), 404
        
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        # Create detailed HTML report
        html_report = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <title>Resume Analysis Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; color: #333; }}
                    h1 {{ color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
                    h2 {{ color: #764ba2; margin-top: 30px; }}
                    .score {{ font-size: 36px; font-weight: bold; color: #667eea; }}
                    .section {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
                    .skill-tag {{ display: inline-block; padding: 8px 12px; margin: 4px; border-radius: 20px; }}
                    .matched {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                    .missing {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
                    .tip {{ margin: 10px 0; padding: 10px; border-left: 4px solid #667eea; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                    th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                    th {{ background: #667eea; color: white; }}
                </style>
            </head>
            <body>
                <h1>📊 Resume Analysis Report</h1>
                <p><strong>Generated:</strong> {report_data.get('timestamp', 'N/A')}</p>
                
                <h2>Overall Scores</h2>
                <div class="section">
                    <div><strong>Resume Score:</strong> <span class="score">{report_data.get('resume_score', 0)}/100</span></div>
                    <div><strong>ATS Score:</strong> <span class="score">{report_data.get('ats_score', 0)}/100</span></div>
                    <div><strong>Skill Match:</strong> <span class="score">{report_data.get('skill_match_percentage', 0)}%</span></div>
                    <div><strong>Suitability:</strong> {report_data.get('suitability', 'Unknown')}</div>
                </div>
                
                <h2>Matched Skills</h2>
                <div class="section">
                    {''.join([f'<span class="skill-tag matched">✓ {skill}</span>' for skill in report_data.get('matched_skills', [])])}
                </div>
                
                <h2>Missing Skills</h2>
                <div class="section">
                    {''.join([f'<span class="skill-tag missing">✗ {skill}</span>' for skill in report_data.get('missing_skills', [])])}
                </div>
                
                <h2>Improvement Tips</h2>
                <div class="section">
                    {''.join([f'''<div class="tip">
                        <strong>{tip.get("title", "")}</strong> [{tip.get("priority", "").upper()}]<br>
                        {tip.get("description", "")}<br>
                        <em>Impact: {tip.get("impact", "")}</em>
                    </div>''' for tip in report_data.get('improvement_tips', [])])}
                </div>
                
                <h2>Key Keywords Found</h2>
                <div class="section">
                    {''.join([f'<span class="skill-tag matched">{keyword}</span>' for keyword in report_data.get('keywords', [])])}
                </div>
            </body>
        </html>
        """
        
        return html_report, 200, {'Content-Type': 'text/html; charset=utf-8'}
    
    except Exception as e:
        return jsonify({'error': f'Error generating report: {str(e)}'}), 500


@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return render_template('index.html'), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Run Flask development server
    print("Starting AI Resume Analyzer...")
    print("Open your browser at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

