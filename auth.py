import os
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read secret logic key from environment variable
LOGIC_KEY = os.getenv("LOGIC_KEY")

def check_password():
    """Returns `True` if the user provided correct full password."""

    def password_entered():
        """Validate entered password."""
        
        today = datetime.now().strftime("%Y%m%d")
        expected_password = today + LOGIC_KEY

        entered_password = st.session_state["password_input"]

        if entered_password == expected_password:
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔒 SECURE ACCESS")
        st.info("⚡ ENTER YOUR ACCESS CREDENTIALS TO CONTINUE")

        st.text_input(
            "PASSWORD",
            type="password",
            key="password_input"
        )
        st.button("◉ INITIALIZE LOGIN", on_click=password_entered)
        return False

    elif not st.session_state["password_correct"]:
        st.title("🔒 SECURE ACCESS")
        st.error("⚠️ ACCESS DENIED - INCORRECT CREDENTIALS")

        st.text_input(
            "PASSWORD",
            type="password",
            key="password_input"
        )
        st.button("◉ INITIALIZE LOGIN", on_click=password_entered)
        return False

    else:
        return True