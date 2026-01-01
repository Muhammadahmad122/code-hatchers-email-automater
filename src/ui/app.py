import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
from dotenv import load_dotenv, set_key
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Prospect, Interaction, get_engine, init_db
from src.ai.scraper import scrape_business_data
from src.ai.pain_point import analyze_pain_points
import subprocess
import sys

# Page Config
st.set_page_config(
    page_title="Code Hatchers Automater",
    page_icon="🚀",
    layout="wide",
)

# Initialize DB connection
@st.cache_resource
def get_db_session():
    engine = get_engine()
    init_db(engine) # Ensure tables exist
    Session = sessionmaker(bind=engine)
    return Session()

session = get_db_session()

# Sidebar
st.sidebar.title("🚀 Code Hatchers")
page = st.sidebar.radio("Navigation", ["Dashboard", "Prospects", "Live Logs", "Settings"])

if page == "Dashboard":
    st.title("📊 Operational Dashboard")
    
    # Metrics
    total_prospects = session.query(Prospect).count()
    contacted = session.query(Prospect).filter(Prospect.status == "CONTACTED").count()
    replies = session.query(Prospect).filter(Prospect.status == "ENGAGED").count()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Prospects", total_prospects)
    col2.metric("Emails Sent", contacted)
    col3.metric("Replies Received", replies)
    
    # Graph
    st.subheader("Industry Breakdown")
    data = pd.read_sql(session.query(Prospect).statement, session.bind)
    if not data.empty:
        fig = px.pie(data, names='industry', title='Prospects by Industry')
        st.plotly_chart(fig)
    else:
        st.info("No data available yet.")

elif page == "Prospects":
    st.title("👥 Prospect Management")
    
    # Add New
    with st.expander("➕ Add New Prospect"):
        with st.form("add_prospect"):
            b_name = st.text_input("Business Name")
            url = st.text_input("Website URL")
            industry = st.text_input("Industry (e.g., Restaurant)")
            email = st.text_input("Contact Email")
            c_name = st.text_input("Contact Name")
            
            submitted = st.form_submit_button("Add to Queue")
            if submitted:
                if email and url:
                    p = Prospect(
                        business_name=b_name, 
                        url=url, 
                        industry=industry, 
                        email=email, 
                        contact_name=c_name, 
                        status="NEW"
                    )
                    session.add(p)
                    session.commit()
                    st.success(f"Added {b_name}!")
                    st.rerun()
                else:
                    st.error("Email and URL are required.")

    # View Table
    st.subheader("Database")
    prospects = session.query(Prospect).all()
    if prospects:
        data = [{
            "ID": p.id,
            "Business": p.business_name,
            "Status": p.status,
            "Pain Point": p.pain_point,
            "Solution": p.solution_concept_title,
            "Email": p.email
        } for p in prospects]
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No prospects found.")

elif page == "Live Logs":
    st.title("📡 Live System Logs")
    st.markdown("Run the automation loop to see logs here.")
    
    if st.button("▶ Run Automation Loop (Background)"):
        # This is a bit tricky from Streamlit, but we can try subprocess Popen
        subprocess.Popen([sys.executable, "main.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        st.success("Launched main.py in a new console window!")
        
    st.caption("Auto-refreshing log view is complex in file-based setups. Check the console window.")

elif page == "Settings":
    st.title("⚙️ Configuration")
    
    env_file = ".env"
    load_dotenv(env_file)
    
    with st.form("settings"):
        email_user = st.text_input("Outlook Email", value=os.getenv("EMAIL_HOST_USER", ""))
        email_pass = st.text_input("Outlook Password", value=os.getenv("EMAIL_HOST_PASSWORD", ""), type="password")
        google_key = st.text_input("Google API Key", value=os.getenv("GOOGLE_API_KEY", ""))
        ollama_host = st.text_input("Ollama Host", value=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        
        saved = st.form_submit_button("Save Configuration")
        if saved:
            set_key(env_file, "EMAIL_HOST_USER", email_user)
            set_key(env_file, "EMAIL_HOST_PASSWORD", email_pass)
            set_key(env_file, "GOOGLE_API_KEY", google_key)
            set_key(env_file, "OLLAMA_HOST", ollama_host)
            st.success("Settings saved! Restart application to apply.")
