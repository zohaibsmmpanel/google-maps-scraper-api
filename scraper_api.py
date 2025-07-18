from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    query = request.json.get('query')
    if not query:
        return jsonify({'error': 'Missing query'}), 400

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.google.com/maps")
        time.sleep(4)
        search_box = driver.find_element(By.ID, "searchboxinput")
        search_btn = driver.find_element(By.ID, "searchbox-searchbutton")
        search_box.send_keys(query)
        search_btn.click()
        time.sleep(7)

        listings = driver.find_elements(By.CLASS_NAME, "qBF1Pd")
        results = [el.text for el in listings]
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        driver.quit()
