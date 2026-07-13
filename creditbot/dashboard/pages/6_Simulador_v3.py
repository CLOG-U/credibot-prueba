"""Simulador v3 para pruebas manuales con metadata del agente."""
import os

import httpx
import streamlit as st

from dashboard.components.auth import require_login

st.set_page_config(page_title="Simulador v3", page_icon="💬", layout="wide")
require_login()

API_BASE = os.getenv("CREDIBOT_API_URL", "http://127.0.0.1:8000")

st.title("Simulador v3")
st.caption("Prueba el flujo conversacional con NLU, GPT opcional y RAG.")

phone = st.text_input("Teléfono", value="593555555101")
enable_samples = st.checkbox("Mostrar mensajes de ejemplo", value=True)

if enable_samples:
    st.markdown(
        """
**Flujo sugerido**
1. Hola
2. 1 (precalificar)
3. Sí acepto
4. `1713175071` (excelente)
5. Gano 2000 al mes
6. Trabajo dependiente
7. 400
8. 24
9. Educación
10. 1 (confirmar)

**Preguntas RAG:** ¿Cuál es el plazo máximo? / ¿Es una aprobación final?
        """
    )

if "chat" not in st.session_state:
    st.session_state.chat = []

message = st.chat_input("Escribe un mensaje...")
if message:
    try:
        response = httpx.post(
            f"{API_BASE}/simulate/message",
            json={"phone": phone, "message": message},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        st.session_state.chat.append({"user": message, "bot": data})
    except httpx.ConnectError:
        st.error("No se pudo conectar con la API. Levanta: `uvicorn app.main:app --reload`")
    except httpx.HTTPStatusError as exc:
        st.error(f"Error HTTP {exc.response.status_code}: {exc.response.text}")

for turn in st.session_state.chat:
    st.chat_message("user").write(turn["user"])
    bot = turn["bot"]
    meta = f"estado={bot.get('state')} | modo={bot.get('agent_mode')} | tokens={bot.get('tokens')}"
    st.chat_message("assistant").write(bot["reply"])
    st.caption(meta)

if st.button("Limpiar conversación"):
    st.session_state.chat = []
    st.rerun()
