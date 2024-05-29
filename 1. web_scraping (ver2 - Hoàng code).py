import os
from time import sleep
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import json
import undetected_chromedriver as uc 
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import mysql.connector

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]
SPREADSHEET_ID = '1gR399rK5Ur_pT7ujvD7igOQQ6jYlwX9TQ3Ipv2HfUm0'
RANGE_NAME = 'Sheet1'  

if os.path.exists("C:/Users/admin/Desktop/python/itviec/token.json"):
    creds = Credentials.from_authorized_user_file("C:/Users/admin/Desktop/python/itviec/token.json", SCOPES)
else:
    print("1")
    flow = InstalledAppFlow.from_client_secrets_file(
        "C:/Users/admin/Desktop/python/itviec/credentials.json", SCOPES
    )
    creds = flow.run_local_server(port=0)

    with open("C:/Users/admin/Desktop/python/itviec/token.json", "w") as token:
        token.write(creds.to_json())

service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets()

# Tài khoản itviec
email = "rfd1894@gmail.com"
password = "ABCDxyzt1234@@"
service = Service(executable_path='C:/Users/admin/Desktop/python/itviec/chromedriver-win64/chromedriver.exe')

options = uc.ChromeOptions() 
options.headless = False
driver = uc.Chrome(service=service, options=options)

# Login:
link_login = "https://itviec.com/sign_in"
driver.get(link_login)
email_input = driver.find_element(By.ID, "user_email")
email_input.send_keys(email)
password_input = driver.find_element(By.ID, "user_password")
password_input.send_keys(password)
sign_in_button = driver.find_element(By.XPATH, "//span[text()='Sign In with Email']")
sign_in_button.click()

# MySQL connection
conn = mysql.connector.connect(
    host="your_host",
    user="your_user",
    password="your_password",
    database="your_database"
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        job_title VARCHAR(255),
        href VARCHAR(255),
        min_salary INT,
        max_salary INT,
        employmentType VARCHAR(255),
        job_posted_date DATE,
        company_name VARCHAR(255),
        company_link VARCHAR(255),
        addressRegion VARCHAR(255),
        addressCountry VARCHAR(255),
        job_skills TEXT,
        job_description_job_part TEXT,
        job_description_skills_part TEXT
    )
""")

today = datetime.now().strftime('%Y-%m-%d')

for i in range(40, 0, -1):
    link_web = "https://itviec.com/viec-lam-it?job_selected=none&page=" + str(i)
    driver.get(link_web)
    driver.implicitly_wait(10)
    print('Collecting Page' + f' {i}')
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    job_links = soup.find_all('a', {'data-search--job-selection-target': 'jobTitle'})
    href_list = []
    for link in job_links:
        href = link.get('href')
        href_list.append(href)
    for href in href_list:
        sleep(3)
        link_job = "https://itviec.com" + href
        driver.get(link_job)
        driver.implicitly_wait(10)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        script_tag = soup.find('script', type='application/ld+json')
    
        if script_tag:
            script_content = script_tag.string
            job_info = json.loads(script_content)
            
            if "@type" in job_info and job_info["@type"] == "JobPosting":
                job_title = job_info["title"]
                job_salary = job_info.get("baseSalary", {})
                min_salary = job_salary.get("value", {}).get("minValue")
                max_salary = job_salary.get("value", {}).get("maxValue")
                employmentType = soup.find('span', class_='normal-text text-rich-grey ms-1').text.strip()
                company_link_a = soup.find('a', class_='hyperlink')
                company_link = company_link_a.get('href') if company_link_a else ""
                company_name = job_info["hiringOrganization"]["name"]
                job_posted_date = job_info["datePosted"]
                for location in job_info.get("jobLocation", []):
                    addressRegion = location.get("address", {}).get("addressRegion")
                    addressCountry = location.get("address", {}).get("addressCountry")
                job_skills = job_info["skills"]
                job_description = job_info["description"]
                job_start_index = job_description.find("The Job")
                your_skills_start_index = job_description.find("Your Skills and Experience")
                your_skills_end_index = job_description.find("Why You'll Love Working Here")
                job_description_job_part = job_description[job_start_index:your_skills_start_index]
                job_description_skills_part = job_description[your_skills_start_index:your_skills_end_index]
                
                if job_posted_date == today:
                    result = sheet.values().get(
                        spreadsheetId=SPREADSHEET_ID,
                        range=RANGE_NAME,
                        majorDimension="ROWS"
                    ).execute()
                    
                    values = result.get("values", [])
                    next_row_index = len(values) + 1
                    
                    data_to_upload = [
                        [job_title, href, min_salary, max_salary, employmentType, 
                        job_posted_date, company_name, company_link, addressRegion, 
                        addressCountry, job_skills, job_description_job_part, 
                        job_description_skills_part]
                    ]
                    
                    request = sheet.values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=RANGE_NAME + f"!A{next_row_index}",
                        valueInputOption="RAW",
                        body={"values": data_to_upload},
                    )
                    response = request.execute()

                    print("Job data" + f" {job_title}"+" uploaded successfully!")
                    
                    cursor.execute("""
                        INSERT INTO jobs (
                            job_title, href, min_salary, max_salary, employmentType, 
                            job_posted_date, company_name, company_link, addressRegion, 
                            addressCountry, job_skills, job_description_job_part, 
                            job_description_skills_part
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (job_title, href, min_salary, max_salary, employmentType, 
                          job_posted_date, company_name, company_link, addressRegion, 
                          addressCountry, job_skills, job_description_job_part, 
                          job_description_skills_part))
                    conn.commit()
                    print("Job data" + f" {job_title}"+" inserted into MySQL successfully!")

    print('Finish Collected Page' + f' {i}')

cursor.close()
conn.close()
driver.quit()
