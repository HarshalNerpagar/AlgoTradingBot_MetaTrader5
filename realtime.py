import MetaTrader5 as mt5
import time
from datetime import datetime

# Display data on the MetaTrader 5 package
print("MetaTrader5 package author: ", mt5.__author__)
print("MetaTrader5 package version: ", mt5.__version__)

# Establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# Attempt to enable the display of the GBPUSD in MarketWatch
selected = mt5.symbol_select("GBPUSD", True)
if not selected:
    print("Failed to select GBPUSD")
    mt5.shutdown()
    quit()

try:
    # Fetch tick data every second
    while True:
        lasttick = mt5.symbol_info_tick("XAUUSD")
        if lasttick is None:
            print("Failed to get tick data")
        else:
            # Convert UNIX timestamp to local time
            local_time = datetime.fromtimestamp(lasttick.time).strftime('%H:%M:%S')
            print(f"Local Time: {local_time},  Bid: ( {lasttick.bid} ) , Ask: ( {lasttick.ask} )")

        # Wait for 1 second before fetching data again
        time.sleep(0.5)

except KeyboardInterrupt:
    # Handle script termination gracefully
    print("Terminating the data fetching loop")

# Shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
