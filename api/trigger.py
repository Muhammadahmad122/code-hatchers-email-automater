from flask import Flask, jsonify
import sys
import os

# Add parent directory to path so we can import src
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database import init_db, get_engine, get_session, Prospect
from src.email.outlook import EmailHandler
# Import the processing functions - assuming we refactor main.py to make them importable
# or we duplicate the simple logic here to avoid circular imports / main execution
from main import process_new_prospect, check_responses

app = Flask(__name__)

@app.route('/api/trigger')
def trigger():
    try:
        # Initialize resources
        engine = get_engine()
        init_db(engine)
        session = get_session(engine)
        
        try:
            email_handler = EmailHandler()
        except Exception as e:
            return jsonify({"error": f"Email config error: {str(e)}"}), 500

        results = []
        
        # 1. Process one new prospect
        new_prospects = session.query(Prospect).filter_by(status="NEW").limit(1).all()
        if new_prospects:
            for p in new_prospects:
                process_new_prospect(p, session, email_handler)
                results.append(f"Processed {p.business_name}")
        else:
            results.append("No new prospects")

        # 2. Check for replies
        contacted = session.query(Prospect).filter(Prospect.status.in_(["CONTACTED", "FOLLOWUP_1"])).all()
        for p in contacted:
            check_responses(p, session, email_handler)
            
        return jsonify({"status": "success", "actions": results})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handler(request):
    return app(request)
