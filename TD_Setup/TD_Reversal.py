import INDICATORS.ATR as ATR

def calculate_td_support_resistance(data):
    data['support_level'] = 0.0
    data['resistance_level'] = 0.0
    data['buy_counter'] = 0
    data['sell_counter'] = 0

    for i in range(1, len(data)):
        # if data['buy_setup'][i] == 6:
        if data['buy_setup'][i] > 1 and data['buy_setup'][i] % 2 == 0:
            data.at[i - 1, 'sell_counter'] = -1
            data.at[i, 'support_level'] = data.at[i, 'low']
        # if data['sell_setup'][i] == 6:
        if data['sell_setup'][i] > 1 and data['sell_setup'][i] % 2 == 0:
            data.at[i - 1, 'buy_counter'] = -1
            data.at[i, 'resistance_level'] = data.at[i, 'high']

        data.at[i, 'buy_counter'] = data.at[i - 1, 'buy_counter'] + 1
        data.at[i, 'sell_counter'] = data.at[i - 1, 'sell_counter'] + 1

    return data

# Calculate TD Setup
# df = calculate_td_setup(data)
# df = calculate_td_support_resistance(data)


def generate_trade_signals(data, levels, long=False, short=False):

    data['ATR'] = 0.0
    data['TRADE'] = ' '
    data['Supp_lev'] = 0.0
    data['Resis_lev'] = 0.0
    support_level = 0
    resistance_level = 10 ** 8
    prev_close = 0

    for i in range(len(data)):
        curr_low = data.at[i, 'low']
        curr_high = data.at[i, 'high']
        curr_close = data.at[i, 'close']
        current_true_range = ATR.true_range(curr_high, curr_low, prev_close)  # arguments need to be added
        data.loc[i, 'ATR'] = round(ATR.ATR_object.current_ATR(current_true_range), 2)


        if data["support_level"][i] != 0:
            support_level = data["support_level"][i]
        if data["resistance_level"][i] != 0 :
            resistance_level = data["resistance_level"][i]

        if data.at[i, 'high'] > resistance_level:
            data.at[i, 'TRADE'] = "BUY"
            resistance_level = float('inf')
        elif data.loc[i, 'low'] < support_level:
            data.loc[i, 'TRADE'] = "SELL"
            support_level = 0

        if long:
            resistance_level = float('inf')
            data.at[i, 'TRADE'] = 'BUY'
        elif short:
            support_level = 0
            data.at[i, 'TRADE'] = 'SELL'

        if data.at[i, 'TRADE'] == 'BUY':
            resistance_level = float('inf')
        elif data.at[i, 'TRADE'] == 'SELL':
            support_level = 0

        data.at[i, 'Supp_lev'] = support_level
        data.at[i, 'Resis_lev'] = resistance_level

        prev_close = data.at[i, 'close']
        levels['buy_c'] = data.at[i , 'buy_counter']
        levels['sell_c'] = data.at[i , 'sell_counter']

    # levels['buy_c'] = data.at[len(data) - 1 , 'buy_counter']
    # levels['sell_c'] = data.at[len(data) - 1 , 'sell_counter']
    levels['ATR'] = data.at[len(data) - 1 , 'ATR']
    levels['SUPPORT'] = float(support_level)
    levels['RESISTANCE'] = float(resistance_level)

    return data