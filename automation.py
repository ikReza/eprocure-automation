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
        # Navigate to My Tenders
        actions = ActionChains(driver)
        tender_tab = driver.find_element(By.ID, "headTabTender")
        actions.move_to_element(tender_tab).perform()
        time.sleep(1)
        driver.find_element(By.XPATH, "//a[@href='/officer/MyTenders.jsp']").click()
        time.sleep(5)

        # Enter tender ID
        tender_input = driver.find_element(By.ID, "tenderId")
        tender_input.clear()
        tender_input.send_keys(tender_id)
        time.sleep(1)

        # Click Processing Tab
        driver.find_element(By.ID, "processingTab").click()
        time.sleep(3)

        # Open Dashboard
        dashboard_xpath = f"//a[@href='/officer/TenderDashboard.jsp?tenderid={tender_id}']"
        driver.find_element(By.XPATH, dashboard_xpath).click()
        time.sleep(3)

        # Open Evaluation Committee
        driver.find_element(By.XPATH, f"//a[contains(@href,'/officer/EvalComm.jsp?tenderid={tender_id}')]").click()
        time.sleep(3)

        # Click Clarification Tab
        driver.find_element(By.ID, "tbClari").click()
        time.sleep(3)
        
        return True
    except Exception as e:
        st.error(f"❌ NAVIGATION ERROR: {str(e)}")
        return False

def process_tenderer_forms(driver, wait, remark_text, tenderer_name):
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
                            
                            # Click the evaluate form link
                            driver.execute_script("arguments[0].scrollIntoView(true);", eval_form_link)
                            time.sleep(0.5)
                            eval_form_link.click()
                            time.sleep(3)
                            
                            forms_processed += 1
                            st.info(f"   🔹 EXECUTING FORM: {form_name}")
                            
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
                                st.info(f"   ℹ️ SYSTEM ALERT: {alert_text}")
                            except:
                                pass
                            
                            st.success(f"   ✅ FORM SUBMITTED: {form_name}")
                            
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
                        st.info(f"✅ ALL PENDING FORMS PROCESSED FOR {tenderer_name}. Processed: {forms_processed}, Already Evaluated: {forms_skipped}")
                    else:
                        st.info(f"ℹ️ NO PENDING FORMS FOR {tenderer_name}. All {forms_skipped} forms already evaluated.")
                    break
                    
            except Exception as inner_error:
                st.error(f"   ❌ ERROR IN FORM PROCESSING LOOP: {str(inner_error)}")
                break
    
    except Exception as e:
        st.error(f"❌ ERROR PROCESSING FORMS FOR {tenderer_name}: {str(e)}")
    
    return forms_processed

def run_automation(email, password, tender_id, remark_text):
    """Main automation function"""
    driver = None
    try:
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
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        successful_tenderers = 0
        failed_tenderers = 0
        
        # Process each tenderer by index
        for idx in range(total_tenderers):
            try:
                current_tenderer_num = idx + 1
                progress_bar.progress(current_tenderer_num / total_tenderers)
                status_text.markdown(f"<h5 style='color: #ff0066;'>⚡ PROCESSING TENDERER #{current_tenderer_num}/{total_tenderers}</h5>", unsafe_allow_html=True)
                
                # Navigate to Clarification page
                st.info(f"🔄 NAVIGATING TO CLARIFICATION FOR TENDERER #{current_tenderer_num}")
                if not navigate_to_clarification(driver, tender_id):
                    st.error(f"❌ FAILED TO NAVIGATE FOR TENDERER #{current_tenderer_num}")
                    failed_tenderers += 1
                    continue
                
                time.sleep(2)
                
                # Find the tenderers table again
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
                    st.error(f"❌ COULD NOT FIND TENDERERS TABLE FOR TENDERER #{current_tenderer_num}")
                    failed_tenderers += 1
                    continue
                
                # Get the specific tenderer row by index
                tenderer_rows = target_table.find_elements(By.XPATH, ".//tr[position()>1 and td]")
                
                if idx >= len(tenderer_rows):
                    st.error(f"❌ TENDERER #{current_tenderer_num} NOT FOUND IN TABLE")
                    failed_tenderers += 1
                    continue
                
                target_row = tenderer_rows[idx]
                
                # Get tenderer name for logging
                try:
                    tenderer_name = target_row.find_element(By.XPATH, ".//td[2]").text.strip()
                except:
                    tenderer_name = f"TENDERER #{current_tenderer_num}"
                
                st.info(f"📋 Processing: {tenderer_name}")
                
                # Check Action column (4th column) - look for "Evaluate Tenderer" or "Edit"
                try:
                    action_cell = target_row.find_element(By.XPATH, ".//td[4]")
                    
                    # Try to find "Evaluate Tenderer" link first
                    try:
                        eval_link = action_cell.find_element(By.XPATH, ".//a[contains(text(),'Evaluate Tenderer')]")
                        st.info(f"✅ FOUND 'EVALUATE TENDERER' LINK FOR {tenderer_name}")
                        driver.execute_script("arguments[0].scrollIntoView(true);", eval_link)
                        time.sleep(0.5)
                        eval_link.click()
                        time.sleep(4)
                        st.info(f"✅ EVALUATION PAGE LOADED: {tenderer_name}")
                    except:
                        # If "Evaluate Tenderer" not found, look for "Edit" link
                        try:
                            edit_link = action_cell.find_element(By.XPATH, ".//a[contains(text(),'Edit')]")
                            st.info(f"✅ FOUND 'EDIT' LINK FOR {tenderer_name} (Already Evaluated)")
                            driver.execute_script("arguments[0].scrollIntoView(true);", edit_link)
                            time.sleep(0.5)
                            edit_link.click()
                            time.sleep(4)
                            st.info(f"✅ EDIT PAGE LOADED: {tenderer_name}")
                        except:
                            st.error(f"❌ NO 'EVALUATE TENDERER' OR 'EDIT' LINK FOUND FOR {tenderer_name}")
                            failed_tenderers += 1
                            continue
                    
                except Exception as link_error:
                    st.error(f"❌ ERROR ACCESSING ACTION CELL FOR {tenderer_name}: {str(link_error)}")
                    failed_tenderers += 1
                    continue
                
                # Process all forms for this tenderer
                forms_count = process_tenderer_forms(driver, wait, remark_text, tenderer_name)
                
                successful_tenderers += 1
                
            except Exception as tenderer_error:
                st.error(f"❌ ERROR PROCESSING TENDERER #{current_tenderer_num}: {str(tenderer_error)}")
                failed_tenderers += 1
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
        if driver is not None:
            st.info("🔄 BROWSER SHUTDOWN IN 10 SECONDS...")
            time.sleep(10)
            driver.quit()
            st.info("✅ BROWSER TERMINATED")