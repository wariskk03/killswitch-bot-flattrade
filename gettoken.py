from urllib.parse import parse_qs, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import hashlib
import requests
import json
import pyotp

with open("cred.json") as f:
    cred = json.load(f)
    user, pas, totp_token = cred["user_id"], cred["pass"], cred["totp_token"]
    api_key, api_secret = cred["api_key"], cred["api_secret"]

def requests_code_value():
    print("Requesting requests-code!")
    url = f"https://auth.flattrade.in/?app_key={api_key}"
    driver = webdriver.Chrome()
    driver.minimize_window()

    driver.get(url)

    username = driver.find_element(By.ID, "input-19")
    username.send_keys(user)

    password = driver.find_element(By.ID, "pwd")
    password.send_keys(pas)

    totp_code = pyotp.TOTP(totp_token).now()
    totp = driver.find_element(By.ID, "pan")
    totp.send_keys(totp_code)

    login_btn = driver.find_element(By.ID, "sbmt")
    login_btn.click()

    WebDriverWait(driver, 10).until(EC.title_contains("localhost"))    
    code_url = driver.current_url
    parsed_url = urlparse(code_url)
    url_params = parse_qs(parsed_url.query)
    code = url_params.get("code")[0]

    return code

def get_token():
    print("Requesting session-token!")
    req_code = requests_code_value()
    secret_key = hashlib.sha256(f"{api_key}{req_code}{api_secret}".encode()).hexdigest()

    payload = {
        "api_key": api_key,
        "request_code": req_code,
        "api_secret": secret_key
    }

    try:
        response = requests.post("https://authapi.flattrade.in/trade/apitoken", json=payload)
        if response.status_code==200:
            response = response.json()
            if response.get("stat") == "Ok":
                print("Session-token fetched successfully!")
                return response.get("token")
            else:
                print("Couldn't generate session-token, wrong response!")
                print(response)
        else:
            print("Error in requesting session-token!")

    except requests.exceptions.RequestException as e:
        return {"error": "RequestException", "details": str(e)}
    