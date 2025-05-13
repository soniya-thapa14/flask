import time
import base64
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def generate_pdf():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)

    url = "https://hamropahuch.axisoftech.com/billing/bill/view_bill_details/1"
    driver.get(url)
    time.sleep(3)  
    driver.execute_script("document.getElementById('page-wrap').scrollIntoView();")
    time.sleep(1)

    devtools = driver.execute_cdp_cmd

    pdf_data = devtools("Page.printToPDF", {
        "printBackground": True,
        "preferCSSPageSize": True,
    })


    unique_id = uuid.uuid4().hex
    pdf_path = f"page-wrapper_{unique_id}.pdf"
    with open(pdf_path, "wb") as f:
        f.write(base64.b64decode(pdf_data['data']))

    driver.quit()
    print(f"{pdf_path} generated successfully")
    return pdf_path
generate_pdf()

