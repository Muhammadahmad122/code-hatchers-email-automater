import google.generativeai as genai
import os
import json

def analyze_pain_points(business_text, business_name, industry):
    """
    Uses Google Gemini (1.5 Flash) to analyze text for operational pain points.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[!] GOOGLE_API_KEY not found. Cannot analyze.")
        return None
        
    genai.configure(api_key=api_key)
    
    # Use 1.5 Flash for speed and large context
    model = genai.GenerativeModel('gemini-1.5-flash') 
    
    prompt = f"""
    You are an expert Business Analyst Agent.
    
    Analyze the following metadata and website text for a business found online.
    Identify ONE specific, high-friction operational bottleneck that can be solved with a custom Python automation script.
    
    Business: {business_name}
    Industry: {industry}
    Website Text Context:
    {business_text}
    
    Task:
    1. Identify a Pain Point (e.g., "Missed phone calls", "Manual inventory tracking", "Slow email response").
    2. Quote evidence if available.
    3. Assign a confidence score (0.0 to 1.0).
    
    Output strictly in JSON format with no preamble:
    {{
        "pain_point": "The specific operational problem",
        "evidence": "Quote or signal from text",
        "confidence": 0.8
    }}
    """
    
    try:
        print(f"[*] Analyzing pain points for {business_name} using Gemini 1.5 Flash...")
        response = model.generate_content(prompt)
        text = response.text
        
        # Parse JSON
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = text[start:end]
            return json.loads(json_str)
        else:
            return {"pain_point": "General operational inefficiency", "evidence": "Inferred from industry standards", "confidence": 0.5}
            
    except Exception as e:
        print(f"Error in pain point analysis: {e}")
        return None
