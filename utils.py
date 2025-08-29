from NorenRestApiPy.NorenApi import NorenApi
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
    pass
