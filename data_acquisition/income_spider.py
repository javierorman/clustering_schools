# import requests
from selenium import webdriver
PATH_CHROMEDRIVER = '/Users/javierorman/Python/chromedriver'
driver = webdriver.Chrome(PATH_CHROMEDRIVER)

import time
import pandas as pd
import json

# Prepare header
my_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'
headers = {'User-Agent': my_user_agent}

### Scrape homepage to get all zip codes in Chicago ###
url_home = 'https://www.zipdatamaps.com/zipcodes-chicago-il'
driver.get(url_home)

i = 1
zip_list = []
errors = 0
MAX_ERRORS = 3

while True:
    try:
        zip_ = driver.find_element_by_xpath(
            f'/html/body/div[1]/div[1]/div[2]/table/tbody/tr[{i}]/td[1]/table/tbody/tr/td[4]/a').text
        zip_list.append(zip_)
        errors = 0  # reset error count
        i += 1  # try again with the next value of i
    except:
        errors += 1
        if errors == MAX_ERRORS: # reached maximum errors allowed
            break
        else:
            i += 1  # try again with the next value of i

### Scrape each individual ZIP code page for median income ###
# Each URL looks like 'https://www.zipdatamaps.com/60007'
dict_incomes = {}
url_base = 'https://www.zipdatamaps.com/'

for zip_ in zip_list:
    driver.get(url_base + str(zip_))

    # income looks like '$75743'
    # xpath syntax: https://www.guru99.com/xpath-selenium.html
    income = driver.find_element_by_xpath(
        "//*[text()='Median Household Income']//following-sibling::td").text
    dict_incomes[zip_] = income[1:]

    driver.find_element

    time.sleep(1)

# print(dict_incomes)
print(json.dumps(dict_incomes, indent=2))

driver.quit()

# Make DataFrame from dictionary:
columns = ['Median_income']
df_incomes = pd.DataFrame.from_dict(dict_incomes, orient='index', columns=columns)

# Export CSV
df_incomes.to_csv('../raw_data/incomes.csv')
