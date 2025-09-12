from utils import session, flatten, get_orders, get_positions, get_open_orders, get_open_positions
import logging
import threading

stop_event = threading.Event() # Create a flag
logging.basicConfig(level=logging.INFO)

api = session()

THRESHOLDS = {
    "26000": float(input("Tgt - NIFTY: ")),
    "26009": float(input("Tgt - BANKNIFTY: "))   
}
direction = input("Direction - (l:long/s:short): ").strip().lower()

def on_open():
    print("✅ WebSocket connected!")
    api.subscribe(["NSE|26000", "NSE|26009"])

latest_prices = {}
def on_quote(message):
    token = message["tk"]
    lp = float(message["lp"])
    latest_prices[token] = lp

    if all(tk in latest_prices for tk in THRESHOLDS):
        if direction == "l":  # long → target is above threshold
            nifty_ok = latest_prices["26000"] > THRESHOLDS["26000"]
            bank_ok  = latest_prices["26009"] > THRESHOLDS["26009"]
        elif direction == "s":  # short → target is below threshold
            nifty_ok = latest_prices["26000"] < THRESHOLDS["26000"]
            bank_ok  = latest_prices["26009"] < THRESHOLDS["26009"]

        if nifty_ok or bank_ok:
            print("⚠️ Either Nifty OR Bank Nifty hit target → Exit triggered ✅")
            pos = get_positions(api)
            ord = get_orders(api)
            open_ord = get_open_orders(ord)
            open_pos = get_open_positions(pos)
            print("❌ Closing positions and open orders!")
            flatten(open_ord, open_pos, api)
            stop_event.set() # set for the main thread which was waiting for set

def on_close():
    print("❌ WebSocket closed!")

api.start_websocket( # create a worker thread
    socket_open_callback=on_open,
    subscribe_callback=on_quote,
    socket_close_callback=on_close
)

try:
    stop_event.wait() # make the main thread wait until the other thread set it
    api.close_websocket()
except KeyboardInterrupt:
    print("\nForce exit detected, closing WebSocket…")
    api.close_websocket()
    stop_event.set()
