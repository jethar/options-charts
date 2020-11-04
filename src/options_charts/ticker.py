import logging, os
import json
from kiteconnect import KiteTicker

API_KEY      = os.getenv("API_KEY")
API_SECRET   = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

instruments = [12219650, 12219906]

logging.basicConfig(level=logging.DEBUG)

# Initialise
# kws = KiteTicker("your_api_key", "your_access_token")
kws = KiteTicker(API_KEY, ACCESS_TOKEN)

def on_ticks(ws, ticks):
    # Callback to receive ticks.
    
    # on json.dumps
    # TypeError: Object of type datetime is not JSON serializable formatting issue on datetime object 
    #     http://127.0.0.1:7777/?token=473bbc2c11c1b9b0865b35b31c0ba704c151a06b833abce7
    logging.debug("Ticks: {}".format(json.dumps(ticks, indent=4, default=str)))

def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    # ws.subscribe([738561, 5633])
    ws.subscribe(instruments)

    # Set RELIANCE to tick in `full` mode.
#     ws.set_mode(ws.MODE_FULL, [738561])
    ws.set_mode(ws.MODE_FULL, instruments)

def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
def execute():
    kws.connect()