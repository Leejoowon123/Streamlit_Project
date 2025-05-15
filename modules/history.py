import streamlit as st
from datetime import datetime

def save_analysis_result(company_name, result_dict):
    if "analysis_history" not in st.session_state:
        st.session_state["analysis_history"] = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state["analysis_history"].append({
        "company": company_name,
        "timestamp": timestamp,
        "result": result_dict
    })

def get_saved_analysis_titles():
    if "analysis_history" not in st.session_state:
        return []
    return [f"{entry['company']} - {entry['timestamp']}" for entry in st.session_state["analysis_history"]]

def get_analysis_by_index(index):
    return st.session_state["analysis_history"][index]["result"]