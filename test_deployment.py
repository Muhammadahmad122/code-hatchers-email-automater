import sys
import os
from colorama import init, Fore

init()

def test_imports():
    print(Fore.CYAN + "[*] Testing Imports...")
    try:
        # DB
        from src.database import get_engine, init_db
        print(Fore.GREEN + "  [+] Database module ok")
        
        # models check
        from src.database.models import Prospect
        print(Fore.GREEN + "  [+] Models ok")

        # AI
        from src.ai.scraper import scrape_business_data
        print(Fore.GREEN + "  [+] AI/Scraper module ok")
        
        from src.ai.pain_point import analyze_pain_points
        print(Fore.GREEN + "  [+] AI/Pain Point module ok")
        
        from src.ai.solution import generate_solution_concept, validate_solution
        print(Fore.GREEN + "  [+] AI/Solution module ok")

        # Email
        from src.email.outlook import EmailHandler
        print(Fore.GREEN + "  [+] Email module ok")
        
        # Libs
        import flask
        print(Fore.GREEN + "  [+] Flask ok")
        
        import google.generativeai
        print(Fore.GREEN + "  [+] Google Generative AI ok")
        
    except ImportError as e:
        print(Fore.RED + f"  [-] Import Error: {e}")
        return False
    except Exception as e:
        print(Fore.RED + f"  [-] Unexpected Error: {e}")
    return True

if __name__ == "__main__":
    if test_imports():
        print(Fore.GREEN + "\n[+] Deployment Structure Verified.")
    else:
        print(Fore.RED + "\n[-] Verify libraries are installed via requirements.txt")
