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

def process_tenderer_forms(driver, wait, remark_text, tenderer_name):
    """Process all forms for a specific tenderer"""
    forms_processed = 0
    
    try:
        time.sleep(2)
        
        # Loop to process all pending forms for this tenderer
        while True:
            try:
                # Find the next form to evaluate
                form_row = driver.find_element(By.XPATH, "//table[contains(@class,'tableList_1')]//tr[td[contains(text(),'Pending')]]//ancestor::tr[contains(@id,'fformtr_')]")
                
                # Find the "Evaluate Form" link within that row
                eval_form_link = form_row.find_element(By.XPATH, ".//a[contains(text(),'Evaluate Form')]")
                
                # Click the link to open the form
                driver.execute_script("arguments[0].scrollIntoView(true);", eval_form_link)
                time.sleep(0.5)
                eval_form_link.click()
                time.sleep(3)
                
                forms_processed += 1
                st.info(f"   🔹 EXECUTING FORM #{forms_processed}")
                
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
                
                st.success(f"   ✅ FORM #{forms_processed} SUBMITTED SUCCESSFULLY")
                
                # Wait for the page to automatically navigate back
                time.sleep(3)
                
            except (NoSuchElementException, TimeoutException):
                # If we can't find another "Pending" form, we're done
                if forms_processed > 0:
                    st.info(f"✅ ALL PENDING FORMS PROCESSED FOR {tenderer_name}. Total: {forms_processed}")
                else:
                    st.warning(f"⚠️ NO PENDING FORMS FOUND FOR {tenderer_name}")
                break
            except Exception as inner_error:
                st.error(f"   ❌ FORM PROCESSING ERROR: {str(inner_error)}")
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
                    st.info(f"✅ FOUND TARGET TABLE WITH HEADERS: {header_texts}")
                    break
            except:
                continue
        
        if not target_table:
            st.error("❌ TENDERERS TABLE NOT FOUND IN SYSTEM")
            raise Exception("Tenderers table not found")
        
        # Get all tenderer rows and extract their info
        tenderer_rows = target_table.find_elements(By.XPATH, ".//tr[position()>1 and td]")
        total_tenderers = len(tenderer_rows)
        st.info(f"🎯 DETECTED {total_tenderers} TENDERERS FOR PROCESSING")
        
        # Extract tenderer data (name and evaluation link) before opening windows
        tenderers_data = []
        for idx, row in enumerate(tenderer_rows):
            try:
                tenderer_name = row.find_element(By.XPATH, ".//td[2]").text.strip()
                eval_link_element = row.find_element(By.XPATH, ".//td[4]//a[contains(text(),'Evaluate Tenderer')]")
                eval_link_url = eval_link_element.get_attribute('href')
                
                tenderers_data.append({
                    'index': idx + 1,
                    'name': tenderer_name,
                    'url': eval_link_url
                })
                st.info(f"📋 Tenderer #{idx+1}: {tenderer_name}")
            except Exception as e:
                st.warning(f"⚠️ Could not extract data for tenderer #{idx+1}: {str(e)}")
        
        st.info(f"✅ EXTRACTED DATA FOR {len(tenderers_data)} TENDERERS")
        
        # Store the main window handle
        main_window = driver.current_window_handle
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        successful_tenderers = 0
        failed_tenderers = 0
        
        # Process each tenderer in a new window
        for tenderer_data in tenderers_data:
            idx = tenderer_data['index']
            tenderer_name = tenderer_data['name']
            eval_url = tenderer_data['url']
            
            try:
                progress_bar.progress(idx / total_tenderers)
                status_text.markdown(f"<h5 style='color: #ff0066;'>⚡ PROCESSING: {tenderer_name} ({idx}/{total_tenderers})</h5>", unsafe_allow_html=True)
                
                # Open evaluation page in a new window
                st.info(f"🪟 OPENING NEW WINDOW FOR: {tenderer_name}")
                driver.execute_script("window.open('');")
                
                # Switch to the new window
                driver.switch_to.window(driver.window_handles[-1])
                
                # Navigate to the evaluation page
                driver.get(eval_url)
                time.sleep(4)
                
                st.info(f"✅ [{idx}/{total_tenderers}] EVALUATION PAGE LOADED: {tenderer_name}")
                
                # Process all forms for this tenderer
                forms_count = process_tenderer_forms(driver, wait, remark_text, tenderer_name)
                
                if forms_count > 0:
                    successful_tenderers += 1
                else:
                    successful_tenderers += 1  # Still count as success if no forms to process
                
                # Close the current window
                st.info(f"🔒 CLOSING WINDOW FOR: {tenderer_name}")
                driver.close()
                
                # Switch back to the main window (Clarification page)
                driver.switch_to.window(main_window)
                st.info("✅ RETURNED TO MAIN CLARIFICATION PAGE")
                time.sleep(1)
                
            except Exception as tenderer_error:
                st.error(f"❌ ERROR PROCESSING {tenderer_name}: {str(tenderer_error)}")
                failed_tenderers += 1
                
                # Try to close any extra windows and return to main window
                try:
                    current_windows = driver.window_handles
                    for window in current_windows:
                        if window != main_window:
                            driver.switch_to.window(window)
                            driver.close()
                    driver.switch_to.window(main_window)
                    st.info("🔄 RECOVERED TO MAIN WINDOW")
                except:
                    st.warning("⚠️ COULD NOT RECOVER TO MAIN WINDOW")
                
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