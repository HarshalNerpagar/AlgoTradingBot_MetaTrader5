import MetaTrader5 as mt5
import time
from datetime import datetime
from Logging import logger

# Display data on the MetaTrader 5 package
logger.info(f"MetaTrader5 package author:  {mt5.__author__}")
logger.info(f"MetaTrader5 package version:  {mt5.__version__}")

# Establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    logger.error(f"initialize() failed, error code = {mt5.last_error()}")
    quit()

selected = mt5.symbol_select("BTCUSD", True)
if not selected:
    logger.error("Failed to select BTCUSD")
    mt5.shutdown()
    quit()

try:

    while True:
        lasttick = mt5.symbol_info_tick("BTCUSD")
        if lasttick is None:
            print("Failed to get tick data")
        else:
            local_time = datetime.fromtimestamp(lasttick.time).strftime('%H:%M:%S')
            curr_price = lasttick.bid
            print(f"Local Time: {local_time} ---( {curr_price} )---")

        # Wait for 1 second before fetching data again
        time.sleep(0.5)

except KeyboardInterrupt:
    # Handle script termination gracefully
    logger.error("Terminating the data fetching loop")

# Shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
