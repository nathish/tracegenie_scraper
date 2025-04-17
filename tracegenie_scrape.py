#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import argparse
from pathlib import Path
from getpass import getpass
import pandas as pd
pd.options.mode.chained_assignment = None
from io import StringIO

parser = argparse.ArgumentParser(description='tracegenie to CSV web scraper')
parser.add_argument('-p', '--postcode',
                    help='Specify postcode district', required=True)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-n', '--name',
                    help='Specify surname')
group.add_argument('-f', '--file',
                    help='Specify file path')
parser.add_argument('-o', '--output',
                    help='Specify output file')
args = vars(parser.parse_args())

surname = args['name']
district = args['postcode']
filepath = args['file']
options = Options()
options.headless = True
options.add_argument("--log-level=3")
if args['output']:
    output = Path(args['output'])
delay = 6

usr = input("username:")
pw = getpass("password:")

# --- HARDCODED CHROMEDRIVER PATH ---
CHROMEDRIVER_PATH = "/nix/store/qhw3psnfrd203ghzmjdllq7cw6layaw3-chromedriver-unwrapped-132.0.6834.110/bin/chromedriver"

def login():
    try:
        login.driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Error during WebDriver initialization: {e}")
        print(f"Make sure the ChromeDriver is in your system's PATH or you specify the executable_path.")
        raise
    login.driver.get("https://www.tracegenie.com")

    # login
    username = login.driver.find_element(By.NAME, "amember_login")
    password = login.driver.find_element(By.NAME, "amember_pass")
    loginB = login.driver.find_element(By.XPATH, "//input[@value='Login']")

    username.send_keys(usr)
    password.send_keys(pw)
    loginB.click()

    # click search area
    try:
        searchA = WebDriverWait(login.driver, delay).until(
            EC.presence_of_element_located((By.ID, 'resource-link-folder-3'))
        )
        searchA.click()
    except:
        print("Loading took too long! Trying again")
        login()

def search():
    # search function
    searchLN = login.driver.find_element(By.XPATH, "//input[@value='Rogers']")
    searchFN = login.driver.find_element(By.XPATH, "//input[@value='Ben*']")
    searchW = login.driver.find_element(By.XPATH, "//input[@value='london']")
    tick = login.driver.find_element(By.XPATH, "//input[@id='check25']")
    search_button = login.driver.find_element(By.XPATH, "//input[@id='ajax_bt1']")

    searchLN.send_keys(surname)
    searchFN.send_keys("")
    searchW.send_keys(district)
    tick.click()
    search_button.click()

    a_data = []
    try:
        # Wait for the iframe to be available and switch to it
        WebDriverWait(login.driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, "iframe_a"))
        )

        # Check for "zero results" text
        try:
            zero_results_element = WebDriverWait(login.driver, 5).until(
                EC.text_to_be_present_in_element((By.XPATH, "/html/body/font/font/p[1]"), "zero results")
            )
            print(f"No addresses found for surname: {surname}")
            return  # Move to the next name
        except Exception as e:
            if "Message: " in str(e):
                pass # This was a timeout, "zero results" not found.
            else:
                print(f"An error occurred while checking for 'zero results': {e}")
                print(traceback.format_exc())
                return

        # Wait for at least one table with the specified class to be present
        WebDriverWait(login.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//table[@class='table table-hover table-curved']"))
        )

        tables = login.driver.find_elements(By.XPATH, "//table[@class='table table-hover table-curved']")
        if tables:
            for table in tables:
                table_html = table.get_attribute('outerHTML').replace("<br>", '\n')
                data = pd.read_html(StringIO(table_html))
                df = data[0]
                df = df.iloc[:, :-1]
                name = df.columns[1]
                df.rename(columns={df.columns[1]: "Name"}, inplace=True)
                df['Name'] = df['Name'].replace(['Voter status'], name)
                df = df.loc[[0]]
                a_data.append(df)
            df = pd.concat(a_data)
            print(df)
            if args['output']:
                df.to_csv(output, mode="a", header=h, index=False)
        else:
            print("no addresses found for surname: " + surname)

    except Exception as e:
        print(f"An error occurred during search or data extraction: {e}")
    finally:
        login.driver.quit() # Ensure the browser closes even if there's an error

# Modify the main execution blocks to not call login.driver.close() immediately
if surname:
    login()
    h = True
    search()
elif filepath:
    with open(filepath) as fp:
        content = fp.readlines()
        for line in content:
            login()
            surname = line.strip()
            if 'output' in locals() and output.is_file():
                h = False
            else:
                h = True
            search()

