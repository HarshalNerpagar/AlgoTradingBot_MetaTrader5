import MetaTrader5 as mt5
from Logging import logger

def initialize():
    if not mt5.initialize(login=175886275, server="Exness-MT5Trial7", password="Harshal@123"):
        print("initialize() failed, error code =", mt5.last_error())
        quit()

    selected = mt5.symbol_select("XAUUSD", True)
    if not selected:
        logger.error("Failed to select XAUUSD")
        print("Failed to select XAUUSD, error code =", mt5.last_error())
        mt5.shutdown()
        quit()

    # Uncomment the next line if you want to log the MetaTrader 5 version
    # logger.info(mt5.version())

initialize()
