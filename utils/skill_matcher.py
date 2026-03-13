"""
Skill Matcher Module
Compares resume text with job skills requirements
"""

import json
import os


def load_job_skills(skills_file_path="data/skills.json"):
    """
    Load job skills from the skills.json file.
    
    Args:
        skills_file_path (str): Path to the skills.json file
        
    Returns:
        dict: Dictionary containing job roles and skills
        
    Raises:
        FileNotFoundError: If skills.json file doesn't exist
        json.JSONDecodeError: If skills.json is not valid JSON
    """
    try:
        with open(skills_file_path, 'r') as file:
            skills_data = json.load(file)
        return skills_data
    except FileNotFoundError:
        raise FileNotFoundError(f"Skills file not found: {skills_file_path}")
    except json.JSONDecodeError:
        raise json.JSONDecodeError("Invalid JSON format in skills file", "", 0)


def get_all_skills_list(skills_data):
    """
    Extract all skills from the skills data.
    
    Args:
        skills_data (dict): Dictionary containing job skills
        
    Returns:
        list: List of all unique skills
    """
    all_skills = []
    
    # Get skills from job roles
    if 'job_roles' in skills_data:
        for role_name, role_data in skills_data['job_roles'].items():
            if 'required_skills' in role_data:
                all_skills.extend(role_data['required_skills'])
            if 'nice_to_have' in role_data:
                all_skills.extend(role_data['nice_to_have'])
    
    # Get skills from technical skills
    if 'technical_skills' in skills_data:
        for category, skills_list in skills_data['technical_skills'].items():
            all_skills.extend(skills_list)
    
    # Remove duplicates and return
    return list(set(all_skills))


def extract_skills_from_text(resume_text, skills_list):
    """
    Find which skills from the skills list are present in the resume text.
    
    Args:
        resume_text (str): The resume text (already in lowercase)
        skills_list (list): List of skills to search for
        
    Returns:
        list: List of skills found in the resume text
    """
    found_skills = []
    
    # Convert resume text to lowercase for case-insensitive matching
    resume_text_lower = resume_text.lower()
    
    # Check each skill
    for skill in skills_list:
        skill_lower = skill.lower()
        
        # Use simple word matching
        if skill_lower in resume_text_lower:
            found_skills.append(skill)
    
    # Remove duplicates
    found_skills = list(set(found_skills))
    
    return found_skills


def compare_resume_with_job(resume_text, job_description, skills_data):
    """
    Compare resume text with job description to find matching and missing skills.
    
    Args:
        resume_text (str): Extracted text from resume (in lowercase)
        job_description (str): Job description text
        skills_data (dict): Dictionary containing job skills data
        
    Returns:
        dict: Dictionary with matched skills, missing skills, and match percentage
    """
    # Get all skills
    all_skills_list = get_all_skills_list(skills_data)
    
    # Extract skills from resume
    resume_skills = extract_skills_from_text(resume_text, all_skills_list)
    
    # Extract skills from job description
    job_skills = extract_skills_from_text(job_description, all_skills_list)
    
    # Find matched skills (skills in both resume and job description)
    matched_skills = []
    for skill in resume_skills:
        if skill in job_skills:
            matched_skills.append(skill)
    
    # Find missing skills (skills in job description but not in resume)
    missing_skills = []
    for skill in job_skills:
        if skill not in matched_skills:
            missing_skills.append(skill)
    
    # Calculate skill match percentage
    if len(job_skills) > 0:
        match_percentage = (len(matched_skills) / len(job_skills)) * 100
    else:
        match_percentage = 0
    
    # Round to 2 decimal places
    match_percentage = round(match_percentage, 2)
    
    # Return results as dictionary
    result = {
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'job_required_skills': job_skills,
        'resume_skills': resume_skills,
        'matched_count': len(matched_skills),
        'missing_count': len(missing_skills),
        'total_job_skills': len(job_skills),
        'match_percentage': match_percentage
    }
    
    return result


def match_skills(resume_text, job_description):
    """
    Main function to match resume skills with job requirements.
    
    Args:
        resume_text (str): Extracted resume text (in lowercase)
        job_description (str): Job description text
        
    Returns:
        dict: Results with matched skills, missing skills, and match percentage
    """
    try:
        # Load skills data
        skills_data = load_job_skills()
        
        # Compare resume with job
        results = compare_resume_with_job(resume_text, job_description, skills_data)
        
        return results
    
    except Exception as e:
        raise Exception(f"Error matching skills: {e}")


# Example usage (uncomment to test)
# if __name__ == "__main__":
#     try:
#         # Load skills
#         skills = load_job_skills()
#         
#         # Example resume and job description
#         resume = "I have experience with python, javascript, react, and docker. I also know SQL and REST APIs."
#         job_desc = "Required skills: Python, JavaScript, React, Docker, Kubernetes, AWS, SQL"
#         
#         # Compare
#         results = match_skills(resume, job_desc)
#         
#         # Display results
#         print("Matched Skills:", results['matched_skills'])
#         print("Missing Skills:", results['missing_skills'])
#         print("Match Percentage:", results['match_percentage'], "%")
#     except Exception as e:
#         print(f"Error: {e}")
