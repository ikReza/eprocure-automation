import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

        # Navigate to My Tenders
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

        # Click Processing Tab
        driver.find_element(By.ID, "processingTab").click()
        time.sleep(3)
        st.success("✅ PROCESSING TAB ACTIVATED")

        # Open Dashboard
        dashboard_xpath = f"//a[@href='/officer/TenderDashboard.jsp?tenderid={tender_id}']"
        driver.find_element(By.XPATH, dashboard_xpath).click()
        time.sleep(3)
        st.success("✅ DASHBOARD MODULE LOADED")

        # Open Evaluation Committee
        driver.find_element(By.XPATH, f"//a[contains(@href,'/officer/EvalComm.jsp?tenderid={tender_id}')]").click()
        time.sleep(3)
        st.success("✅ EVALUATION MODULE INITIALIZED")

        # Click Clarification Tab
        driver.find_element(By.ID, "tbClari").click()
        time.sleep(3)
        st.success("✅ CLARIFICATION INTERFACE ACTIVE")

        st.subheader("📊 PROCESSING TENDERERS")
        
        # Find the correct table with "S. No.", "List of Tenderers", "Clarification Status", "Action" headers
        tables = driver.find_elements(By.CSS_SELECTOR, "table.tableList_1")
        target_table = None
        
        for table in tables:
            try:
                headers = table.find_elements(By.TAG_NAME, "th")
                header_texts = [h.text.strip() for h in headers]
                
                # Check if this table has the correct headers
                if ("S. No." in header_texts and 
                    "List of Tenderers" in header_texts and 
                    "Action" in header_texts):
                    target_table = table
                    st.info(f"✅ FOUND TARGET TABLE WITH HEADERS: {header_texts}")
                    break
            except:
                continue
        
        if not target_table:
            st.error("❌ TENDERERS TABLE NOT FOUND IN SYSTEM")
            raise Exception("Tenderers table not found")
        
        # Get all tenderer rows (skip header row)
        tenderer_rows = target_table.find_elements(By.XPATH, ".//tr[position()>1 and td]")
        total_tenderers = len(tenderer_rows)
        st.info(f"🎯 DETECTED {total_tenderers} TENDERERS FOR PROCESSING")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        successful_tenderers = 0
        failed_tenderers = 0
        
        for idx in range(total_tenderers):
            try:
                # Re-fetch the table and rows to avoid stale element references
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
                    st.error(f"❌ COULD NOT RE-LOCATE TABLE FOR TENDERER #{idx+1}")
                    failed_tenderers += 1
                    continue
                
                tenderer_rows = target_table.find_elements(By.XPATH, ".//tr[position()>1 and td]")
                
                if idx >= len(tenderer_rows):
                    st.warning(f"⚠️ TENDERER #{idx+1} NOT FOUND AFTER REFRESH")
                    failed_tenderers += 1
                    continue
                
                row = tenderer_rows[idx]
                
                progress_bar.progress((idx + 1) / total_tenderers)
                
                try:
                    # Get tenderer name from 2nd column
                    tenderer_name = row.find_element(By.XPATH, ".//td[2]").text.strip()
                except:
                    tenderer_name = f"TENDERER #{idx+1}"
                
                status_text.markdown(f"<h5 style='color: #ff0066;'>⚡ PROCESSING: {tenderer_name} ({idx+1}/{total_tenderers})</h5>", unsafe_allow_html=True)
                
                # Find "Evaluate Tenderer" link in the Action column (4th column)
                try:
                    eval_link = row.find_element(By.XPATH, ".//td[4]//a[contains(text(),'Evaluate Tenderer')]")
                    driver.execute_script("arguments[0].scrollIntoView(true);", eval_link)
                    time.sleep(0.5)
                    eval_link.click()
                    time.sleep(3)
                    
                    st.info(f"✅ [{idx+1}/{total_tenderers}] EVALUATION PAGE LOADED: {tenderer_name}")
                except Exception as link_error:
                    st.warning(f"⚠️ NO 'EVALUATE TENDERER' LINK FOR {tenderer_name}: {str(link_error)}")
                    failed_tenderers += 1
                    continue
                
                # Process forms - REVISED LOGIC
                try:
                    time.sleep(2)
                    
                    # Loop to process all pending forms for this tenderer
                    forms_processed_for_tenderer = 0
                    while True:
                        try:
                            # Find the next form to evaluate
                            # We look for a row with "Pending" status and an "Evaluate Form" link
                            form_row = driver.find_element(By.XPATH, "//table[contains(@class,'tableList_1')]//tr[td[contains(text(),'Pending')]]//ancestor::tr[contains(@id,'fformtr_')]")
                            
                            # Find the "Evaluate Form" link within that row
                            eval_form_link = form_row.find_element(By.XPATH, ".//a[contains(text(),'Evaluate Form')]")
                            
                            # Click the link to open the form
                            driver.execute_script("arguments[0].scrollIntoView(true);", eval_form_link)
                            time.sleep(0.5)
                            eval_form_link.click()
                            time.sleep(3)
                            
                            forms_processed_for_tenderer += 1
                            st.info(f"   🔹 EXECUTING FORM #{forms_processed_for_tenderer}")
                            
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
                            
                            st.success(f"   ✅ FORM #{forms_processed_for_tenderer} SUBMITTED SUCCESSFULLY")
                            
                            # CRITICAL: Wait for the page to automatically navigate back
                            time.sleep(3)
                            
                        except Exception as inner_error:
                            # If we can't find another "Pending" form, we're done with this tenderer
                            if "no such element" in str(inner_error).lower():
                                st.info(f"✅ ALL PENDING FORMS PROCESSED FOR {tenderer_name}. Total: {forms_processed_for_tenderer}")
                                break
                            else:
                                st.error(f"   ❌ AN ERROR OCCURRED: {str(inner_error)}")
                                break
                    
                    if forms_processed_for_tenderer > 0:
                        successful_tenderers += 1
                    else:
                        st.warning(f"⚠️ NO PENDING FORMS FOUND FOR {tenderer_name}")
                        successful_tenderers += 1 # Count as success since nothing to do
                
                except Exception as forms_error:
                    st.error(f"❌ FORMS PROCESSING ERROR FOR {tenderer_name}: {str(forms_error)}")
                    failed_tenderers += 1
                
                # Navigate back to the main tenderers list
                driver.back()
                time.sleep(3)
                
            except Exception as tenderer_error:
                st.error(f"❌ TENDERER #{idx+1} PROCESSING ERROR: {str(tenderer_error)}")
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
        if driver is not None:
            st.info("🔄 BROWSER SHUTDOWN IN 10 SECONDS...")
            time.sleep(10)
            driver.quit()
            st.info("✅ BROWSER TERMINATED")