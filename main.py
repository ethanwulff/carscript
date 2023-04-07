import sys

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from test import TEST_OUTPUT
from config import USERNAME, PASSWORD

TESTING_MODE = False

LOGIN_URL = 'https://spark.auctionedge.com/login'
SN_URL = 'https://spark.auctionedge.com/details/vehicles?sn='

def writeToFile(data):
    file = open("example.html", "w")
    file.write(data)
    file.close()

def waitForElement(browser, selector):
    try:
        # Wait for up to 10 seconds for the specified element to be visible
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    except TimeoutException:
        print("Login was unsuccessful or the page took too long to load.")
        browser.quit()
        exit()

def loginToSpark(browser):
    browser.get(LOGIN_URL)

    username_field = browser.find_element(By.CSS_SELECTOR, '[autocomplete="username"]')
    password_field = browser.find_element(By.CSS_SELECTOR, '[autocomplete="current-password"]')

    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)

    login_button = browser.find_element(By.CSS_SELECTOR, '[type="submit"]')
    login_button.click()

    waitForElement(browser, '[data-test="SearchCard-widget"]')

def parseResults(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    writeToFile(soup.prettify())

    vehicle_details = {}
    sale_information = {}

    vehicle_details_section = soup.find(class_='emot-1k6141t ebacqer4')
    vehicle_details_labels = vehicle_details_section.find_all(class_='emot-13qlwbb eb0wyyv3')
    vehicle_details_values = vehicle_details_section.find_all(class_='MuiTypography-root MuiTypography-body1 eb0wyyv0 emot-h7u0w9')

    for label, value in zip(vehicle_details_labels, vehicle_details_values):
        key = label.get_text().strip()
        vehicle_details[key] = value.get_text().strip()

    sale_information_section = soup.find_all(class_='emot-1k6141t ebacqer4')[1]
    sale_information_labels = sale_information_section.find_all(class_='emot-13qlwbb eb0wyyv3')
    sale_information_values = sale_information_section.find_all(class_='MuiTypography-root MuiTypography-body1 eb0wyyv0 emot-h7u0w9')

    for label, value in zip(sale_information_labels, sale_information_values):
        key = label.get_text().strip()
        sale_information[key] = value.get_text().strip()

    result = {
        'vehicle_details': vehicle_details,
        'sale_information': sale_information,
    }

    return result

def getDataFromPage(sn_number):
    # Set up a headless browser
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True) # Uncomment this line to keep the browser open after the script finishes
    #chrome_options.add_argument("--headless")

    driver_path = "/chromedriver_win32/chromedriver.exe"
    browser = webdriver.Chrome(executable_path=driver_path, options=chrome_options)

    loginToSpark(browser)

    #pick DAA Seattle
    dropdown = browser.find_element(By.CSS_SELECTOR, '[aria-haspopup="listbox"]')
    dropdown.click()
    dropdown_option = browser.find_element(By.CSS_SELECTOR, '[data-value="daas"]')
    dropdown_option.click()
    waitForElement(browser, '[data-test="SearchCard-widget"]')

    browser.get(SN_URL + sn_number)
    waitForElement(browser, '[xmlns="http://www.w3.org/2000/svg"]')

    page_source = browser.page_source

    return parseResults(browser.page_source)


input_value = sys.argv[1]

if TESTING_MODE:
    output = TEST_OUTPUT
else:
    output = getDataFromPage(input_value)

print(output)

csv_data = (
    f"{output['vehicle_details']['VIN'][-6:]},"
    f"{output['vehicle_details']['Stock #']},"
    f"{output['sale_information']['Sale Status']},"
    f"{output['sale_information']['Buyer']},"
    f"{output['sale_information']['Buyer Account #']}"
)

print(csv_data)


