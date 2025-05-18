import streamlit as st
from modules.kpi_deadline_logic import check_deadline_alerts

def render_global_alerts():
    alerts = check_deadline_alerts()
    for a in alerts:
        st.warning(f"⚠ {a}")