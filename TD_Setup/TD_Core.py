import pandas as pd

def create_dataframe(hdata):
    data = pd.DataFrame(hdata['candles'][:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='s')
    data['timestamp'] = data['timestamp'].dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata')
    data['timestamp'] = data['timestamp'].dt.tz_localize(None)
    return data


def calculate_td_setup(data):
    data['buy_setup'] = 0
    data['sell_setup'] = 0

    for i in range(4, len(data)):
        # Buy Setup
        if data['close'][i] > data['close'][i - 4]:
            data.at[i, 'buy_setup'] = data['buy_setup'][i - 1] + 1 if data['buy_setup'][i - 1] >= 0 else 1
        else:
            data.at[i, 'buy_setup'] = 0

        # Sell Setup
        if data['close'][i] < data['close'][i - 4]:
            data.at[i, 'sell_setup'] = data['sell_setup'][i - 1] + 1 if data['sell_setup'][i - 1] >= 0 else 1
        else:
            data.at[i, 'sell_setup'] = 0

    return data
