from utils import get_orders, get_open_orders, get_open_positions, get_pnl, get_positions, session, flatten, killswitch
import json
import time

api = session()
with open("cred.json") as f:
    daily_risk = json.load(f)["daily_risk"]

polling_interval = 1

def killswitch_bot():
    attempts = 0
    pnl = 0
    print("Starting the Bot!")
    
    while attempts < 3:
        positions = get_positions(api)
        pnl = get_pnl(positions)
        print("PNL: ", round(pnl, 2))

        if pnl <= -daily_risk:
            print("Activating Killswitch")

            print("Closing Positions and orders")
            open_positions = get_open_positions(positions)

            orders = get_orders(api)
            open_orders = get_open_orders(orders)

            flatten(open_positions, open_orders, api)

            print("Final Checking")
            positions = get_positions(api)
            open_positions = get_open_positions(positions)
            
            orders = get_orders(api)
            open_orders = get_open_orders(orders)

            closed_flag = not len(open_positions)
            canceled_flag = not len(open_orders)

            if closed_flag and canceled_flag:
                print("✅ All positions closed and orders cancelled.")
                if killswitch():
                    print("Activated Successfully!")
                    return
                else:
                    print("Couldn't Activate Killswitch")
                    return
            else:
                print(f"❌ Attempt {attempts} failed. Retrying...")
                attempts += 1
                time.sleep(polling_interval * (attempts + 1))
        else:
            time.sleep(polling_interval)

    print("❌ Killswitch failed after 3 attempts. Manual intervention required.")

if __name__ == "__main__":
    try:
        killswitch_bot()
    except KeyboardInterrupt:
        print("\nBot manually stopped!")
