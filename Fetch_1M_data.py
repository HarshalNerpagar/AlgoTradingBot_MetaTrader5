from datetime import datetime, timedelta
import MetaTrader5 as mt5
import pandas as pd
import pytz


# Establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()


timezone = pytz.timezone("Etc/UTC")
utc_to = datetime.now(timezone)
utc_from = utc_to - timedelta(days=1)

symbol = "BTCUSD"
timeframe = mt5.TIMEFRAME_M1

rates = mt5.copy_rates_range(symbol, timeframe, utc_from, utc_to)
mt5.shutdown()
rates_frame = pd.DataFrame(rates[:-1])

rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

# Display data
print("\nDisplay dataframe with data")
print(rates_frame)

# Save DataFrame to a CSV file
csv_file_path = "one_minute_candle_data.csv"
rates_frame.to_csv(csv_file_path, index=False)
print(f"\nData saved to {csv_file_path}")
