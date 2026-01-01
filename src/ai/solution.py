import google.generativeai as genai
import os
import json

def generate_solution_concept(pain_point, business_name, industry):
    """
    Uses Google Gemini (1.5 Flash) to draft a Python-based solution concept.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an expert Solutions Architect.
    
    Task: Create a concept for a custom Python-based AI solution to solve the following pain point.
    
    Business: {business_name} ({industry})
    Pain Point: {pain_point}
    
    Constraints:
    1. Must use Python technologies (FastAPI, OpenCV, Pandas, etc.) and Generative AI / Agentic AI where applicable.
    2. Must be an "On-Demand" or "Agentic" solution.
    3. Title must be business-friendly (e.g., "AI Receptionist", not "Twilio Bot").
    
    Output strictly in JSON with no preamble:
    {{
        "title": "Business friendly title",
        "concept_body": "2-3 sentences explaining how it works and the benefit.",
        "technical_details": "Internal notes on python libs (e.g., Use twilio + openai api)"
    }}
    """
    
    try:
        print(f"[*] Generating solution for {business_name} using Gemini...")
        response = model.generate_content(prompt)
        text = response.text
        
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1:
            return json.loads(text[start:end])
        return None
    except Exception as e:
        print(f"Error generating solution: {e}")
        return None

def validate_solution(solution_data, pain_point):
    """
    Uses Google Gemini API (CTO Persona) to validate the solution.
    returns: (is_valid: bool, feedback: str)
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[!] GOOGLE_API_KEY not found. Skipping validation (Assumption: Valid).")
        return True, "No validation key provided."
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash') 
    
    prompt = f"""
    You are the CTO of Code Hatchers. Review this proposed AI solution.
    
    Pain Point: {pain_point}
    Proposed Title: {solution_data['title']}
    Proposed Concept: {solution_data['concept_body']}
    Technical Notes: {solution_data['technical_details']}
    
    Validation Rules:
    1. Is it technically feasible in Python?
    2. Does the title HIDE backend jargon like "Twilio", "VoIP", "AWS"? (Crucial)
    3. Does it directly address the pain point?
    
    Output strictly in JSON:
    {{
        "valid": true,
        "feedback": "Reason for rejection or approval notes"
    }}
    """
    
    try:
        print("[*] Validating solution with Google Gemini (CTO Persona)...")
        # Try-catch for model name availability, fallback to gemini-pro if needed
        try:
             response = model.generate_content(prompt)
        except:
             model = genai.GenerativeModel('gemini-pro')
             response = model.generate_content(prompt)

        text = response.text
        
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1:
            data = json.loads(text[start:end])
            return data['valid'], data['feedback']
        return False, "Could not parse validation response"
    except Exception as e:
        print(f"Error validating solution: {e}")
        return False, f"Validation error: {e}"
