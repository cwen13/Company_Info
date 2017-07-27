from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv


def get_company_info(page_source):
    # Make the soup
    soup = BeautifulSoup(page_source,'html.parser')

    # Extracting basic info
    company_name = soup.h1.text
    description  = soup.find(class_='tagline').text
    # List comprehension for grabing listings of tags
    industry_tags= [x.text for x in soup.find(class_='industries').find_all('a')]
    other_tags   = [x.text for x in soup.find_all(class_='tag-list')[1].find_all('a')]
    location     = soup.find(class_='company-locations').text
    company_url  = soup.find(class_='company-external-url').text

    comp_info    = soup.find(class_='company-info')
    
    # Initiate Variables
    target_market = "NONE"
    employees     = "NONE"
    launch_date   = "NONE"
    ownership     = "NONE"
    est_value     = "NONE"
    funding       = "NONE"
    last_round    = "NONE"
    total_funding = "NONE"
    
    for entry in comp_info.find_all(class_='field'):
        if "Target Markets" in entry.text:
            target_market = entry.text[14:]
        elif "Employees" in entry.text:
            employees     = entry.text[9:]
        elif "Launch Date" in entry.text:
            launch_date   = entry.text[11:]
        elif "Ownership" in entry.text:
            ownership     = entry.text[9:]
        elif "Estimated Valuation" in entry.text:
            est_value     = entry.text[19:]
            
    funding      = soup.find(class_='tab-funding-rounds') 
    try:
        last_round   = funding.find_all('tr')[-2].find(class_='round').text
    except:
        last_round = "NONE"
    try:
        total_funding= funding.find_all('tr')[-1].find(class_='footer-value').text
    except:
        total_funding="NONE"
        
    return (company_name,  description,
            industry_tags, other_tags,
            location,      company_url,
            target_market, employees,
            launch_date,   ownership,
            est_value,     last_round,
            total_funding)

if __name__ == "__main__":
    base_url = "http://app.startupeuropeclub.eu"
    search_url = "http://app.startupeuropeclub.eu/funding-rounds/f/locations/Europe/rounds/anyof_SEED_SERIES%20A_SERIES%20B_SERIES%20C_EQUITY_PRE%20SERIES%20A_GRANT_-"

    company_urls = []
    scrollHeight = 250
    screen = 0
    
    # Initiate webdriver
    driver = webdriver.Chrome()
    driver.get(search_url)

    # grab a listing of the companys in the page
    while True:
        soup = BeautifulSoup(driver.page_source,'html.parser')
        table = soup.find(class_='table-list')
        # for each etry in the table pull out the link
        for entry in table:
            try:
                company_urls.append(entry.div.a['href'])
            except:
                pass
                
        # if less than 25 exit loop
        if len(table) < 25:
            break
        #if not less than 25 scroll down by window height
        else:
            print("screen:", screen)
            screen += 1
            driver.execute_script("window.scrollTo(0,"+str(scrollHeight)+")")
            scrollHeight += 250

    company_urls = set(company_urls)
    # Initiate files
    outputFile = open("companies.csv",'w', encoding='utf-8')
    # Initiate csv writer
    csvw = csv.writer(outputFile, dialect='unix')

    # grab each companies info
    for company in company_urls:
        company_url = "".join((base_url, company))
        # Got to company page
        driver.get(company_url)
        # Grab company info and write each row
        csvw.writerow(get_company_info(driver.page_source))

    outputFile.close()
