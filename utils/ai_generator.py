import requests
import streamlit as st
import json
import time
import re

def generate_job_profile(role_name, job_level, role_purpose, benchmark_info):
    """Generate AI-powered job profile using OpenRouter with robust error handling"""
    
    # First, check if AI features are enabled and credentials exist
    try:
        ai_enabled = st.secrets.get("ai", {}).get("ENABLE_AI_FEATURES", True)
        api_key = st.secrets.get("ai", {}).get("OPENROUTER_API_KEY", "")
        api_url = st.secrets.get("ai", {}).get("OPENROUTER_API_URL", "")
        
        if not ai_enabled or not api_key or not api_url:
            return get_enhanced_fallback_profile(role_name, job_level, role_purpose, benchmark_info)
            
    except Exception as config_error:
        return get_enhanced_fallback_profile(role_name, job_level, role_purpose, benchmark_info)

    prompt = f"""
    Create a comprehensive job profile for the following position:

    POSITION: {role_name}
    LEVEL: {job_level}
    PURPOSE: {role_purpose}
    CONTEXT: Based on analysis of {benchmark_info}

    Provide the response in this exact format without using ANY asterisks (*) or markdown formatting:

    JOB REQUIREMENTS:
    • [List 5-7 specific technical requirements]
    • [Include both hard and soft skills]
    • [Focus on measurable competencies]

    JOB DESCRIPTION:
    [2-3 paragraph description of responsibilities, impact, and key objectives]

    KEY COMPETENCIES:
    • [List 4-6 core competencies]
    • [Include both technical and behavioral competencies]
    • [Make them specific and actionable]

    CRITICAL: DO NOT USE ASTERISKS (*) ANYWHERE IN THE RESPONSE. Use bullet points (•) only for lists.
    """
    
    try:
        with st.spinner("🤖 Generating AI-powered profile..."):
            # Try multiple available models
            models_to_try = [
                "google/gemini-pro",  # Free tier available
                "meta-llama/llama-3-70b-instruct",  # Free tier available
                "anthropic/claude-3-haiku",  # Alternative Claude model
                "openai/gpt-3.5-turbo",  # Widely available
            ]
            
            for model in models_to_try:
                try:
                    response = requests.post(
                        api_url,
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "HTTP-Referer": "https://neural-match.streamlit.app",
                            "X-Title": "Neural Match AI Talent App",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 1500,
                            "temperature": 0.7
                        },
                        timeout=45
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if "choices" in result and len(result["choices"]) > 0:
                            content = result["choices"][0]["message"]["content"]
                            # Clean ALL asterisks from the content
                            cleaned_content = clean_asterisks(content)
                            return cleaned_content
                    
                    # Silent fail - just try next model without showing warnings
                    continue
                        
                except Exception as model_error:
                    # Silent fail - just try next model without showing errors
                    continue
            
            # If all models fail, use fallback without showing error
            return get_enhanced_fallback_profile(role_name, job_level, role_purpose, benchmark_info)
                
    except Exception as e:
        # Silent fail - use fallback without showing error
        return get_enhanced_fallback_profile(role_name, job_level, role_purpose, benchmark_info)

def clean_asterisks(text):
    """Remove all asterisks from text comprehensively"""
    if not text:
        return ""
    
    # Remove single asterisks
    text = text.replace('*', '')
    
    # Remove patterns like **text** (bold markdown)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    
    # Remove patterns like * text (bullet points)
    text = re.sub(r'^\s*\*\s+', '• ', text, flags=re.MULTILINE)
    
    # Remove any remaining asterisk patterns
    text = re.sub(r'\*+', '', text)
    
    # Ensure clean bullet points
    text = text.replace('•', '•')  # This ensures consistent bullet character
    
    return text

def get_enhanced_fallback_profile(role_name, job_level, role_purpose, benchmark_info):
    """Provide comprehensive fallback profile when AI is unavailable"""
    
    level_specific = {
        "Junior": "entry-level position focusing on learning and development under supervision",
        "Middle": "mid-level role with independent responsibility and specialized contributions", 
        "Senior": "senior role with strategic impact, mentorship, and complex problem-solving",
        "Lead": "leadership position with team management, decision-making, and project oversight",
        "Principal": "expert-level role with organizational influence, innovation, and thought leadership"
    }
    
    level_desc = level_specific.get(job_level, "professional role")
    
    # More specific requirements based on role type
    if any(keyword in role_name.lower() for keyword in ['strategy', 'business', 'manager']):
        role_specific_reqs = [
            "Strong business acumen and strategic thinking",
            "Experience with market analysis and competitive intelligence",
            "Stakeholder management and executive communication skills",
            "Data-driven decision making and performance metrics",
            "Project management and cross-functional leadership"
        ]
    elif any(keyword in role_name.lower() for keyword in ['tech', 'developer', 'engineer', 'data']):
        role_specific_reqs = [
            "Technical expertise in relevant programming languages/tools",
            "System design and architecture knowledge",
            "Problem-solving and debugging capabilities",
            "Agile methodology and software development lifecycle",
            "Technical documentation and code quality standards"
        ]
    else:
        role_specific_reqs = [
            "Domain expertise in relevant field",
            "Analytical and critical thinking skills",
            "Excellent communication and presentation abilities",
            "Project management and organizational skills",
            "Stakeholder engagement and relationship building"
        ]
    
    requirements_text = "\n".join([f"• {req}" for req in role_specific_reqs])
    
    profile_content = f"""
    JOB REQUIREMENTS:
    {requirements_text}
    • Minimum 3+ years of relevant professional experience
    • Bachelor's degree in related field or equivalent practical experience
    • Strong collaboration and teamworking capabilities
    • Adaptability and continuous learning mindset

    JOB DESCRIPTION:
    The {role_name} ({job_level}) is a {level_desc} primarily responsible for {role_purpose.lower()}. This position requires a professional who can demonstrate strong technical and interpersonal capabilities while contributing significantly to team objectives and organizational goals.
    
    Key responsibilities include strategic planning, execution of key initiatives, collaboration with cross-functional teams, and driving measurable results. The role demands a balance of technical expertise, business understanding, and leadership qualities to successfully navigate complex challenges and deliver value.

    KEY COMPETENCIES:
    • Technical proficiency and domain expertise
    • Analytical thinking and problem-solving capabilities
    • Strategic planning and execution excellence
    • Stakeholder management and communication skills
    • Leadership and team collaboration
    • Innovation and continuous improvement mindset
    • Results orientation and accountability
    """
    
    return clean_asterisks(profile_content)

def parse_ai_profile(ai_content):
    """Parse AI-generated content into structured sections with improved error handling"""
    sections = {
        "requirements": "",
        "description": "", 
        "competencies": ""
    }
    
    try:
        # Clean all asterisks from the content first
        cleaned_content = clean_asterisks(ai_content)
        
        # Check if content follows our expected format
        if "JOB REQUIREMENTS:" in cleaned_content:
            # Parse AI-generated content
            content = cleaned_content
            
            # Extract requirements
            if "JOB REQUIREMENTS:" in content and "JOB DESCRIPTION:" in content:
                requirements_section = content.split("JOB REQUIREMENTS:")[1].split("JOB DESCRIPTION:")[0].strip()
                sections["requirements"] = format_section(requirements_section)
            
            # Extract description
            if "JOB DESCRIPTION:" in content and "KEY COMPETENCIES:" in content:
                description_section = content.split("JOB DESCRIPTION:")[1].split("KEY COMPETENCIES:")[0].strip()
                sections["description"] = format_section(description_section)
            elif "JOB DESCRIPTION:" in content:
                description_section = content.split("JOB DESCRIPTION:")[1].strip()
                sections["description"] = format_section(description_section)
            
            # Extract competencies
            if "KEY COMPETENCIES:" in content:
                competencies_section = content.split("KEY COMPETENCIES:")[1].strip()
                sections["competencies"] = format_section(competencies_section)
                
        else:
            # Use the entire content as description for fallback
            sections["description"] = format_section(cleaned_content)
            
        return sections
        
    except Exception as e:
        sections["description"] = format_section(clean_asterisks(ai_content))
        return sections

def format_section(content):
    """Format section content for better readability"""
    if not content:
        return ""
    
    # Clean any remaining asterisks and format with bullet points
    cleaned_content = clean_asterisks(content)
    
    # Convert various bullet formats to consistent bullet points
    cleaned_content = re.sub(r'^[\s\-]*([•·◦])?\s*', '• ', cleaned_content, flags=re.MULTILINE)
    
    # Add proper line breaks for markdown
    formatted = cleaned_content.replace('\n', '  \n')
    
    return formatted