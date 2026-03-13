"""
ATS Calculator Module
Calculates ATS (Applicant Tracking System) score for resumes
"""


def count_resume_sections(resume_text):
    """
    Count how many important resume sections are present.
    
    Args:
        resume_text (str): The resume text in lowercase
        
    Returns:
        dict: Dictionary with section names and their presence (True/False)
    """
    # Important section keywords to search for
    sections = {
        'education': ['education', 'degree', 'university', 'college', 'bachelors', 'masters'],
        'experience': ['experience', 'work', 'employment', 'position', 'job', 'worked'],
        'projects': ['projects', 'project', 'portfolio', 'built', 'developed', 'created'],
        'skills': ['skills', 'technical', 'proficient', 'expertise', 'competencies']
    }
    
    # Check each section
    section_status = {}
    for section_name, keywords in sections.items():
        found = False
        for keyword in keywords:
            if keyword in resume_text.lower():
                found = True
                break
        section_status[section_name] = found
    
    return section_status


def count_keywords(resume_text):
    """
    Count professional keywords in the resume.
    
    Args:
        resume_text (str): The resume text in lowercase
        
    Returns:
        int: Number of professional keywords found
    """
    # Important professional keywords
    keywords = [
        'achieved', 'managed', 'developed', 'implemented', 'designed',
        'led', 'improved', 'increased', 'reduced', 'created',
        'responsible', 'collaborated', 'organized', 'analyzed', 'built',
        'certified', 'trained', 'demonstrated', 'proficient', 'expertise'
    ]
    
    # Count keywords found
    keyword_count = 0
    for keyword in keywords:
        if keyword in resume_text:
            keyword_count += keyword.count(keyword)  # Count all occurrences
    
    return keyword_count


def calculate_resume_length_score(resume_text):
    """
    Calculate score based on resume length.
    Ideal resume is 200-1000 words.
    
    Args:
        resume_text (str): The resume text
        
    Returns:
        float: Length score (0-100)
    """
    # Count words in resume
    words = resume_text.split()
    word_count = len(words)
    
    # Ideal range: 200-1000 words
    if word_count < 200:
        # Too short, give partial score
        score = (word_count / 200) * 50
    elif word_count <= 1000:
        # In ideal range, full score
        score = 100
    else:
        # Too long, reduce score
        excess_words = word_count - 1000
        score = max(100 - (excess_words / 500 * 30), 30)  # Minimum 30%
    
    return score


def calculate_contact_info_score(resume_text):
    """
    Calculate score based on contact information presence.
    
    Args:
        resume_text (str): The resume text in lowercase
        
    Returns:
        float: Contact info score (0-100)
    """
    score = 0
    
    # Check for email (contains @)
    if '@' in resume_text:
        score += 30
    
    # Check for phone (contains numbers like 123-456-7890 or similar)
    if any(char.isdigit() for char in resume_text):
        score += 30
    
    # Check for location indicators (city, state, country mentions)
    location_keywords = ['city', 'state', 'country', 'address', 'located', 'based']
    for keyword in location_keywords:
        if keyword in resume_text:
            score += 20
            break
    
    # Check for name at top (usually first line has capitalized text)
    lines = resume_text.split('\n')
    if len(lines) > 0 and any(c.isupper() for c in lines[0][:50]):
        score += 20
    
    return min(score, 100)


def calculate_section_score(section_status):
    """
    Calculate score based on resume sections present.
    
    Args:
        section_status (dict): Dictionary with section names and their presence
        
    Returns:
        float: Section score (0-100)
    """
    # Each section is worth 25 points (4 sections total)
    sections_present = sum(1 for present in section_status.values() if present)
    
    # 4 sections = 100 points
    # 3 sections = 75 points
    # 2 sections = 50 points
    # 1 section = 25 points
    # 0 sections = 0 points
    
    score = (sections_present / 4) * 100
    return score


def calculate_keyword_score(keyword_count):
    """
    Calculate score based on professional keywords.
    
    Args:
        keyword_count (int): Number of professional keywords found
        
    Returns:
        float: Keyword score (0-100)
    """
    # Ideal: 10-20 keywords
    # Score is based on keyword frequency
    
    if keyword_count < 5:
        score = (keyword_count / 5) * 50
    elif keyword_count <= 20:
        score = 100
    else:
        # Too many keywords might be keyword stuffing
        excess = keyword_count - 20
        score = max(100 - (excess * 2), 50)
    
    return score


def calculate_skill_match_score(skill_match_percentage):
    """
    Convert skill match percentage to ATS score component.
    
    Args:
        skill_match_percentage (float): Skill match percentage (0-100)
        
    Returns:
        float: Skill match score component (0-100)
    """
    return skill_match_percentage


def calculate_ats_score(resume_text, skill_match_percentage=50):
    """
    Calculate overall ATS score for a resume.
    
    Args:
        resume_text (str): The resume text (ideally in lowercase)
        skill_match_percentage (float): Skill match percentage from skill_matcher (0-100)
        
    Returns:
        dict: Dictionary with ATS score and component breakdown
    """
    
    # Calculate individual component scores
    length_score = calculate_resume_length_score(resume_text)
    contact_score = calculate_contact_info_score(resume_text)
    section_status = count_resume_sections(resume_text)
    section_score = calculate_section_score(section_status)
    keyword_count = count_keywords(resume_text)
    keyword_score = calculate_keyword_score(keyword_count)
    skill_score = calculate_skill_match_score(skill_match_percentage)
    
    # Weight each component
    weights = {
        'length': 0.15,           # 15% - Resume should be appropriate length
        'contact_info': 0.10,     # 10% - Contact information is important
        'sections': 0.20,         # 20% - All sections should be present
        'keywords': 0.20,         # 20% - Professional keywords matter
        'skills': 0.35            # 35% - Skill match is most important
    }
    
    # Calculate weighted score
    total_score = (
        length_score * weights['length'] +
        contact_score * weights['contact_info'] +
        section_score * weights['sections'] +
        keyword_score * weights['keywords'] +
        skill_score * weights['skills']
    )
    
    # Round to 2 decimal places
    total_score = round(total_score, 2)
    
    # Make sure score is between 0 and 100
    total_score = max(0, min(100, total_score))
    
    # Return results
    result = {
        'ats_score': total_score,
        'components': {
            'length_score': round(length_score, 2),
            'contact_info_score': round(contact_score, 2),
            'section_score': round(section_score, 2),
            'keyword_score': round(keyword_score, 2),
            'skill_match_score': round(skill_score, 2)
        },
        'weights': weights,
        'sections_present': section_status,
        'keyword_count': keyword_count
    }
    
    return result


# Example usage (uncomment to test)
# if __name__ == "__main__":
#     # Example resume text
#     resume = """
#     john doe
#     email: john@email.com | phone: 123-456-7890 | located in new york
#     
#     education
#     bachelor's degree in computer science from state university
#     
#     experience
#     senior software engineer at tech company (2020-2026)
#     - developed and implemented new features
#     - managed team of 5 developers
#     - achieved 40% performance improvement
#     
#     skills
#     python, javascript, react, docker, kubernetes, aws, sql
#     
#     projects
#     built an ai resume analyzer - created with python and flask
#     """
#     
#     # Calculate ATS score
#     results = calculate_ats_score(resume, skill_match_percentage=75)
#     
#     print("ATS Score:", results['ats_score'])
#     print("Component Scores:", results['components'])
#     print("Sections Found:", results['sections_present'])
#     print("Keywords Found:", results['keyword_count'])
