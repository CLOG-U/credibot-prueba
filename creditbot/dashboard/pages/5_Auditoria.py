"""Página de auditoría de tools."""
import pandas as pd
import streamlit as st

from dashboard.components.auth import require_login
from dashboard.services.supabase_dashboard import get_tool_audit_logs

st.set_page_config(page_title="Auditoría Tools", page_icon="🔍", layout="wide")
require_login()

st.title("Auditoría de tools")
st.caption("Registro de invocaciones del agente y motor determinista.")

logs = get_tool_audit_logs(limit=200)
if not logs:
    st.info("No hay registros de auditoría todavía.")
    st.stop()

df = pd.DataFrame(logs)
display_cols = [c for c in ["tool_name", "success", "error_code", "latency_ms", "created_at"] if c in df.columns]
st.dataframe(df[display_cols], use_container_width=True)

st.subheader("Detalle")
selected = st.selectbox("Registro", range(len(logs)), format_func=lambda i: f"{logs[i].get('tool_name')} — {logs[i].get('created_at')}")
if selected is not None:
    st.json(logs[selected])
