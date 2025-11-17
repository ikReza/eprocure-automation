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

# --- Authentication Check ---
def check_password():
    """Returns `True` if the user provided correct password and logic_key."""

    def password_entered():
        """Checks whether user input is correct."""
        today = datetime.now().strftime("%Y%m%d")

        entered_password = st.session_state["password"]
        entered_logic_key = st.session_state["logic_key"]

        if entered_password == today and entered_logic_key == LOGIC_KEY:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["logic_key"]
        else:
            st.session_state["password_correct"] = False

    # First run
    if "password_correct" not in st.session_state:
        st.title("🔐 Login Required")
        st.info("This application requires a password to access.")

        st.text_input("Enter today's password (YYYYMMDD)", type="password", key="password")
        st.text_input("Enter logic key", type="password", key="logic_key")
        st.button("Login", on_click=password_entered)

        return False

    # Wrong password
    elif not st.session_state["password_correct"]:
        st.title("🔐 Login Required")
        st.error("😕 Password or logic key incorrect")

        st.text_input("Enter today's password (YYYYMMDD)", type="password", key="password")
        st.text_input("Enter logic key", type="password", key="logic_key")
        st.button("Login", on_click=password_entered)

        return False

    # Correct password
    else:
        return True

# --- Copyright Notice ---
def show_copyright():
    """Displays copyright notice at bottom right"""
    st.markdown("""
    <style>
    .copyright {
        position: fixed;
        bottom: 10px;
        right: 15px;
        color: #d3d3d3;
        font-size: 12px;
        font-family: Arial, sans-serif;
        z-index: 999;
        opacity: 0.6;
        pointer-events: none;
    }
    </style>
    <div class="copyright">ⓒ iKaiser</div>
    """, unsafe_allow_html=True)

# --- Main App ---
if check_password():
    # --- Streamlit UI ---
    st.title("E-Procure Tender Automation")

    st.markdown("""
    This tool automates tender evaluation in **eprocure.gov.bd**.
    """)

    email = st.text_input("Enter your Email")
    password = st.text_input("Enter your Password", type="password")
    tender_id = st.text_input("Enter Tender ID")
    remark_text = st.text_input("Enter Remark", value="Accepted")

    run_button = st.button("Run Automation")

    if run_button:
        if not email or not password or not tender_id:
            st.warning("Please enter all fields!")
        else:
            st.info("Starting automation... Make sure Chrome is installed.")

            try:
                # --- Setup Chrome WebDriver ---
                chrome_options = Options()
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--disable-infobars")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--disable-notifications")
                
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
                wait = WebDriverWait(driver, 10)

                # --- Step 1: Open website ---
                driver.get("https://www.eprocure.gov.bd")
                time.sleep(3)

                # --- Step 2: Login ---
                driver.find_element(By.ID, "txtEmailId").send_keys(email)
                driver.find_element(By.ID, "txtPassword").send_keys(password)
                driver.find_element(By.ID, "btnLogin").click()
                time.sleep(5)

                # --- Step 3: Click "Update Later" if exists ---
                try:
                    driver.find_element(By.ID, "btnUpdateLater").click()
                    st.success("✅ Clicked 'Update Later'")
                except:
                    st.info("⚠️ 'Update Later' button not found or skipped")

                # --- Step 4: Hover Tender → My Tender ---
                actions = ActionChains(driver)
                tender_tab = driver.find_element(By.ID, "headTabTender")
                actions.move_to_element(tender_tab).perform()
                time.sleep(1)
                driver.find_element(By.XPATH, "//a[@href='/officer/MyTenders.jsp']").click()
                st.success("✅ Opened 'My Tender'")

                # --- Step 5: Enter Tender ID ---
                time.sleep(5)
                tender_input = driver.find_element(By.ID, "tenderId")
                tender_input.clear()
                tender_input.send_keys(tender_id)
                st.success(f"✅ Entered Tender ID: {tender_id}")

                # --- Step 6: Click Processing tab ---
                driver.find_element(By.ID, "processingTab").click()
                time.sleep(3)
                st.success("✅ Clicked Processing tab")

                # --- Step 7: Dashboard ---
                dashboard_xpath = f"//a[@href='/officer/TenderDashboard.jsp?tenderid={tender_id}']"
                driver.find_element(By.XPATH, dashboard_xpath).click()
                time.sleep(3)
                st.success("✅ Opened Dashboard")

                # --- Step 8: Evaluation tab ---
                driver.find_element(By.XPATH, f"//a[contains(@href,'/officer/EvalComm.jsp?tenderid={tender_id}')]").click()
                time.sleep(3)
                st.success("✅ Opened Evaluation tab")

                # --- Step 9: Clarification tab ---
                driver.find_element(By.ID, "tbClari").click()
                time.sleep(3)
                st.success("✅ Opened Clarification tab")

                # --- Step 10: Find the correct tenderers table ---
                st.subheader("🔄 Processing Tenderers")
                
                # Find the specific table with tenderers (the one after "List of Tenderers/Consultants for seeking clarification")
                tables = driver.find_elements(By.CSS_SELECTOR, "table.tableList_1")
                target_table = None
                
                for table in tables:
                    try:
                        headers = table.find_elements(By.TAG_NAME, "th")
                        header_text = " ".join([h.text for h in headers])
                        # Look for the table with "S. No." and "List of Tenderers" headers
                        if "S. No." in header_text and "List of Tenderers" in header_text:
                            target_table = table
                            break
                    except:
                        continue
                
                if not target_table:
                    st.error("❌ Could not find the tenderers table!")
                    raise Exception("Tenderers table not found")
                
                # Get all tenderer rows from the specific table
                tenderer_rows = target_table.find_elements(By.XPATH, ".//tr[td]")
                total_tenderers = len(tenderer_rows)
                st.info(f"📊 Found {total_tenderers} tenderers to process")
                
                # Create a progress container
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                successful_tenderers = 0
                failed_tenderers = 0
                
                # --- Loop through each tenderer ---
                for idx, row in enumerate(tenderer_rows, start=1):
                    try:
                        # Update progress
                        progress_bar.progress(idx / total_tenderers)
                        
                        # Get tenderer name for logging
                        try:
                            tenderer_name = row.find_element(By.XPATH, ".//td[2]//a").text.strip()
                        except:
                            tenderer_name = f"Tenderer #{idx}"
                        
                        status_text.text(f"Processing: {tenderer_name} ({idx}/{total_tenderers})")
                        
                        # Find and click "View Evaluation Status" link
                        eval_link = row.find_element(By.XPATH, ".//a[contains(@href,'EvalViewStatus.jsp')]")
                        driver.execute_script("arguments[0].scrollIntoView(true);", eval_link)
                        time.sleep(0.5)
                        eval_link.click()
                        time.sleep(3)
                        
                        st.info(f"✅ [{idx}/{total_tenderers}] Opened evaluation page for: {tenderer_name}")
                        
                        # --- Step 11: Find and process all forms for this tenderer ---
                        try:
                            # Wait for the forms table to load
                            time.sleep(2)
                            
                            # Find all "Evaluate Form" links on the current page
                            form_links = driver.find_elements(By.XPATH, "//a[contains(text(),'Evaluate Form') or contains(@href,'EvalCriteria.jsp')]")
                            total_forms = len(form_links)
                            
                            if total_forms == 0:
                                st.warning(f"⚠️ No forms found for {tenderer_name}")
                            else:
                                st.info(f"📋 Found {total_forms} forms for {tenderer_name}")
                                
                                forms_processed = 0
                                
                                # Process each form
                                for jdx in range(total_forms):
                                    try:
                                        # Re-find form links after each navigation back
                                        form_links = driver.find_elements(By.XPATH, "//a[contains(text(),'Evaluate Form') or contains(@href,'EvalCriteria.jsp')]")
                                        
                                        if jdx >= len(form_links):
                                            st.warning(f"⚠️ Form {jdx+1} not found after page refresh")
                                            continue
                                        
                                        form_link = form_links[jdx]
                                        
                                        # Scroll and click
                                        driver.execute_script("arguments[0].scrollIntoView(true);", form_link)
                                        time.sleep(0.5)
                                        form_link.click()
                                        time.sleep(3)
                                        
                                        st.info(f"   📝 Processing Form {jdx+1}/{total_forms}")
                                        
                                        # --- Step 12: Fill the evaluation form ---
                                        try:
                                            # Click "Accept" radio button
                                            accept_radio = wait.until(EC.element_to_be_clickable((By.ID, "techQualify")))
                                            driver.execute_script("arguments[0].click();", accept_radio)
                                            time.sleep(0.5)
                                            
                                            # Enter remark
                                            remark_box = driver.find_element(By.ID, "evalNonCompRemarks")
                                            remark_box.clear()
                                            remark_box.send_keys(remark_text)
                                            time.sleep(0.5)
                                            
                                            # Click Submit button
                                            submit_btn = driver.find_element(By.ID, "btnPost")
                                            driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
                                            time.sleep(0.5)
                                            submit_btn.click()
                                            
                                            # Handle any alerts
                                            try:
                                                time.sleep(1)
                                                alert = driver.switch_to.alert
                                                alert_text = alert.text
                                                alert.accept()
                                                st.info(f"   ℹ️ Alert: {alert_text}")
                                            except:
                                                pass
                                            
                                            time.sleep(2)
                                            st.success(f"   ✅ Form {jdx+1}/{total_forms} submitted successfully")
                                            forms_processed += 1
                                            
                                        except Exception as form_error:
                                            st.error(f"   ❌ Error filling form {jdx+1}: {str(form_error)}")
                                        
                                        # Navigate back to forms list
                                        driver.back()
                                        time.sleep(2)
                                        
                                    except Exception as form_nav_error:
                                        st.error(f"   ❌ Error navigating form {jdx+1}: {str(form_nav_error)}")
                                        continue
                                
                                if forms_processed == total_forms:
                                    st.success(f"✅ Completed all {forms_processed} forms for {tenderer_name}")
                                    successful_tenderers += 1
                                else:
                                    st.warning(f"⚠️ Completed {forms_processed}/{total_forms} forms for {tenderer_name}")
                        
                        except Exception as forms_error:
                            st.error(f"❌ Error processing forms for {tenderer_name}: {str(forms_error)}")
                            failed_tenderers += 1
                        
                        # Navigate back to tenderers list
                        driver.back()
                        time.sleep(3)
                        
                    except Exception as tenderer_error:
                        st.error(f"❌ Error processing tenderer #{idx}: {str(tenderer_error)}")
                        failed_tenderers += 1
                        try:
                            driver.back()
                            time.sleep(2)
                        except:
                            pass
                        continue
                
                # Final summary
                progress_bar.progress(1.0)
                status_text.text("Processing complete!")
                
                st.success("🎯 Automation completed!")
                st.info(f"""
                **Summary:**
                - Total Tenderers: {total_tenderers}
                - Successfully Processed: {successful_tenderers}
                - Failed: {failed_tenderers}
                """)

            except Exception as e:
                st.error(f"❌ Automation failed: {e}")
                import traceback
                st.error(traceback.format_exc())
            finally:
                if 'driver' in locals():
                    st.info("Browser will close in 10 seconds...")
                    time.sleep(10)
                    driver.quit()
                    st.info("Browser closed.")
    
    # Show copyright notice at the bottom
    show_copyright()
else:
    # Also show copyright on login page
    show_copyright()