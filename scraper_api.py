from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

app = Flask(__name__)
CORS(app)  # ✅ This line enables full cross-origin access

@app.route('/')
def home():
    return jsonify({"status": "API is live. Use POST /scrape with {query}"})

@app.route('/scrape', methods=['POST', 'OPTIONS'])  # ✅ Added OPTIONS method
def scrape():
    if request.method == 'OPTIONS':
        return '', 204  # ✅ Preflight response

    query = request.json.get('query')
    if not query:
        return jsonify({'error': 'Missing query'}), 400

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=options)
    results = []

    try:
        driver.get("https://www.google.com/maps")
        time.sleep(5)

        search_box = driver.find_element(By.ID, "searchboxinput")
        search_btn = driver.find_element(By.ID, "searchbox-searchbutton")
        search_box.send_keys(query)
        search_btn.click()
        time.sleep(7)

        scrollable = driver.find_element(By.XPATH, '//div[@role="feed"]')
        last_height = 0
        stuck_count = 0

        for _ in range(20):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
            time.sleep(1.5)
            new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable)
            if new_height == last_height:
                stuck_count += 1
            else:
                stuck_count = 0
            last_height = new_height
            if stuck_count >= 3:
                break

        listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")

        for el in listings:
            try:
                name = el.find_element(By.CLASS_NAME, "qBF1Pd").text
                category = el.find_element(By.CLASS_NAME, "W4Efsd").text
                phone = ""
                try:
                    phone = el.find_element(By.CLASS_NAME, "UsdlK").text
                except:
                    pass
                maps_link = el.find_element(By.TAG_NAME, "a").getAttribute("href")

                results.append({
                    'name': name,
                    'category': category,
                    'phone': phone,
                    'maps_link': maps_link
                })
            except:
                continue

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        driver.quit()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
