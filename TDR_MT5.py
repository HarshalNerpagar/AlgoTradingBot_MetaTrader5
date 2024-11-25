import MetaTrader5 as mt5
import time
from datetime import datetime, timedelta
import pandas as pd
import pytz
from MT5_initialize import initialize
import TD_Setup.TD_Reversal as TD
import TD_Setup.TD_Core as Core
from Logging import logger
from Orders import BUY_LIMIT_ORDER as MT5_buy_order
from Orders import SELL_LIMIT_ORDER as MT5_sell_order
from Orders import MODIFY_SL as MT5_SLM
from Orders import cancel_pending_order as MT5_cancel_pending_order



class TradingStrategy:
    def __init__(self):
        self.MULTIPLAYER = 2
        self.MAX_LOSS_CAP = 2
        self.RISK_TO_REWARD = 10
        self.BREAK_EVEN_POINT = 0.5
        self.LOT_SIZE = 0.01
        self.levels = {'SUPPORT': 0, 'RESISTANCE': 0, 'ATR': 0, 'buy_c': 0, 'sell_c': 0}
        self.LONG = False
        self.SHORT = False
        self.ENTRY = 0
        self.STOP_LOSS = 0
        self.TARGET = 0
        self.ORDER_ID_BUY = 0
        self.ORDER_ID_SELL = 0
        self.sl_points = 0
        self.prev_minute = None
        self.print_flag = True
        self.prev_support = 0
        self.prev_resistance = float('inf')


    def perform_task(self):
        now = datetime.now()

        try:
            initialize()
            timezone = pytz.timezone("Etc/UTC")
            utc_to = datetime.now(timezone) - timedelta(minutes=1)
            # utc_from = utc_to - timedelta(hours=11)
            timezone = pytz.UTC
            # Define the date range
            utc_from_str = '31-JUL-2024 09:21:00'
            # utc_to_str = '31-JUL-2024 06:58:00'

            # Convert the date strings to datetime objects
            date_format = "%d-%b-%Y %H:%M:%S"  # Define the date format
            utc_from = datetime.strptime(utc_from_str, date_format).replace(tzinfo=timezone)
            # utc_to = datetime.strptime(utc_to_str, date_format).replace(tzinfo=timezone)

            symbol = "XAUUSD"
            timeframe = mt5.TIMEFRAME_M1
            rates = mt5.copy_rates_range(symbol, timeframe, utc_from, utc_to)
            # mt5.shutdown()
            rates_frame = pd.DataFrame(rates)
            rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
            core_data = Core.calculate_td_setup(rates_frame)
            data_df = TD.calculate_td_support_resistance(core_data)
            data_df = TD.generate_trade_signals(data_df, self.levels, self.LONG, self.SHORT)
            data_df.to_csv('TDR_output.csv', sep='\t', index=False)
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")

        candle_high = data_df.at[len(data_df) - 1, 'high']
        candle_low = data_df.at[len(data_df) - 1, 'low']
        candle_close = data_df.at[len(data_df) - 1, 'close']

        if self.LONG:
            self.STOP_LOSS = self.trailing_stops(candle_close ,self.LONG, self.SHORT, self.ENTRY, self.STOP_LOSS, self.sl_points)
            modify_sl = MT5_SLM(self.ORDER_ID_BUY, self.STOP_LOSS)
        elif self.SHORT:
            self.STOP_LOSS = self.trailing_stops(candle_close, self.LONG, self.SHORT, self.ENTRY, self.STOP_LOSS, self.sl_points)
            modify_sl = MT5_SLM(self.ORDER_ID_SELL, self.STOP_LOSS)



    def connect(self):
        while True:
            now = datetime.now()
            curr_time = now.strftime("%H:%M:%S")
            t = time.localtime()
            curr_sec = time.strftime('%S', t)

            if self.prev_minute != now.strftime("%H:%M"):
                self.perform_task()
                if self.print_flag:
                    logger.info(f'---( TDR )---')
                    logger.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} --( 1 Min Data Get Updated )-- ")

                    self.prev_support, self.prev_resistance  = self.levels['SUPPORT'], self.levels['RESISTANCE']
                    self.print_flag = False

                # logger.success(f"Support --( {self.levels['SUPPORT']} )--  ||  Resistance --( {self.levels['RESISTANCE']} )--")
                self.prev_minute = now.strftime("%H:%M")
            if self.prev_resistance != self.levels['RESISTANCE'] and self.levels['RESISTANCE'] != float('inf'):
                    if self.ORDER_ID_BUY != 0:
                        for pending in mt5.orders_get():
                            if pending.ticket == self.ORDER_ID_BUY:
                                MT5_cancel_pending_order(self.ORDER_ID_BUY)
                                self.ORDER_ID_BUY = 0
                    self.prev_resistance = self.levels['RESISTANCE']
                    # logger.info(f'TDR_Strategy Updated Resistance -( {self.prev_resistance} )-')
                    if self.ORDER_ID_BUY == 0 :
                        self.sl_points = min((self.levels['ATR'] * self.MULTIPLAYER), self.MAX_LOSS_CAP)
                        self.ENTRY = self.levels['RESISTANCE']
                        self.STOP_LOSS = self.ENTRY - self.sl_points
                        self.TARGET = self.ENTRY + (self.sl_points * self.RISK_TO_REWARD)
                        self.ORDER_ID_BUY = MT5_buy_order(self.ENTRY, self.STOP_LOSS, self.TARGET, 'TDR_BUY')

            if self.prev_support != self.levels['SUPPORT'] and self.levels['SUPPORT'] != 0:
                    if self.ORDER_ID_SELL != 0:
                        for pending in mt5.orders_get():
                            if pending.ticket == self.ORDER_ID_SELL:
                                MT5_cancel_pending_order(self.ORDER_ID_SELL)
                                self.ORDER_ID_SELL = 0
                    self.prev_support = self.levels['SUPPORT']
                    # logger.info(f'TDR_Strategy Updated Support -( {self.prev_support} )-')
                    if self.ORDER_ID_SELL == 0:
                        self.sl_points = min((self.levels['ATR'] * self.MULTIPLAYER), self.MAX_LOSS_CAP)
                        self.ENTRY = self.levels['SUPPORT']
                        self.STOP_LOSS = self.ENTRY + self.sl_points
                        self.TARGET = self.ENTRY - (self.sl_points * self.RISK_TO_REWARD)
                        self.ORDER_ID_SELL = MT5_sell_order(self.ENTRY, self.STOP_LOSS, self.TARGET, 'TDR_SELL')
                

            initialize()
            if mt5.positions_get():
                for open_trades in mt5.positions_get():
                    if open_trades.ticket == self.ORDER_ID_BUY:
                        self.LONG = True
                    if open_trades.ticket == self.ORDER_ID_SELL:
                        self.SHORT = True

            if self.SHORT or self.LONG:
                lst_open_orders = []
                lst_pending = []
                lst_order_buy = []
                lst_order_sell = []

                for pending in mt5.orders_get():
                    # if pending.comment == 'TDR_BUY' or pending.comment == 'TDR_SELL':
                    lst_pending.append(pending.ticket)
                for open in mt5.positions_get():
                    if open.comment == 'TDR_BUY':
                        lst_order_buy.append(open.ticket)
                    elif open.comment == 'TDR_SELL':
                        lst_order_sell.append(open.ticket)

                lst_open_orders.extend(lst_order_buy)
                lst_open_orders.extend(lst_order_sell)

                if self.ORDER_ID_BUY not in lst_open_orders and self.ORDER_ID_BUY not in lst_pending:
                    self.ORDER_ID_BUY = 0
                if self.ORDER_ID_SELL not in lst_open_orders and self.ORDER_ID_SELL not in lst_pending:
                    self.ORDER_ID_SELL = 0

                if not (lst_order_buy):
                    self.LONG = False
                if not(lst_order_sell):
                    self.SHORT = False

            if self.levels['buy_c'] >= 3 and self.ORDER_ID_BUY != 0:
                if mt5.orders_get():
                    for orders in mt5.orders_get():
                        if self.ORDER_ID_BUY == orders.ticket and self.ORDER_ID_BUY != 0:
                            MT5_cancel_pending_order(self.ORDER_ID_BUY)
                            self.ORDER_ID_BUY = 0
            elif self.levels['sell_c'] >= 3 and self.ORDER_ID_SELL != 0:
                if mt5.orders_get():
                    for orders in mt5.orders_get():
                        if self.ORDER_ID_SELL == orders.ticket and self.ORDER_ID_SELL != 0:
                            MT5_cancel_pending_order(self.ORDER_ID_SELL)
                            self.ORDER_ID_SELL = 0


            time.sleep(0.5)






    def trailing_stops(self, curr_price, LONG, SHORT, ENTRY, STOP_LOSS, sl_points):
        # Implement the trailing stop logic
        if LONG:
            if (curr_price - ENTRY) > (sl_points * 4.5):
                if ENTRY + (sl_points * 4) > STOP_LOSS:
                    # alert.modifyed_orders("SLM", ENTRY + (sl_points * 4), '1 : 4')
                    return ENTRY + (sl_points * 4)
                else:
                    return STOP_LOSS
            elif (curr_price - ENTRY) > (sl_points * 4):
                if ENTRY + (sl_points * 3.5) > STOP_LOSS:
                    # alert.modifyed_orders("SLM", ENTRY + (sl_points * 3.5), '1 : 3.5')
                    return ENTRY + (sl_points * 3.5)
                else:
                    return STOP_LOSS
            elif (curr_price - ENTRY) > (sl_points * 3.5):
                if ENTRY + (sl_points * 3) > STOP_LOSS:
                    # alert.modifyed_orders("SLM", ENTRY + (sl_points * 3), '1 : 3')
                    return ENTRY + (sl_points * 3)
                else:
                    return STOP_LOSS
            elif (curr_price - ENTRY) > (sl_points * 3):
                if ENTRY + (sl_points * 2.5) > STOP_LOSS:
                    # alert.modifyed_orders("SLM", ENTRY + (sl_points * 2.5), '1 : 2.5')
                    return ENTRY + (sl_points * 2.5)
                else:
                    return STOP_LOSS
            elif (curr_price - ENTRY) > (sl_points * 2.5):
                if ENTRY + (sl_points * 2) > STOP_LOSS:
                    # alert.modifyed_orders("SLM", ENTRY + (sl_points * 2), '1 : 2')
                    return ENTRY + (sl_points * 2)
                else:
                    return STOP_LOSS
            elif (curr_price - ENTRY) > (sl_points * 2):
                if ENTRY + (sl_points * 1.5) > STOP_LOSS:
                    # alert.modifyed_orders("SLM", ENTRY + (sl_points * 1.5), '1 : 1.5')
                    return ENTRY + (sl_points * 1.5)
                else:
                    return STOP_LOSS
            elif (curr_price - ENTRY) > (sl_points * self.BREAK_EVEN_POINT):
                if ENTRY > STOP_LOSS:
                    # alert.modifyed_orders("SLM", ENTRY + (sl_points * self.BREAK_EVEN_POINT), 'Break Even')
                    return ENTRY
                else:
                    return STOP_LOSS
            else:
                return STOP_LOSS

        elif SHORT:
            if (ENTRY - curr_price) > (sl_points * 4.5):
                if ENTRY - (sl_points * 4) < STOP_LOSS:
                    # alert.modifyed_orders("SLM", ENTRY - (sl_points * 4), '1 : 4')
                    return ENTRY - (sl_points * 4)
                else:
                    return STOP_LOSS
            elif (ENTRY - curr_price) > (sl_points * 4):
                if ENTRY - (sl_points * 3.5) < STOP_LOSS:
                    # alert.modifyed_orders("SLM", ENTRY - (sl_points * 3.5), '1 : 3.5')
                    return ENTRY - (sl_points * 3.5)
                else:
                    return STOP_LOSS
            elif (ENTRY - curr_price) > (sl_points * 3.5):
                if ENTRY - (sl_points * 3) < STOP_LOSS:
                    # alert.modifyed_orders("SLM", ENTRY - (sl_points * 3), '1 : 3')
                    return ENTRY - (sl_points * 3)
                else:
                    return STOP_LOSS
            elif (ENTRY - curr_price) > (sl_points * 3):
                if ENTRY - (sl_points * 2.5) < STOP_LOSS:
                    # alert.modifyed_orders("SLM", ENTRY - (sl_points * 2.5), '1 : 2.5')
                    return ENTRY - (sl_points * 2.5)
                else:
                    return STOP_LOSS
            elif (ENTRY - curr_price) > (sl_points * 2.5):
                if ENTRY - (sl_points * 2) < STOP_LOSS:
                    # alert.modifyed_orders("SLM", ENTRY - (sl_points * 2), '1 : 2')
                    return ENTRY - (sl_points * 2)
                else:
                    return STOP_LOSS
            elif (ENTRY - curr_price) > (sl_points * 2):
                if ENTRY - (sl_points * 1.5) < STOP_LOSS:
                    # alert.modifyed_orders("SLM", ENTRY - (sl_points * 1.5), '1 : 1.5')
                    return ENTRY - (sl_points * 1.5)
                else:
                    return STOP_LOSS
            elif (ENTRY - curr_price) > (sl_points * self.BREAK_EVEN_POINT):
                if ENTRY < STOP_LOSS:
                    # alert.modifyed_orders("SLM", ENTRY - (sl_points * self.BREAK_EVEN_POINT), 'Break Even')
                    return ENTRY
                else:
                    return STOP_LOSS
            else:
                return STOP_LOSS


strategy = TradingStrategy()
strategy.connect()
