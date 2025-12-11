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
        remark_text = st.text_input("💬 EVALUATION REMARK", value="Accept")
    
    with col2:
        password = st.text_input("🔑 PASSWORD", type="password")
        skip_first = st.number_input(
            "⏭️ SKIP FIRST N TENDERERS", 
            min_value=0, 
            value=0, 
            step=1,
            help="If you've already processed some tenderers, enter the number to skip. Example: Enter 20 to start from tenderer #21."
        )

    st.info("💡 **TIP:** If automation fails or stops, note the last processed tenderer number, then restart and use 'Skip First N Tenderers' to resume from where you left off.")

    # Center the button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        run_button = st.button("▶ EXECUTE AUTOMATION")

    if run_button:
        if not email or not password or not tender_id:
            st.warning("⚠️ ALL FIELDS REQUIRED FOR SYSTEM INITIALIZATION")
        else:
            st.info("🔄 INITIALIZING AUTOMATION SEQUENCE...")
            run_automation(email, password, tender_id, remark_text, start_from=skip_first)
    
    show_copyright()
else:
    show_copyright()