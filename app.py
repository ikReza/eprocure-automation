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

    # Skip option
    start_from = st.number_input("⏭️ SKIP FIRST N TENDERERS (Optional)", min_value=0, value=0, step=1)

    # Center the button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        run_button = st.button("▶ EXECUTE AUTOMATION")

    if run_button:
        if not email or not password or not tender_id:
            st.warning("⚠️ ALL FIELDS REQUIRED FOR SYSTEM INITIALIZATION")
        else:
            st.info("🔄 INITIALIZING AUTOMATION SEQUENCE...")
            run_automation(email, password, tender_id, remark_text, start_from)
    
    # Show download button if CSV data exists from previous run
    if 'csv_data' in st.session_state and len(st.session_state.csv_data) > 1:
        st.divider()
        st.subheader("📥 PREVIOUS RUN DATA")
        
        import csv
        import io
        from datetime import datetime
        
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerows(st.session_state.csv_data)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.download_button(
                label=f"📥 Download Previous Log ({len(st.session_state.csv_data)-1} entries)",
                data=csv_buffer.getvalue(),
                file_name=f"log_{tender_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    show_copyright()
else:
    show_copyright()