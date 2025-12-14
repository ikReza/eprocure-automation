import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import csv
from datetime import datetime
import io

# --- Chrome Driver Setup ---
def get_chrome_driver():
    """Initialize Chrome driver compatible with both local and Streamlit Cloud"""
    chrome_options = Options()
    
    # Essential options for Streamlit Cloud
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-features=NetworkService")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Check if running on Streamlit Cloud (Linux with chromium installed)
    if os.path.exists("/usr/bin/chromium"):
        st.info("🌐 Detected Streamlit Cloud environment")
        chrome_options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        # Local development - use webdriver-manager
        st.info("💻 Detected local environment")
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def navigate_to_clarification(driver, tender_id):
    """Navigate from current page to Clarification tab"""
    try:
        # Wait for page to be fully loaded
        wait = WebDriverWait(driver, 15)
        
        # Navigate to My Tenders - with explicit wait
        wait.until(EC.presence_of_element_located((By.ID, "headTabTender")))
        actions = ActionChains(driver)
        tender_tab = wait.until(EC.element_to_be_clickable((By.ID, "headTabTender")))
        actions.move_to_element(tender_tab).perform()
        time.sleep(2)
        
        my_tender_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/officer/MyTenders.jsp']")))
        my_tender_link.click()
        time.sleep(5)

        # Enter tender ID
        tender_input = wait.until(EC.presence_of_element_located((By.ID, "tenderId")))
        tender_input.clear()
        tender_input.send_keys(tender_id)
        time.sleep(1)

        # Click Processing Tab
        processing_tab = wait.until(EC.element_to_be_clickable((By.ID, "processingTab")))
        processing_tab.click()
        time.sleep(3)

        # Open Dashboard
        dashboard_xpath = f"//a[@href='/officer/TenderDashboard.jsp?tenderid={tender_id}']"
        dashboard_link = wait.until(EC.element_to_be_clickable((By.XPATH, dashboard_xpath)))
        dashboard_link.click()
        time.sleep(3)

        # Open Evaluation Committee
        eval_comm_xpath = f"//a[contains(@href,'/officer/EvalComm.jsp?tenderid={tender_id}')]"
        eval_comm_link = wait.until(EC.element_to_be_clickable((By.XPATH, eval_comm_xpath)))
        eval_comm_link.click()
        time.sleep(3)

        # Click Clarification Tab
        clarification_tab = wait.until(EC.element_to_be_clickable((By.ID, "tbClari")))
        clarification_tab.click()
        time.sleep(3)
        
        return True
    except Exception as e:
        st.error(f"❌ NAVIGATION ERROR: {str(e)}")
        return False

def process_tenderer_forms(driver, wait, remark_text, tenderer_name, status_text, current_num=None, total_num=None):
    """Process all forms for a specific tenderer that have 'Evaluate Form' action"""
    forms_processed = 0
    forms_skipped = 0
    
    try:
        time.sleep(3)
        
        # Loop to process all pending forms
        while True:
            try:
                # Find all form rows in the table
                form_rows = driver.find_elements(By.XPATH, "//table[contains(@class,'tableList_1')]//tr[contains(@id,'fformtr_')]")
                
                if not form_rows:
                    st.warning(f"⚠️ NO FORM ROWS FOUND FOR {tenderer_name}")
                    break
                
                # Find a form that needs evaluation (has "Evaluate Form" link)
                found_pending = False
                for form_row in form_rows:
                    try:
                        action_cell = form_row.find_element(By.XPATH, ".//td[3]")  # Action column
                        action_text = action_cell.text.strip()
                        
                        # Check if this form has "Evaluate Form" link
                        if "Evaluate Form" in action_text:
                            # This form needs evaluation
                            eval_form_link = action_cell.find_element(By.XPATH, ".//a[contains(text(),'Evaluate Form')]")
                            
                            # Get form name for logging
                            try:
                                form_name = form_row.find_element(By.XPATH, ".//td[1]//a").text.strip()
                            except:
                                form_name = "FORM"
                            
                            forms_processed += 1
                            
                            # Update status with current form being processed
                            if current_num and total_num:
                                status_text.markdown(
                                    f"<h5 style='color: #ff0066;'>🔹 [{current_num}/{total_num}] FORM #{forms_processed}: {form_name[:40]}...</h5>", 
                                    unsafe_allow_html=True
                                )
                            else:
                                status_text.markdown(
                                    f"<h5 style='color: #ff0066;'>🔹 FORM #{forms_processed}: {form_name[:50]}...</h5>", 
                                    unsafe_allow_html=True
                                )
                            
                            # Click the evaluate form link
                            driver.execute_script("arguments[0].scrollIntoView(true);", eval_form_link)
                            time.sleep(0.5)
                            eval_form_link.click()
                            time.sleep(3)
                            
                            # Fill out and submit the form
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
                            
                            # Handle any alerts
                            try:
                                WebDriverWait(driver, 2).until(EC.alert_is_present())
                                alert = driver.switch_to.alert
                                alert_text = alert.text
                                alert.accept()
                            except:
                                pass
                            
                            st.success(f"   ✅ FORM #{forms_processed} SUBMITTED: {form_name[:60]}")
                            
                            # Wait for the page to automatically navigate back
                            time.sleep(3)
                            
                            found_pending = True
                            break  # Exit inner loop to re-check forms
                            
                        elif "Form Evaluated" in action_text:
                            # This form is already evaluated, skip it
                            forms_skipped += 1
                    except:
                        continue
                
                # If no pending forms found, we're done
                if not found_pending:
                    if forms_processed > 0:
                        st.info(f"✅ COMPLETED {tenderer_name}: {forms_processed} forms processed, {forms_skipped} already evaluated")
                    else:
                        st.info(f"ℹ️ {tenderer_name}: All {forms_skipped} forms already evaluated")
                    break
                    
            except Exception as inner_error:
                st.error(f"   ❌ ERROR IN FORM PROCESSING LOOP: {str(inner_error)}")
                break
    
    except Exception as e:
        st.error(f"❌ ERROR PROCESSING FORMS FOR {tenderer_name}: {str(e)}")
    
    return forms_processed

def run_automation(email, password, tender_id, remark_text, start_from=0):
    """Main automation function"""
    driver = None
    csv_data = []
    
    try:
        # CSV Headers
        csv_data.append(['Timestamp', 'Tenderer_Num', 'Tenderer_Name', 'Status', 'Forms_Count', 'Error'])
        
        # Initialize Chrome driver
        driver = get_chrome_driver()
        wait = WebDriverWait(driver, 10)

        driver.get("https://www.eprocure.gov.bd")
        time.sleep(3)

        # Login
        driver.find_element(By.ID, "txtEmailId").send_keys(email)
        driver.find_element(By.ID, "txtPassword").send_keys(password)
        driver.find_element(By.ID, "btnLogin").click()
        time.sleep(5)

        # Handle update prompt if exists
        try:
            driver.find_element(By.ID, "btnUpdateLater").click()
            st.success("✅ UPDATE PROMPT BYPASSED")
        except:
            st.info("⚡ NO UPDATE PROMPT DETECTED")

        # INITIAL NAVIGATION: Navigate to Clarification tab to get tenderer count
        st.info("🔄 INITIAL NAVIGATION TO CLARIFICATION PAGE...")
        if not navigate_to_clarification(driver, tender_id):
            raise Exception("Failed to navigate to Clarification page")
        
        st.success("✅ CLARIFICATION INTERFACE ACTIVE")
        st.subheader("📊 DETECTING TENDERERS")
        
        # Find the tenderers table
        tables = driver.find_elements(By.CSS_SELECTOR, "table.tableList_1")
        target_table = None
        
        for table in tables:
            try:
                headers = table.find_elements(By.TAG_NAME, "th")
                header_texts = [h.text.strip() for h in headers]
                
                if ("S. No." in header_texts and 
                    "List of Tenderers" in header_texts and 
                    "Action" in header_texts):
                    target_table = table
                    break
            except:
                continue
        
        if not target_table:
            st.error("❌ TENDERERS TABLE NOT FOUND IN SYSTEM")
            raise Exception("Tenderers table not found")
        
        # Get total count of tenderers
        tenderer_rows = target_table.find_elements(By.XPATH, ".//tr[position()>1 and td]")
        total_tenderers = len(tenderer_rows)
        
        st.success(f"🎯 DETECTED {total_tenderers} TENDERERS FOR PROCESSING")
        
        # Apply skip/start_from logic
        if start_from > 0:
            if start_from >= total_tenderers:
                st.error(f"❌ SKIP VALUE ({start_from}) IS GREATER THAN OR EQUAL TO TOTAL TENDERERS ({total_tenderers})")
                return
            st.warning(f"⏭️ SKIPPING FIRST {start_from} TENDERERS - STARTING FROM TENDERER #{start_from + 1}")
        
        # Collect all tenderer info upfront
        st.info("📋 Collecting tenderer information...")
        tenderer_info = []
        for idx in range(start_from, total_tenderers):
            try:
                row = tenderer_rows[idx]
                name = row.find_element(By.XPATH, ".//td[2]").text.strip()
                tenderer_info.append((idx + 1, name))
            except:
                tenderer_info.append((idx + 1, f"TENDERER_{idx + 1}"))
        
        st.success(f"✅ Collected {len(tenderer_info)} tenderers")
        
        # Sidebar for progress and download
        with st.sidebar:
            st.subheader("📊 PROGRESS")
            sidebar_progress = st.progress(0)
            sidebar_status = st.empty()
            st.divider()
            st.subheader("💾 DOWNLOAD LOG")
            st.info("⚠️ Download will be available after automation completes")
            download_placeholder = st.empty()
        
        # Main area for logs (newest at top)
        log_container = st.empty()
        log_messages = []
        
        def update_logs():
            """Update log display with current messages"""
            log_html = ""
            for msg in log_messages[:30]:  # Show last 30 messages
                if "❌" in msg or "FAILED" in msg:
                    color = "#ff0066"
                elif "✅" in msg or "COMPLETED" in msg:
                    color = "#00ff88"
                else:
                    color = "#00ffff"
                log_html += f"<p style='color: {color}; font-size: 14px; margin: 2px 0;'>{msg}</p>"
            log_container.markdown(log_html, unsafe_allow_html=True)
        
        successful_tenderers = 0
        failed_tenderers = 0
        skipped_tenderers = start_from
        
        # Store original window handle
        original_window = driver.current_window_handle
        
        # Process each tenderer by opening in new duplicated tab
        for i, (tenderer_num, tenderer_name) in enumerate(tenderer_info):
            try:
                # Update sidebar progress
                sidebar_progress.progress((i + 1) / len(tenderer_info))
                sidebar_status.markdown(f"**#{tenderer_num}/{total_tenderers}**")
                
                # Add to top of log messages
                log_messages.insert(0, f"⚡ PROCESSING #{tenderer_num}/{total_tenderers}: {tenderer_name[:50]}")
                update_logs()
                
                # Duplicate current tab
                log_messages.insert(0, f"📑 Opening new tab for: {tenderer_name[:50]}")
                update_logs()
                
                driver.execute_script("window.open(arguments[0]);", driver.current_url)
                time.sleep(2)
                
                # Switch to new tab
                new_window = [w for w in driver.window_handles if w != original_window][0]
                driver.switch_to.window(new_window)
                time.sleep(2)
                
                # Find tenderer table in new tab
                tables = driver.find_elements(By.CSS_SELECTOR, "table.tableList_1")
                target_table = None
                
                for table in tables:
                    try:
                        headers = table.find_elements(By.TAG_NAME, "th")
                        header_texts = [h.text.strip() for h in headers]
                        if ("S. No." in header_texts and "List of Tenderers" in header_texts):
                            target_table = table
                            break
                    except:
                        continue
                
                if not target_table:
                    raise Exception("Table not found in new tab")
                
                # Find the specific tenderer row by name
                tenderer_rows_new = target_table.find_elements(By.XPATH, ".//tr[position()>1 and td]")
                target_row = None
                
                for row in tenderer_rows_new:
                    try:
                        name_cell = row.find_element(By.XPATH, ".//td[2]")
                        if name_cell.text.strip() == tenderer_name:
                            target_row = row
                            break
                    except:
                        continue
                
                if not target_row:
                    raise Exception("Tenderer not found in new tab")
                
                # Click action link
                action_cell = target_row.find_element(By.XPATH, ".//td[4]")
                
                try:
                    eval_link = action_cell.find_element(By.XPATH, ".//a[contains(text(),'Evaluate Tenderer')]")
                    log_messages.insert(0, f"✅ FOUND 'EVALUATE TENDERER' LINK")
                    update_logs()
                    driver.execute_script("arguments[0].scrollIntoView(true);", eval_link)
                    time.sleep(0.5)
                    eval_link.click()
                    time.sleep(4)
                except:
                    try:
                        edit_link = action_cell.find_element(By.XPATH, ".//a[contains(text(),'Edit')]")
                        log_messages.insert(0, f"✅ FOUND 'EDIT' LINK (Already Evaluated)")
                        update_logs()
                        driver.execute_script("arguments[0].scrollIntoView(true);", edit_link)
                        time.sleep(0.5)
                        edit_link.click()
                        time.sleep(4)
                    except:
                        raise Exception("No action link found")
                
                # Process forms
                status_text = st.empty()  # Dummy for compatibility
                forms_count = process_tenderer_forms(driver, wait, remark_text, tenderer_name, status_text, tenderer_num, total_tenderers)
                
                # Log to CSV
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                csv_data.append([timestamp, tenderer_num, tenderer_name, "SUCCESS", forms_count, ""])
                
                # Close new tab and switch back to original
                driver.close()
                driver.switch_to.window(original_window)
                time.sleep(1)
                
                log_messages.insert(0, f"✅ COMPLETED: {tenderer_name[:50]} ({forms_count} forms)")
                update_logs()
                
                successful_tenderers += 1
                
                # Update CSV data in session state to avoid rerun issues
                if 'csv_data' not in st.session_state:
                    st.session_state.csv_data = []
                st.session_state.csv_data = csv_data
                
            except Exception as tenderer_error:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                csv_data.append([timestamp, tenderer_num, tenderer_name, "FAILED", 0, str(tenderer_error)])
                
                log_messages.insert(0, f"❌ FAILED: {tenderer_name[:50]} - {str(tenderer_error)[:30]}")
                update_logs()
                
                # Update CSV data in session state
                if 'csv_data' not in st.session_state:
                    st.session_state.csv_data = []
                st.session_state.csv_data = csv_data
                
                # Make sure we're back on original window
                try:
                    driver.close()
                except:
                    pass
                try:
                    driver.switch_to.window(original_window)
                except:
                    pass
                
                failed_tenderers += 1
                continue
        
        # Store final CSV data
        st.session_state.csv_data = csv_data
        
        sidebar_progress.progress(1.0)
        sidebar_status.markdown("**✅ COMPLETE**")
        
        # Now show download button (won't cause rerun since automation is done)
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerows(csv_data)
        
        download_placeholder.download_button(
            label=f"📥 Download Log ({len(csv_data)-1} entries)",
            data=csv_buffer.getvalue(),
            file_name=f"log_{tender_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
        
        st.success("🎯 AUTOMATION SUCCESSFULLY EXECUTED")
        st.markdown(f"""
        <div class="main-container">
        <h3 style="text-align: center;">📊 EXECUTION SUMMARY</h3>
        <p style="text-align: center; font-size: 18px;">
        <strong>TOTAL TENDERERS:</strong> {total_tenderers}<br>
        <strong style="color: #ffc107;">SKIPPED:</strong> {skipped_tenderers}<br>
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
        if driver is not None:
            st.info("🔄 BROWSER SHUTDOWN IN 10 SECONDS...")
            time.sleep(10)
            driver.quit()
            st.info("✅ BROWSER TERMINATED")