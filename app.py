import streamlit as st
from auth import check_password
from theme import apply_scifi_theme, show_copyright
from automation import run_automation

# Apply theme
apply_scifi_theme()

# --- Main App ---
if check_password():
    st.title("⚡ E-PROCURE TENDER AUTOMATION")

    st.markdown("""
    <div class="main-container">
    <p style="text-align: center; font-size: 18px;">
    🚀 AUTOMATED TENDER EVALUATION SYSTEM FOR <strong>eprocure.gov.bd</strong>
    </p>
    </div>
    """, unsafe_allow_html=True)

    # Input fields in a container
    st.subheader("⚙️ SYSTEM CONFIGURATION")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email = st.text_input("📧 EMAIL ADDRESS")
        tender_id = st.text_input("🆔 TENDER ID")
    
    with col2:
        password = st.text_input("🔑 PASSWORD", type="password")
        remark_text = st.text_input("💬 EVALUATION REMARK", value="Accept")

    # Center the button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        run_button = st.button("▶ EXECUTE AUTOMATION")

    if run_button:
        if not email or not password or not tender_id:
            st.warning("⚠️ ALL FIELDS REQUIRED FOR SYSTEM INITIALIZATION")
        else:
            st.info("🔄 INITIALIZING AUTOMATION SEQUENCE...")
            run_automation(email, password, tender_id, remark_text)
    
    show_copyright()
else:
    show_copyright()