import pandas as pd
import streamlit as st

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

def BoAuto():
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    

    usernameStr = 'VDB_DEV-ABDER'
    passwordStr = 'vpmarhJeDe9EXXnA'

    browser = webdriver.Chrome()
    browser.get(('https://dev-abder-vdb.kd-dws.net/admin/login'))
    browser.implicitly_wait(1)


    browser.find_element(By.XPATH,"//input[@placeholder='Enter Username']").send_keys(usernameStr)

    browser.find_element(By.XPATH,"//input[@placeholder='Enter Password']").send_keys(passwordStr)

    browser.find_element(By.XPATH, "//button[@id='loginform-submit']").click()
    time.sleep(1)

    browser.find_element(By.XPATH, "//p[normalize-space()='CouchDB Operations']").click()
    time.sleep(1)

    browser.find_element(By.XPATH, "//a[normalize-space()='Data Import']").click()
    time.sleep(10)

    browser.find_element(By.XPATH, "//textarea[@id='import-data']").click()
    time.sleep(10)

    browser.find_element(By.XPATH, "//textarea[@id='import-data']").send_keys(jsonToImport)
    time.sleep(10)

    browser.find_element(By.CSS_SELECTOR, "#couchdb-import-validate").click()
    time.sleep(5)
    
    browser.find_element(By.CSS_SELECTOR, "#couchdb-import-submit").click()
    time.sleep(5)

    browser.find_element(By.XPATH, "//button[normalize-space()='Yes, import!']").click()
    time.sleep(15)
    

    st.write('Les datas ont été importées')

    


    browser.quit()



#########################################################################################################################

data = st.file_uploader('Upload file here', type=['csv','xlsx'])

if data is not None:

    # ----- Import des rooms :
    df = pd.read_excel(data, sheet_name='rooms').iloc[:2]
    df.dropna(inplace=True)

    
    df.set_index('roomid', inplace=True)
    df = df.reset_index().to_json(orient='records')

    f = open("../formattedData.txt", "w")
    f.write('''{"docs":''')
    f.write(df)
    f.write('''}''')
    f.close()

    f = open("../formattedData.txt", "r")
    jsonToImport = f.read()
    f.close()

    with st.spinner("Les ROOMS sont en cours d'importation..."):
        BoAuto()
    st.success('Donées ROOMS importées')
        

    time.sleep(2)

    #----- Import des sensors : 
    df = pd.read_excel(data, sheet_name='sensors').iloc[:2]
    df.dropna(inplace=True)

    df['sensorid'] = df['sensorid'].str.lower()
    df = df[~df['sensorid'].str.contains('_')].iloc[:10]

    df.set_index('sensorid', inplace=True)
    df = df.reset_index().to_json(orient='records')

    f = open("../formattedData.txt", "w")
    f.write('''{"docs":''')
    f.write(df)
    f.write('''}''')
    f.close()

    f = open("../formattedData.txt", "r")
    jsonToImport = f.read()
    f.close()

    with st.spinner("Les SENSORS sont en cours d'importation..."):
        BoAuto()
    st.success('Données SENSORS importées')


    #------- Import des lights 
    df = pd.read_excel(data, sheet_name='lights').iloc[:2]
    df.dropna(inplace=True)
    df.drop('Unnamed: 6',axis=1,inplace=True)

    df.set_index('lightid', inplace=True)
    df = df.reset_index().to_json(orient='records')

    f = open("../formattedData.txt", "w")
    f.write('''{"docs":''')
    f.write(df)
    f.write('''}''')
    f.close()

    f = open("../formattedData.txt", "r")
    jsonToImport = f.read()
    f.close()

    with st.spinner("Les LIGHTS sont en cours d'importation..."):
        BoAuto()
    st.success('Donées LIGHTS importées!')
