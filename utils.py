from NorenRestApiPy.NorenApi import NorenApi
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyotp
import json

def session():
    api = NorenApi(host='https://piconnect.flattrade.in/PiConnectTP/', websocket='wss://piconnect.flattrade.in/PiConnectWSTp/')

    with open("cred.json") as f:
        cred = json.load(f)

    api.set_session(userid=cred["user_id"], password=cred["pass"], usertoken=cred["token"])

    return api

def get_orders(api):
    for i in range(3):
        orders = api.get_order_book()
        if orders:
            if orders.get("stat") == "Ok":
                return orders
            else:
                print(f"Error in getting orders: {orders}")
        return []

def get_open_orders(orders):
    open_orders = []
    for ord in orders:
        if ord["status"] == "OPEN":
            open_orders.append(ord)
    return open_orders

def get_pnl(positions):
    pnl = 0
    for pos in positions:
        pnl = float(pos["rpnl"]) + float(pos["urmtom"])
    return pnl

def get_positions(api):
    for i in range(3):
        positions = api.get_positions()
        if positions:
            if positions.get("stat") == "Ok":
                return positions
            else:
                print(f"Error in getting orders: {positions}")
        return []
    
def get_open_positions(positions):
    open_positions = []
    for pos in positions:
        if pos["netqty"] != "0":
            open_positions.append(pos)
    return open_positions

def close_positions(open_positions, api):
    for pos in open_positions:
        api.place_order(
            buy_or_sell="B" if pos["netqty"] < 0 else "S",
            product_type=pos["prd"],
            exchange=pos["exch"],
            tradingsymbol=pos["tsym"],
            quantity=abs(int(pos["netqty"])),
            discloseqty=0,
            price_type="MKT",
            retention="DAY"
        )

def cancel_orders(open_orders, api):
    for ord in open_orders:
        api.cancel_order(ord["norenordno"]) 

def flatten(open_positions, open_orders, api):
    close_positions(open_positions, api)
    cancel_orders(open_orders, api)

def killswitch():
    with open("/Users/wariskhan/Python Algo/flattrade_api/killswitch_tool/cred.json") as f:
        cred = json.load(f)
        user, pas, totp_token = cred["user_id"], cred["pass"], cred["totp_token"]

    driver = webdriver.Chrome()
    driver.minimize_window()

    driver.get("https://auth.flattrade.in/?app=wall")

    username = driver.find_element(By.ID, "input-19")
    username.send_keys(user)

    password = driver.find_element(By.ID, "pwd")
    password.send_keys(pas)

    totp_code = pyotp.TOTP(totp_token).now()
    totp = driver.find_element(By.ID, "pan")
    totp.send_keys(totp_code)

    login_btn = driver.find_element(By.ID, "sbmt")
    login_btn.click()

    my_account = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[3]//span[1]")))
    my_account.click()

    time.sleep(0.2)
    WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".v-overlay__scrim")))

    killswitch_tab = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//b[normalize-space(text())='Kill Switch']")))
    killswitch_tab.click()

    checkboxes = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "v-input--selection-controls__ripple")))

    checkboxes[1].click()
    checkboxes[6].click()

    deactivate = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class='v-btn v-btn--has-bg theme--light elevation-0 v-size--small primary'] span[class='v-btn__content']")))
    deactivate.click()
    driver.maximize_window()

    try:
        while True:
            time.sleep(1)
            driver.title
    except:
        print("Browser is closed")

killswitch()