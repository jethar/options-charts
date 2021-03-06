import logging, os
import json
from kiteconnect import KiteTicker

# from db import insert_ticks

import sqlite3
from datetime import datetime
from dateutil import tz


API_KEY      = os.getenv("API_KEY")
API_SECRET   = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
DB_FILE      = f"{os.getenv('DB_FILE')}_{datetime.now().strftime('%Y-%m-%d')}.db"

INSTRUMENT_CSV = os.getenv('INSTRUMENT_CSV')


CREATE_TICK_TABLE_SCRIPT = f"""
    CREATE TABLE IF NOT EXISTS ticks ( 
        tick_date	DATETIME, 
        token	INTEGER, 
        price	REAL,
        tick_json JSON
    );
"""

def get_instruments():
    import csv

    data = []
    with open(INSTRUMENT_CSV, newline='') as f:
        reader = csv.DictReader(f)
    #     header = next(reader)  # ignore header
        data_nifty = [int(row['instrument_token']) for row in reader if ("NIFTY" in row['tradingsymbol']) or ("ETF" in row['tradingsymbol'])]

    with open(INSTRUMENT_CSV, newline='') as f:
        reader = csv.DictReader(f)       
        data_oth = [int(row['instrument_token']) for row in reader if ("NIFTY" not in row['tradingsymbol']) and ("ETF" not in row['tradingsymbol'])]

    return data_nifty, data_oth  

# instruments = [12219650, 12219906]
instruments_nifty, instruments_oth = get_instruments()
instruments = [*instruments_nifty, *instruments_oth]

logging.basicConfig(level=logging.INFO)

db = sqlite3.connect(DB_FILE)
cur = db.cursor()
cur.execute(CREATE_TICK_TABLE_SCRIPT)

# Timezone information for timezone conversion
utc_tz= tz.gettz('UTC')
india_tz= tz.gettz('Asia/Kolkata')

def get_time_in_timezone(timezone):
    """
    Get time in given timezone, assuming starting with UTC.
    source: https://stackoverflow.com/a/53914639
    """
    utc = datetime.now()
    # utc = utc.replace(tzinfo=utc_tz)
    time_with_offset = utc.astimezone(timezone)
    time_without_offset = time_with_offset.replace(tzinfo=None)
    return time_without_offset

def get_IST_time():
    return get_time_in_timezone(india_tz)

def delete_keys(tick, keys):
    """
    Delete keys from tick dict. 
    Use "dot" notaion for representing nested keys. e.g. ohlc.close
    """
    
    for key in keys:
        t = tick
        *key_prefix, last_part = key.split('.')
        for k in key_prefix:
            t = t[k]
 
        try:
            del t[last_part]
        except KeyError:
            logging.debug(f'Key {key}" is not in the tick dictionary')   

# Task to insert to SQLite db
def insert_ticks(ticks):
    c = db.cursor()
    qry = "insert into ticks (tick_date, token, price) values "
    qry_full = "insert into ticks (tick_date, token, price, tick_json) values "
    count = 0
    count_full = 0
    time = get_IST_time()

    for tick in ticks:
        # c.execute(f"insert into ticks values ('{datetime.now()}', {tick['instrument_token']}, {tick['last_price']})")
        # c.execute(insert_tick_statement, {
        #     "date": datetime.now(),
        #     "token": tick["instrument_token"],
        #     "price": tick["last_price"]})

        if tick['mode'] == "full":
            if count_full > 0:
                qry_full += ", "
            
            delete_keys(tick, ["depth", "oi_day_high", "oi_day_low", "buy_quantity", "sell_quantity", "ohlc.open", "ohlc.close"])

            qry_full += f"('{time}', {tick['instrument_token']}, {tick['last_price']}, json('{json.dumps(tick, default=str)}'))"
            count_full += 1
        else:
            if count > 0:
                qry += ", "
            qry += f"('{time}', {tick['instrument_token']}, {tick['last_price']})"
            count += 1

    if count:
        c.execute(qry)
    if count_full:
        c.execute(qry_full)    
    # logging.debug("Inserting ticks to db : {}".format(json.dumps(ticks)))
    logging.debug(f"Inserting ticks to db {time}.")

    try:
        db.commit()
    except Exception:
        db.rollback()
        logging.exception("Couldn't write ticks to db: ")

# Initialise
# kws = KiteTicker("your_api_key", "your_access_token")
kws = KiteTicker(API_KEY, ACCESS_TOKEN)

def on_ticks(ws, ticks):
    # Callback to receive ticks.
    if len(ticks) > 0:
        # on json.dumps
        # TypeError: Object of type datetime is not JSON serializable formatting issue on datetime object 
        #     http://127.0.0.1:7777/?token=473bbc2c11c1b9b0865b35b31c0ba704c151a06b833abce7
        logging.debug("Ticks: {}".format(json.dumps(ticks, indent=4, default=str)))
        insert_ticks(ticks)

def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    # ws.subscribe([738561, 5633])
    ws.subscribe(instruments)

    # Set RELIANCE to tick in `full` mode.
    #    ws.MODE_FULL , ws.MODE_LTP
    # ws.set_mode(ws.MODE_FULL, [738561])
    ws.set_mode(ws.MODE_LTP, instruments)
    ws.set_mode(ws.MODE_FULL, instruments_nifty)

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
kws.connect()