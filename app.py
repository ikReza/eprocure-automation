import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read secret logic key from environment variable
LOGIC_KEY = os.getenv("LOGIC_KEY")

# --- Sci-Fi Theme CSS ---
def apply_scifi_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1628 100%);
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Animated background grid */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        animation: gridMove 20s linear infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes gridMove {
        0% { transform: translate(0, 0); }
        100% { transform: translate(50px, 50px); }
    }
    
    /* Glowing particles */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: radial-gradient(circle, rgba(0, 255, 255, 0.1) 1px, transparent 1px);
        background-size: 100px 100px;
        animation: particleFloat 30s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes particleFloat {
        0%, 100% { opacity: 0.3; transform: translateY(0); }
        50% { opacity: 0.6; transform: translateY(-20px); }
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #00ffff !important;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.5),
                     0 0 20px rgba(0, 255, 255, 0.3),
                     0 0 30px rgba(0, 255, 255, 0.2);
        position: relative;
        z-index: 1;
    }
    
    h1 {
        font-size: 2.5rem !important;
        border-bottom: 2px solid #00ffff;
        padding-bottom: 15px;
        margin-bottom: 30px;
        animation: titleGlow 2s ease-in-out infinite;
    }
    
    @keyframes titleGlow {
        0%, 100% { text-shadow: 0 0 10px rgba(0, 255, 255, 0.5), 0 0 20px rgba(0, 255, 255, 0.3); }
        50% { text-shadow: 0 0 20px rgba(0, 255, 255, 0.8), 0 0 30px rgba(0, 255, 255, 0.5), 0 0 40px rgba(0, 255, 255, 0.3); }
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background: rgba(10, 20, 40, 0.6) !important;
        border: 2px solid #00ffff !important;
        border-radius: 8px !important;
        color: #00ffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 16px !important;
        padding: 12px !important;
        box-shadow: inset 0 0 10px rgba(0, 255, 255, 0.2),
                    0 0 15px rgba(0, 255, 255, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00ffff !important;
        box-shadow: inset 0 0 15px rgba(0, 255, 255, 0.3),
                    0 0 25px rgba(0, 255, 255, 0.4) !important;
        outline: none !important;
    }
    
    .stTextInput > label {
        color: #00ffff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 14px !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%) !important;
        color: #00ffff !important;
        border: 2px solid #00ffff !important;
        border-radius: 8px !important;
        padding: 15px 40px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.4),
                    inset 0 0 10px rgba(0, 255, 255, 0.1) !important;
        transition: all 0.3s ease !important;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0f1a2e 0%, #1f2f4a 100%) !important;
        color: #00ffff !important;
        border-color: #00ffff !important;
        box-shadow: 0 0 40px rgba(0, 255, 255, 0.8),
                    inset 0 0 20px rgba(0, 255, 255, 0.2) !important;
        transform: translateY(-2px);
        text-shadow: 0 0 15px rgba(0, 255, 255, 1);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.6),
                    inset 0 0 15px rgba(0, 255, 255, 0.15) !important;
    }
    
    /* Info boxes */
    .stAlert {
        background: rgba(0, 255, 255, 0.1) !important;
        border: 1px solid #00ffff !important;
        border-left: 4px solid #00ffff !important;
        border-radius: 8px !important;
        color: #00ffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.2) !important;
    }
    
    .stSuccess {
        background: rgba(0, 255, 136, 0.1) !important;
        border: 1px solid #00ff88 !important;
        border-left: 4px solid #00ff88 !important;
        color: #00ff88 !important;
    }
    
    .stWarning {
        background: rgba(255, 193, 7, 0.1) !important;
        border: 1px solid #ffc107 !important;
        border-left: 4px solid #ffc107 !important;
        color: #ffc107 !important;
    }
    
    .stError {
        background: rgba(255, 0, 102, 0.1) !important;
        border: 1px solid #ff0066 !important;
        border-left: 4px solid #ff0066 !important;
        color: #ff0066 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #00ffff 0%, #00ff88 100%) !important;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.5) !important;
    }
    
    .stProgress > div > div {
        background: rgba(0, 255, 255, 0.1) !important;
        border: 1px solid #00ffff !important;
        border-radius: 10px !important;
    }
    
    /* Markdown text */
    p, li, .stMarkdown {
        color: #b0c4de !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
    }
    
    /* Copyright */
    .copyright {
        position: fixed;
        bottom: 10px;
        right: 15px;
        color: #00ffff;
        font-size: 12px;
        font-family: 'Orbitron', sans-serif;
        z-index: 999;
        opacity: 0.6;
        pointer-events: none;
        text-shadow: 0 0 5px rgba(0, 255, 255, 0.5);
        letter-spacing: 2px;
    }
    
    /* Subheader styling */
    .stSubheader {
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e27 0%, #1a1f3a 100%) !important;
        border-right: 2px solid #00ffff !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- Authentication Check ---
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
        st.title("🔐 SECURE ACCESS")
        st.info("⚡ ENTER YOUR ACCESS CREDENTIALS TO CONTINUE")

        st.text_input(
            "PASSWORD",
            type="password",
            key="password_input"
        )
        st.button("◉ INITIALIZE LOGIN", on_click=password_entered)
        st.markdown('</div>', unsafe_allow_html=True)
        return False

    elif not st.session_state["password_correct"]:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.title("🔐 SECURE ACCESS")
        st.error("⚠️ ACCESS DENIED - INCORRECT CREDENTIALS")

        st.text_input(
            "PASSWORD",
            type="password",
            key="password_input"
        )
        st.button("◉ INITIALIZE LOGIN", on_click=password_entered)
        st.markdown('</div>', unsafe_allow_html=True)
        return False

    else:
        return True

# --- Copyright Notice ---
def show_copyright():
    """Displays copyright notice at bottom right"""
    st.markdown("""
    <div class="copyright">© iKAISER</div>
    """, unsafe_allow_html=True)

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
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Center the button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        run_button = st.button("▶ EXECUTE AUTOMATION")

    if run_button:
        if not email or not password or not tender_id:
            st.warning("⚠️ ALL FIELDS REQUIRED FOR SYSTEM INITIALIZATION")
        else:
            st.info("🔄 INITIALIZING AUTOMATION SEQUENCE...")

            try:
                chrome_options = Options()
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--disable-infobars")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--disable-notifications")
                
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
                wait = WebDriverWait(driver, 10)

                driver.get("https://www.eprocure.gov.bd")
                time.sleep(3)

                driver.find_element(By.ID, "txtEmailId").send_keys(email)
                driver.find_element(By.ID, "txtPassword").send_keys(password)
                driver.find_element(By.ID, "btnLogin").click()
                time.sleep(5)

                try:
                    driver.find_element(By.ID, "btnUpdateLater").click()
                    st.success("✅ UPDATE PROMPT BYPASSED")
                except:
                    st.info("⚡ NO UPDATE PROMPT DETECTED")

                actions = ActionChains(driver)
                tender_tab = driver.find_element(By.ID, "headTabTender")
                actions.move_to_element(tender_tab).perform()
                time.sleep(1)
                driver.find_element(By.XPATH, "//a[@href='/officer/MyTenders.jsp']").click()
                st.success("✅ MY TENDER MODULE ACCESSED")

                time.sleep(5)
                tender_input = driver.find_element(By.ID, "tenderId")
                tender_input.clear()
                tender_input.send_keys(tender_id)
                st.success(f"✅ TENDER ID CONFIGURED: {tender_id}")

                driver.find_element(By.ID, "processingTab").click()
                time.sleep(3)
                st.success("✅ PROCESSING TAB ACTIVATED")

                dashboard_xpath = f"//a[@href='/officer/TenderDashboard.jsp?tenderid={tender_id}']"
                driver.find_element(By.XPATH, dashboard_xpath).click()
                time.sleep(3)
                st.success("✅ DASHBOARD MODULE LOADED")

                driver.find_element(By.XPATH, f"//a[contains(@href,'/officer/EvalComm.jsp?tenderid={tender_id}')]").click()
                time.sleep(3)
                st.success("✅ EVALUATION MODULE INITIALIZED")

                driver.find_element(By.ID, "tbClari").click()
                time.sleep(3)
                st.success("✅ CLARIFICATION INTERFACE ACTIVE")

                st.subheader("📊 PROCESSING TENDERERS")
                
                tables = driver.find_elements(By.CSS_SELECTOR, "table.tableList_1")
                target_table = None
                
                for table in tables:
                    try:
                        headers = table.find_elements(By.TAG_NAME, "th")
                        header_text = " ".join([h.text for h in headers])
                        if "S. No." in header_text and "List of Tenderers" in header_text:
                            target_table = table
                            break
                    except:
                        continue
                
                if not target_table:
                    st.error("❌ TENDERERS TABLE NOT FOUND IN SYSTEM")
                    raise Exception("Tenderers table not found")
                
                tenderer_rows = target_table.find_elements(By.XPATH, ".//tr[td]")
                total_tenderers = len(tenderer_rows)
                st.info(f"🎯 DETECTED {total_tenderers} TENDERERS FOR PROCESSING")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                successful_tenderers = 0
                failed_tenderers = 0
                
                for idx, row in enumerate(tenderer_rows, start=1):
                    try:
                        progress_bar.progress(idx / total_tenderers)
                        
                        try:
                            tenderer_name = row.find_element(By.XPATH, ".//td[2]//a").text.strip()
                        except:
                            tenderer_name = f"TENDERER #{idx}"
                        
                        status_text.markdown(f"<h5 style='color: #ff0066;'>⚡ PROCESSING: {tenderer_name} ({idx}/{total_tenderers})</h5>", unsafe_allow_html=True)
                        
                        eval_link = row.find_element(By.XPATH, ".//a[contains(@href,'EvalViewStatus.jsp')]")
                        driver.execute_script("arguments[0].scrollIntoView(true);", eval_link)
                        time.sleep(0.5)
                        eval_link.click()
                        time.sleep(3)
                        
                        st.info(f"✅ [{idx}/{total_tenderers}] EVALUATION PAGE LOADED: {tenderer_name}")
                        
                        try:
                            time.sleep(2)
                            
                            form_links = driver.find_elements(By.XPATH, "//a[contains(text(),'Evaluate Form') or contains(@href,'EvalCriteria.jsp')]")
                            total_forms = len(form_links)
                            
                            if total_forms == 0:
                                st.warning(f"⚠️ NO FORMS DETECTED FOR {tenderer_name}")
                            else:
                                st.info(f"📋 PROCESSING {total_forms} FORMS FOR {tenderer_name}")
                                
                                forms_processed = 0
                                
                                for jdx in range(total_forms):
                                    try:
                                        form_links = driver.find_elements(By.XPATH, "//a[contains(text(),'Evaluate Form') or contains(@href,'EvalCriteria.jsp')]")
                                        
                                        if jdx >= len(form_links):
                                            st.warning(f"⚠️ FORM {jdx+1} UNAVAILABLE AFTER REFRESH")
                                            continue
                                        
                                        form_link = form_links[jdx]
                                        
                                        driver.execute_script("arguments[0].scrollIntoView(true);", form_link)
                                        time.sleep(0.5)
                                        form_link.click()
                                        time.sleep(3)
                                        
                                        st.info(f"   🔹 EXECUTING FORM {jdx+1}/{total_forms}")
                                        
                                        try:
                                            accept_radio = wait.until(EC.element_to_be_clickable((By.ID, "techQualify")))
                                            driver.execute_script("arguments[0].click();", accept_radio)
                                            time.sleep(0.5)
                                            
                                            remark_box = driver.find_element(By.ID, "evalNonCompRemarks")
                                            remark_box.clear()
                                            remark_box.send_keys(remark_text)
                                            time.sleep(0.5)
                                            
                                            submit_btn = driver.find_element(By.ID, "btnPost")
                                            driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
                                            time.sleep(0.5)
                                            submit_btn.click()
                                            
                                            try:
                                                time.sleep(1)
                                                alert = driver.switch_to.alert
                                                alert_text = alert.text
                                                alert.accept()
                                                st.info(f"   ℹ️ SYSTEM ALERT: {alert_text}")
                                            except:
                                                pass
                                            
                                            time.sleep(2)
                                            st.success(f"   ✅ FORM {jdx+1}/{total_forms} SUBMITTED SUCCESSFULLY")
                                            forms_processed += 1
                                            
                                        except Exception as form_error:
                                            st.error(f"   ❌ FORM {jdx+1} ERROR: {str(form_error)}")
                                        
                                        driver.back()
                                        time.sleep(2)
                                        
                                    except Exception as form_nav_error:
                                        st.error(f"   ❌ NAVIGATION ERROR FORM {jdx+1}: {str(form_nav_error)}")
                                        continue
                                
                                if forms_processed == total_forms:
                                    st.success(f"✅ ALL {forms_processed} FORMS COMPLETED FOR {tenderer_name}")
                                    successful_tenderers += 1
                                else:
                                    st.warning(f"⚠️ COMPLETED {forms_processed}/{total_forms} FORMS FOR {tenderer_name}")
                        
                        except Exception as forms_error:
                            st.error(f"❌ FORMS PROCESSING ERROR FOR {tenderer_name}: {str(forms_error)}")
                            failed_tenderers += 1
                        
                        driver.back()
                        time.sleep(3)
                        
                    except Exception as tenderer_error:
                        st.error(f"❌ TENDERER #{idx} PROCESSING ERROR: {str(tenderer_error)}")
                        failed_tenderers += 1
                        try:
                            driver.back()
                            time.sleep(2)
                        except:
                            pass
                        continue
                
                progress_bar.progress(1.0)
                status_text.markdown("<h5 style='color: #ff0066;'>✅ PROCESSING SEQUENCE COMPLETE</h5>", unsafe_allow_html=True)
                
                st.success("🎯 AUTOMATION SUCCESSFULLY EXECUTED")
                st.markdown(f"""
                <div class="main-container">
                <h3 style="text-align: center;">📊 EXECUTION SUMMARY</h3>
                <p style="text-align: center; font-size: 18px;">
                <strong>TOTAL TENDERERS:</strong> {total_tenderers}<br>
                <strong style="color: #00ff88;">SUCCESSFULLY PROCESSED:</strong> {successful_tenderers}<br>
                <strong style="color: #ff0066;">FAILED:</strong> {failed_tenderers}
                </p>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ SYSTEM FAILURE: {e}")
                import traceback
                st.error(traceback.format_exc())
            finally:
                if 'driver' in locals():
                    st.info("🔄 BROWSER SHUTDOWN IN 10 SECONDS...")
                    time.sleep(10)
                    driver.quit()
                    st.info("✅ BROWSER TERMINATED")
    
    show_copyright()
else:
    show_copyright()