import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
import time

URL = 'https://www.zapimoveis.com.br/aluguel/imoveis/sp+sao-paulo+zona-sul+vl-olimpia/2-quartos/?onde=,S%C3%A3o%20Paulo,S%C3%A3o%20Paulo,Zona%20Sul,Vila%20Ol%C3%ADmpia,,,neighborhood,BR%3ESao%20Paulo%3ENULL%3ESao%20Paulo%3EZona%20Sul%3EVila%20Olimpia,-23.598157,-46.68293,&transacao=Aluguel&tipo=Im%C3%B3vel%20usado&precoMaximo=3000&precoMinimo=1000&pagina=1&quartos=2&banheiros=1&vagas=1&tipoAluguel=Mensal'
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}
FORMS_LINK = 'https://docs.google.com/forms/d/e/1FAIpQLSeyJaPfqj6q3QwO65-f-zQ7qcvYuhOV0FfYNPFgljnL0OGZag/viewform?usp=sf_link'


data = {}

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument(r"user-data-dir=C:/Users/mathe/AppData/Local/Google/Chrome/User Data")
chrome_options.add_argument("--profile-directory=Profile 2")


response = requests.get(URL, headers=HEADERS)
webpage = response.text
soup = BeautifulSoup(webpage, "html.parser")

# Creating dictionary without data for all results in page
results = soup.select(selector='div > div.card-listing.simple-card')
dict_index = 0
for result in results:
    data[dict_index] = {"price": None,
                        "condominium": None,
                        "total price (month)": None,
                        "IPTU": None,
                        "total price (year)": None,
                        "area": None,
                        "bedrooms": None,
                        "parking": None,
                        "bathroom": None,
                        "link": None,
                        }
    dict_index += 1 

# Updating data with prices
prices = soup.select(selector='div.simple-card__listing-prices.simple-card__prices > div > p > strong')
dict_index = 0
price_list = []
for price in prices:
    price_split = price.text.split()
    del price_split[-1]
    del price_split[0]
    price_number = int(" ".join(price_split).replace('.', ''))
    data[dict_index]["price"] = price_number
    price_list.append(price_number)
    dict_index += 1

# Updating data with condominium
condominiums = soup.select(selector='div.simple-card__listing-prices.simple-card__prices > ul > li.card-price__item.condominium.text-regular > span.card-price__value')
dict_index = 0
condominium_list = []
for condominium in condominiums:
    condominium_split = condominium.text.split()
    del condominium_split[0]
    condominium_number = int(" ".join(condominium_split).replace('.', ''))
    data[dict_index]["condominium"] = condominium_number
    condominium_list.append(condominium_number)
    dict_index += 1

# Updating data with total price (month)
dict_index = 0
for price, condominium in zip(price_list, condominium_list):
    total_price_month = price + condominium
    data[dict_index]["total price (month)"] = total_price_month
    dict_index += 1

# Updating data with areas
areas = soup.select(selector='div.simple-card__actions > ul.feature__container.simple-card__amenities > li.feature__item.text-small.js-areas > span[itemprop="floorSize"]')
dict_index = 0
for area in areas:
    area_split = area.text.split()
    del area_split[-1]
    data[dict_index]["area"] = int("".join(area_split))
    dict_index += 1

# Updating data with bedrooms
bedrooms = soup.select(selector='div.simple-card__actions > ul > li.feature__item.text-small.js-bedrooms > span[itemprop="numberOfRooms"]')
dict_index = 0
for bedroom in bedrooms:
    bedroom_number = int(bedroom.text)
    data[dict_index]["bedrooms"] = bedroom_number
    dict_index += 1

# Updating data with parking
parkings = soup.select(selector='div.simple-card__actions > ul > li.feature__item.text-small.js-parking-spaces > span:nth-of-type(2)')
dict_index = 0
for parking in parkings:
    parking_number = int(parking.text)
    data[dict_index]["parking"] = parking_number
    dict_index += 1

# Updating data with bathrooms
bathrooms = soup.select(selector='div.simple-card__actions > ul > li.feature__item.text-small.js-bathrooms > span[itemprop="numberOfBathroomsTotal"]')
dict_index = 0
for bathroom in bathrooms:
    bathroom_number = int(bathroom.text)
    data[dict_index]["bathroom"] = bathroom_number
    dict_index += 1

print(data)

chrome_driver_path = "C:\Code\chromedriver.exe"
driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
driver.get(URL)

# find all the results
results = driver.find_elements(By.CSS_SELECTOR, 'div.listings__container > div > div > div.card-listing.simple-card > div.simple-card__box > div.simple-card__actions')

iptu_list = []
dict_index = 0

# iterate over the results and get the URL and IPTU for each one
for result in results:
    try:
        # get the current window handle
        current_window = driver.current_window_handle

        # scroll the element into view
        driver.execute_script("arguments[0].scrollIntoView();", result)
        time.sleep(1)

        # move to the result to hover over it
        actions = webdriver.ActionChains(driver)
        actions.move_to_element(result)
        actions.perform()
        time.sleep(1)

        # click the result to open the link in a new tab
        result.click()
        time.sleep(2)

        # wait for the new tab to load and switch to it
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        driver.switch_to.window(driver.window_handles[-1])

        # get the URL and IPTU
        time.sleep(5)
        url = driver.current_url
        data[dict_index]["link"] = url

        iptu = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/section/div[2]/div[1]/article[1]/div/div/div[2]/div[1]/ul/li[2]/span')
        if iptu.text == 'não informado':
            data[dict_index]["IPTU"] = 0
            data[dict_index]["total price (year)"] = (data[dict_index]["total price (month)"] * 12)
        else:
            iptu_split = iptu.text.split()
            del iptu_split[0]
            iptu_number = int(" ".join(iptu_split).replace('.', ''))
            data[dict_index]["IPTU"] = int("".join(iptu_split))
            data[dict_index]["total price (year)"] = (data[dict_index]["total price (month)"] * 12) + iptu_number
        dict_index += 1

        # close the tab and switch back to the original tab
        driver.close()
        driver.switch_to.window(current_window)

    except Exception as e:
        print(f"Error: {e}")
        continue

with open('day_053/zapimoveis.json', mode = "w") as file:
    json.dump(data, file, indent=4)

driver.execute_script("window.open('about:blank','secondtab');")
driver.switch_to.window("secondtab")
driver.get(FORMS_LINK)

forms_counter = 0
for entries in data:
    time.sleep(2)
   
    forms_index = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input')
    forms_index.send_keys(forms_counter)

 
    forms_price = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input')
    forms_price.send_keys(data[forms_counter]["price"])

    forms_condominium = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input')
    forms_condominium.send_keys(data[forms_counter]["condominium"])

    forms_total_price_month = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[4]/div/div/div[2]/div/div[1]/div/div[1]/input')
    forms_total_price_month.send_keys(data[forms_counter]["total price (month)"])

    forms_iptu = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[5]/div/div/div[2]/div/div[1]/div/div[1]/input')
    forms_iptu.send_keys(data[forms_counter]["IPTU"])

    forms_total_price_year = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[6]/div/div/div[2]/div/div[1]/div/div[1]/input')
    forms_total_price_year.send_keys(data[forms_counter]["total price (year)"])

    forms_area = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[7]/div/div/div[2]/div/div[1]/div/div[1]/input')
    forms_area.send_keys(data[forms_counter]["area"])

    forms_bedrooms = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[8]/div/div/div[2]/div/div[1]/div/div[1]/input')
    forms_bedrooms.send_keys(data[forms_counter]["bedrooms"])

    forms_parking = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[9]/div/div/div[2]/div/div[1]/div/div[1]/input')
    forms_parking.send_keys(data[forms_counter]["parking"])

    forms_bathroom = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[10]/div/div/div[2]/div/div[1]/div/div[1]/input')
    forms_bathroom.send_keys(data[forms_counter]["bathroom"])

    forms_link = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[11]/div/div/div[2]/div/div[1]/div/div[1]/input')
    forms_link.send_keys(data[forms_counter]["link"])

    forms_submit = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div')
    forms_submit.click()

    time.sleep(1)
    forms_back = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/div[4]/a')
    forms_back.click()
    
    forms_counter += 1

driver.quit()