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

#### Scrape homepage for links to individual schools###
# 
# Add to dictionary:
#   {'A.N. Pritzker School': ['2009 W Schiller St, Chicago, IL 60622']}

url_home = 'https://5-essentials.org/cps/5e/2018/'
driver.get(url_home)
time.sleep(5)

NUM_SCHOOLS = 661
urls = []
i = 1

for i in range(1, NUM_SCHOOLS + 1):
    sqr_xpath = f'/html/body/section/div/div[2]/div[2]/div/div/div[1]/div/table/tbody/tr[{i}]/td[1]/span[1]'
    sqr = driver.find_element_by_xpath(sqr_xpath).get_attribute('class')
    if sqr == 'summary-well rank-0-cell':
        continue

    url_xpath = f'/html/body/section/div/div[2]/div[2]/div/div/div[1]/div/table/tbody/tr[{i}]/td[1]/a'
    url_school = driver.find_element_by_xpath(url_xpath).get_attribute('href')
    urls.append(url_school)


### Scrape sub-page for school_name, school_address and essentials_link to "Essentials"###
# e.g. https://5-essentials.org/cps/5e/2018/s/610229/essentials/

dict_schools = {}
essentials_urls = []

for url in urls:
    driver.get(url)
    time.sleep(1)
    target = driver.find_element_by_id('react_target')
    info = target.find_element_by_tag_name('a')
    
    school_name = info.find_element_by_tag_name('h1').text
    school_address = info.find_elements_by_tag_name('h3')[1].text
    essentials_url = driver.find_element_by_xpath(
        '/html/body/div[3]/div/section/div[2]/div[2]/div[2]/h2[1]/a').get_attribute('href')
    
    dict_schools[school_name] = []
    dict_schools[school_name].append(school_address)

    essentials_urls.append(essentials_url)
    
# Scrape 'performance' page for data and add to dictionary
#   {'A.N. Pritzker School': ['2009 W Schiller St, Chicago, IL 60622', 70, 63, 46, 45, 42]}
# url_performance = 'https://5-essentials.org/cps/5e/2018/s/610229/essentials/'
# school_name = 'A.N. Pritzker School'

for url, school_name in zip(essentials_urls, dict_schools.keys()):
    driver.get(url)
    time.sleep(1)

    # click to sort "The 5Essentials" alphabetically
    # Sorting button xpath: '/html/body/div[2]/div/section/div/div[2]/div[2]/div/div/table/thead/tr/th[1]'

    sort_button = driver.find_element_by_xpath(
        '/html/body/div[2]/div/section/div/div[2]/div[2]/div/div/table/thead/tr/th[1]')
    sort_button.click()

    families_xpath = '/html/body/div[2]/div/section/div/div[2]/div[2]/div/div/table/tbody/tr[1]/td[2]/span/span[1]'
    instruction_xpath = '/html/body/div[2]/div/section/div/div[2]/div[2]/div/div/table/tbody/tr[2]/td[2]/span/span[1]'
    teachers_xpath = '/html/body/div[2]/div/section/div/div[2]/div[2]/div/div/table/tbody/tr[3]/td[2]/span/span[1]'
    environment_xpath = '/html/body/div[2]/div/section/div/div[2]/div[2]/div/div/table/tbody/tr[4]/td[2]/span/span[1]'
    leaders_xpath = '/html/body/div[2]/div/section/div/div[2]/div[2]/div/div/table/tbody/tr[5]/td[2]/span/span[1]'

    for xpath in [families_xpath, instruction_xpath, teachers_xpath, environment_xpath, leaders_xpath]:
        try:
            num = driver.find_element_by_xpath(xpath).text
        except:
            num = -1
        dict_schools[school_name].append(num)

print(json.dumps(dict_schools, indent=2))

driver.quit()

# Make DataFrame from dictionary:
columns = ['Address', 'Ambitious_Instruction', 'Collaborative_Teachers', 'Effective_Leaders', 'Involved_Families', 'Supportive_Environment']
df_schools = pd.DataFrame.from_dict(dict_schools, orient='index', columns=columns)

# Export CSV
df_schools.to_csv('../raw_data/schools.csv')
