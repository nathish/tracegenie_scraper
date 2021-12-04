#!/usr/bin/env python

import os
import re
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
pd.options.mode.chained_assignment = None
import argparse
from pathlib import Path
from getpass import getpass

parser = argparse.ArgumentParser(description='tracegenie to CSV web scraper')
parser.add_argument('-p','--postcode', help='Specify postcode district', required=True)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-n','--name', help='Specify surname')
group.add_argument('-f','--file', help='Specify file path')
args = vars(parser.parse_args())

surname = args['name']
district = args['postcode']
filepath = args['file']
options = Options()
options.headless = True
options.add_argument("--log-level=3")
output=Path(district+"_addresses.csv")
delay = 6

usr = input("username:")
pw = getpass("password:")

usr = manchester_spanish

def login():
    login.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    login.driver.get("https://www.tracegenie.com")

    # login
    username = login.driver.find_element_by_name("amember_login")
    password = login.driver.find_element_by_name("amember_pass")
    loginB = login.driver.find_element_by_xpath("//input[@value='Login']")

    username.send_keys(usr)
    password.send_keys(pw)
    loginB.click()

    # click search area
    try:
        searchA =  WebDriverWait(login.driver, delay).until(EC.presence_of_element_located((By.ID, 'resource-link-folder-3')))
        searchA.click()
    except:
        print("Loading took too long! Trying again")
        login()

def search():
    # search function
    searchLN = login.driver.find_element_by_xpath("//input[@value='Rogers']")
    searchFN =login. driver.find_element_by_xpath("//input[@value='Ben*']")
    searchW = login.driver.find_element_by_xpath("//input[@value='london']")
    tick = login.driver.find_element_by_xpath("//input[@id='check21']")
    search = login.driver.find_element_by_xpath("//input[@id='ajax_bt1']")

    searchLN.send_keys(surname)
    searchFN.send_keys("")
    searchW.send_keys(district)
    tick.click()
    search.click()

    a_data = []
    login.driver.switch_to.frame(login.driver.find_element_by_name("iframe_a"))
    tables = login.driver.find_elements_by_xpath("//table[@class='table table-hover table-curved']")
    if tables:
        for table in tables:
            table = table.get_attribute('outerHTML').replace("<br>", '\n')
            data = pd.read_html(table)
            df = data[0]
            df = df.iloc[:, :-1]
            name = df.columns[1]
            df.rename(columns={ df.columns[1]: "Name" }, inplace = True)
            df['Name'] = df['Name'].replace(['Voter status'], name)
            df = df.loc[[0]]
            a_data.append(df)
        df = pd.concat(a_data)
        print(df)
        df.to_csv(output, mode="a", header=h, index=False)
    else:
        print("no addresses found for surname: "+surname)
    login.driver.close()

if surname:
    login()
    h=True
    search()
elif filepath:
    with open(filepath) as fp:
        content = fp.readlines()
        for line in content:
            login()
            surname=line
            if output.is_file():
                h=False
            else:
                h=True
            search()
