import time
import os
from colorama import Fore, init, Style
from dotenv import load_dotenv

from src.database import init_db, get_engine, get_session, Prospect, Interaction
from src.ai.scraper import scrape_business_data
from src.ai.pain_point import analyze_pain_points
from src.ai.solution import generate_solution_concept, validate_solution
from src.email.outlook import EmailHandler

init(autoreset=True)
load_dotenv()

def main():
    print(Fore.CYAN + "========================================")
    print(Fore.CYAN + "   Code Hatchers Automater v1.3         ")
    print(Fore.CYAN + "========================================")
    
    engine = get_engine()
    init_db(engine)
    session = get_session(engine)
    
    try:
        email_handler = EmailHandler()
    except Exception as e:
        print(Fore.RED + f"[!] Email config error: {e}")
        return

    print(Fore.GREEN + "[*] System Ready. Starting Loop...")
    
    while True:
        try:
            # 1. Process New Prospects
            new_prospects = session.query(Prospect).filter_by(status="NEW").limit(1).all()
            if new_prospects:
                for p in new_prospects:
                    process_new_prospect(p, session, email_handler)
            else:
                print(Fore.YELLOW + "[*] No new prospects in queue.")
                
            # 2. Check for Replies (Simple logic: check all contacted)
            contacted_prospects = session.query(Prospect).filter(Prospect.status.in_(["CONTACTED", "FOLLOWUP_1"])).all()
            for p in contacted_prospects:
                 check_responses(p, session, email_handler)

            # Sleep to avoid CPU spin
            print(Fore.WHITE + "[*] Sleeping 60s...")
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("Stopping...")
            break
        except Exception as e:
            print(Fore.RED + f"Global Loop Error: {e}")
            time.sleep(10)

def process_new_prospect(prospect, session, email_handler):
    print(Fore.YELLOW + f"Processing {prospect.business_name}...")
    
    # 1. Scrape
    print("  > Scraping website...")
    text = scrape_business_data(prospect.url)
    if not text:
        print(Fore.RED + "  [-] Scraping failed (or empty). Continuing with metadata only...")
        text = "No website content available."
        
    # 2. Analyze Pain Point
    print("  > Analyzing pain points (Ollama)...")
    analysis = analyze_pain_points(text, prospect.business_name, prospect.industry)
    if not analysis:
        print(Fore.RED + "  [-] Analysis failed.")
        return
        
    prospect.pain_point = analysis.get("pain_point")
    prospect.pain_point_evidence = analysis.get("evidence")
    prospect.pain_point_confidence = analysis.get("confidence", 0.0)
    session.commit()
    print(Fore.CYAN + f"    > Identified: {prospect.pain_point}")
    
    # 3. Generate Solution
    print("  > Generating solution (Ollama)...")
    solution = generate_solution_concept(prospect.pain_point, prospect.business_name, prospect.industry)
    if not solution:
         print(Fore.RED + "  [-] Generation failed.")
         return
         
    print(Fore.CYAN + f"    > Proposed: {solution.get('title')}")
        
    # 4. Validate Solution
    print("  > Validating solution (Google API)...")
    is_valid, feedback = validate_solution(solution, prospect.pain_point)
    if not is_valid:
        print(Fore.RED + f"  [-] Solution Rejected: {feedback}")
        prospect.validation_status = "REJECTED"
        session.commit()
        return
    
    print(Fore.GREEN + "    > Solution APPROVED.") 
    prospect.solution_concept_title = solution.get("title")
    prospect.solution_concept_body = solution.get("concept_body")
    prospect.solution_technical_details = solution.get("technical_details")
    prospect.validation_status = "APPROVED"
    session.commit()
    
    # 5. Send Email
    print("  > Sending Initial Email...")
    subject = f"Question about {prospect.business_name}'s operations / Idea"
    body = draft_email(prospect, solution)
    
    tracking_id = email_handler.generate_tracking_id()
    if email_handler.send_email(prospect.email, subject, body, tracking_id):
        prospect.status = "CONTACTED"
        # Log interaction
        interaction = Interaction(prospect_id=prospect.id, type="EMAIL_SENT", content=body)
        session.add(interaction)
        session.commit()

def draft_email(prospect, solution):
    return f"""
    Hi {prospect.contact_name},<br><br>
    
    I'm Sam with Code Hatchers. I was looking at {prospect.business_name} online and noticed "{prospect.pain_point_evidence}".<br>
    It got me thinking about your operations.<br><br>
    
    We build custom Python-based AI solutions. I sketched out an idea for an <b>{solution['title']}</b> that works by 
    {solution['concept_body']}.<br><br>
    
    Would you be open to a 5-minute chat to see if this could help?<br><br>
    
    Best,<br>
    Sam<br>
    Business Developer<br>
    Code Hatchers<br>
    Sam@codehatchers.com
    """

def check_responses(prospect, session, email_handler):
    replies = email_handler.check_replies(prospect.email)
    if replies:
        print(Fore.GREEN + f"Reply detected from {prospect.business_name}!")
        prospect.status = "ENGAGED"
        interaction = Interaction(prospect_id=prospect.id, type="REPLY_RECEIVED", content=replies[0]['body'])
        session.add(interaction)
        session.commit()

if __name__ == "__main__":
    main()
