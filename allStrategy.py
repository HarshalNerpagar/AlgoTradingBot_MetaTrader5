import time
from datetime import datetime, timedelta

import TD_Setup.TD_Core as TD
import TD_Setup.TD_Breakout as TDBO
import TD_Setup.TD_Reversal as TDR
import TD_Setup.TD_SR_Levels as TDSR
from Logging import logger
import MetaTrader5 as mt5
import pandas as pd
import pytz
from Orders import BUY_LIMIT_ORDER as MT5_Buy_Order
from Orders import SELL_LIMIT_ORDER as MT5_Sell_Order
from Orders import MODIFY_SL as MT5_SL_Modify

# mt5.initialize('C:/Program Files/MetaTrader 5 EXNESS/terminal64.exe')
class TradingStrategy:
    def __init__(self):
        self.MULTIPLAYER = 1.5
        self.RISK_TO_REWARD = 5
        self.BREAK_EVEN_POINT = 0.3
        self.TDR_levels = {'SUPPORT': 0, 'RESISTANCE': 0, 'ATR': 0, 'buy_c': 0, 'sell_c': 0}
        self.TDBO_levels = {'SUPPORT': 0, 'RESISTANCE': 0, 'ATR': 0, 'counter': 0}
        self.TDSR_levels = {'SUPPORT': 0, 'RESISTANCE': 0, 'ATR': 0}


        # TDSR Strategy Variable
        self.TDSR_LONG = False
        self.TDSR_SHORT = False
        self.TDSR_ENTRY = 0
        self.TDSR_STOP_LOSS = 0
        self.TDSR_TARGET = 0
        self.TDSR_ORDER_ID_BUY = 0
        self.TDSR_ORDER_ID_SELL = 0
        self.TDSR_prev_support = 0
        self.TDSR_prev_resistance = 0

        # TDBO Strategy Variable
        self.TDBO_LONG = False
        self.TDBO_SHORT = False
        self.TDBO_ENTRY = 0
        self.TDBO_STOP_LOSS = 0
        self.TDBO_TARGET = 0
        self.TDBO_ORDER_ID_BUY = 0
        self.TDBO_ORDER_ID_SELL = 0
        self.TDBO_prev_support = 0
        self.TDBO_prev_resistance = 0
        # self.TDBO_PENDING_ORDERS = []
        # self.TDBO_PENDING_ORDERS_FLAG = False

        # TDR Strategy Variable
        self.TDR_LONG = False
        self.TDR_SHORT = False
        self.TDR_ENTRY = 0
        self.TDR_STOP_LOSS = 0
        self.TDR_TARGET = 0
        self.TDR_ORDER_ID_BUY = 0
        self.TDR_ORDER_ID_SELL = 0
        self.TDR_prev_support = 0
        self.TDR_prev_resistance = 0
        # self.TDR_PENDING_ORDERS = []
        # self.TDR_PENDING_ORDERS_FLAG = False

        self.sl_points = 0
        self.prev_minute = None
        self.print_flag = True




    def perform_task(self):
        # logger.info(MT5_Sell_Order(67660.54, 67819.63, 67535.08))
        global TDR_data_df, TDBO_data_df, TDSR_data_df
        now = datetime.now()
        try:
            if not mt5.initialize():
                print("initialize() failed, error code =", mt5.last_error())
                quit()

            timezone = pytz.timezone("Etc/UTC")
            utc_to = datetime.now(timezone)
            utc_from = utc_to - timedelta(hours=5)
            symbol = "BTCUSD"
            timeframe = mt5.TIMEFRAME_M1

            rates = mt5.copy_rates_range(symbol, timeframe, utc_from, utc_to)
            mt5.shutdown()
            rates_frame = pd.DataFrame(rates[:-1])
            rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

            core_data = TD.calculate_td_setup(rates_frame)

            # TDSR Strategy
            TDSR_data_df = TDSR.calculate_td_support_resistance(core_data)
            TDSR_data_df = TDSR.generate_trade_signals(TDSR_data_df, self.TDSR_levels, self.TDSR_LONG, self.TDSR_SHORT)
            TDSR_data_df.to_csv('TDSR_output.csv', sep='\t', index=False)

            # TDBO Strategy
            TDBO_data_df = TDBO.calculate_td_support_resistance(core_data)
            TDBO_data_df = TDBO.generate_trade_signals(TDBO_data_df, self.TDBO_levels, self.TDBO_LONG, self.TDBO_SHORT)
            TDBO_data_df.to_csv('TDBO_output.csv', sep='\t', index=False)

            # TDR Strategy
            TDR_data_df = TDR.calculate_td_support_resistance(core_data)
            TDR_data_df = TDR.generate_trade_signals(TDR_data_df, self.TDR_levels, self.TDR_LONG, self.TDR_SHORT)
            TDR_data_df.to_csv('TDR_output.csv', sep='\t', index=False)


        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")

        TDSR_candle_high = TDSR_data_df.at[len(TDSR_data_df) - 1, 'high']
        TDSR_candle_low = TDSR_data_df.at[len(TDSR_data_df) - 1, 'low']

        TDBO_candle_high = TDBO_data_df.at[len(TDBO_data_df) - 1, 'high']
        TDBO_candle_low = TDBO_data_df.at[len(TDBO_data_df) - 1, 'low']

        TDR_candle_high = TDR_data_df.at[len(TDR_data_df) - 1, 'high']
        TDR_candle_low = TDR_data_df.at[len(TDR_data_df) - 1, 'low']

        if self.TDSR_LONG:
            self.TDSR_STOP_LOSS = self.trailing_stops(TDSR_candle_high, self.TDSR_LONG, self.TDSR_SHORT,
                                                      self.TDSR_ENTRY, self.TDSR_STOP_LOSS, self.sl_points)
            MT5_SL_Modify(self.TDSR_ORDER_ID_BUY, self.TDSR_STOP_LOSS)
        elif self.TDSR_SHORT:
            self.TDSR_STOP_LOSS = self.trailing_stops(TDSR_candle_low, self.TDSR_LONG, self.TDSR_SHORT, self.TDSR_ENTRY,
                                                      self.TDSR_STOP_LOSS, self.sl_points)
            MT5_SL_Modify(self.TDSR_ORDER_ID_SELL, self.TDSR_STOP_LOSS)

        if self.TDBO_LONG:
            self.TDBO_STOP_LOSS = self.trailing_stops(TDBO_candle_high, self.TDBO_LONG, self.TDBO_SHORT,
                                                      self.TDBO_ENTRY, self.TDBO_STOP_LOSS, self.sl_points)
            MT5_SL_Modify(self.TDBO_ORDER_ID_BUY, self.TDBO_STOP_LOSS)
        elif self.TDBO_SHORT:
            self.TDBO_STOP_LOSS = self.trailing_stops(TDBO_candle_low, self.TDBO_LONG, self.TDBO_SHORT, self.TDBO_ENTRY,
                                                      self.TDBO_STOP_LOSS, self.sl_points)
            MT5_SL_Modify(self.TDBO_ORDER_ID_SELL, self.TDBO_STOP_LOSS)

        if self.TDR_LONG:
            self.TDR_STOP_LOSS = self.trailing_stops(TDR_candle_high, self.TDR_LONG, self.TDR_SHORT,
                                                     self.TDR_ENTRY, self.TDR_STOP_LOSS, self.sl_points)
            MT5_SL_Modify(self.TDR_ORDER_ID_BUY, self.TDR_STOP_LOSS)
        elif self.TDR_SHORT:
            self.TDR_STOP_LOSS = self.trailing_stops(TDR_candle_low, self.TDR_LONG, self.TDR_SHORT, self.TDR_ENTRY,
                                                     self.TDR_STOP_LOSS, self.sl_points)
            MT5_SL_Modify(self.TDR_ORDER_ID_SELL, self.TDR_STOP_LOSS)

        # logger.info(self.TDSR_levels)
        # logger.info(self.TDBO_levels)
        # logger.info(self.TDR_levels)

    def cancel_pending_order(self, ticket):
        # Initialize connection to MetaTrader 5

        if not mt5.initialize():
            print("initialize() failed, error code =", mt5.last_error())
            quit()

        # Login to your account
        account_number = 79339868  # Replace with your account number
        password = "your_password"  # Replace with your password
        server = "your_server"  # Replace with your server

        authorized = mt5.login(account_number, password=password, server=server)
        if authorized:
            print(f"Connected to account: {account_number}")
        else:
            print("Failed to connect. Error code: ", mt5.last_error())
            mt5.shutdown()
            quit()

        request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": ticket,
            }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"Failed to cancel order {ticket}, retcode: {result.retcode}")
        else:
                print(f"Successfully canceled order {ticket}")



            # Shutdown the connection
        # mt5.shutdown()

    def connect(self):
        while True:
            now = datetime.now()
            curr_time = now.strftime("%H:%M:%S")
            t = time.localtime()
            curr_sec = time.strftime('%S', t)

            if self.prev_minute != now.strftime("%H:%M"):
                self.perform_task()
                if self.print_flag:
                    logger.info(f'---( ALGO STARTED )---')
                    logger.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} --( 1 Min Data Get Updated )-- ")

                    # self.TDSR_prev_support, self.TDSR_prev_resistance = self.TDSR_levels['SUPPORT'], self.TDSR_levels[
                    #     'RESISTANCE']
                    self.TDBO_prev_support, self.TDBO_prev_resistance = self.TDBO_levels['SUPPORT'], self.TDBO_levels[
                        'RESISTANCE']
                    self.TDR_prev_support, self.TDR_prev_resistance = self.TDR_levels['SUPPORT'], self.TDR_levels[
                        'RESISTANCE']
                    self.print_flag = False

                if self.TDBO_prev_resistance != self.TDBO_levels['RESISTANCE'] and not(self.TDBO_ORDER_ID_BUY):
                    if not mt5.initialize():
                        logger.error(f"initialize() failed, error code = {mt5.last_error()}")
                        quit()
                    selected = mt5.symbol_select("BTCUSD", True)
                    if not selected:
                        logger.error("Failed to select BTCUSD")
                        mt5.shutdown()
                        quit()
                    lasttick = mt5.symbol_info_tick("BTCUSD")
                    logger.success(lasttick)

                    if self.TDBO_ORDER_ID_BUY:
                        self.cancel_pending_order(self.TDBO_ORDER_ID_BUY)

                    self.TDBO_prev_resistance = self.TDBO_levels['RESISTANCE']
                    self.sl_points = round(self.TDBO_levels['ATR'] * self.MULTIPLAYER, 2)
                    self.TDBO_STOP_LOSS = self.TDBO_prev_resistance - self.sl_points
                    self.TDBO_ENTRY = self.TDBO_prev_resistance
                    self.TDBO_TARGET = round(self.TDBO_prev_resistance + (self.sl_points * self.RISK_TO_REWARD), 2)
                    if lasttick.ask >= self.TDBO_ENTRY:
                        self.TDBO_ORDER_ID_BUY = MT5_Buy_Order(self.TDBO_ENTRY, self.TDBO_STOP_LOSS, self.TDBO_TARGET, 'TDBO',True)
                    else:
                        self.TDBO_ORDER_ID_BUY = MT5_Buy_Order(self.TDBO_ENTRY, self.TDBO_STOP_LOSS, self.TDBO_TARGET, 'TDBO')
                    logger.info(f'TDBO BUY_TRADE_TRIGGER --( {self.TDBO_ORDER_ID_BUY} )--')

                elif self.TDBO_prev_support != self.TDBO_levels['SUPPORT'] and not(self.TDBO_ORDER_ID_SELL):
                    if not mt5.initialize():
                        logger.error(f"initialize() failed, error code = {mt5.last_error()}")
                        quit()

                    selected = mt5.symbol_select("BTCUSD", True)
                    if not selected:
                        logger.error("Failed to select BTCUSD")
                        mt5.shutdown()
                        quit()
                    lasttick = mt5.symbol_info_tick("BTCUSD")

                    if self.TDBO_ORDER_ID_SELL:
                        self.cancel_pending_order(self.TDBO_ORDER_ID_SELL)

                    self.TDBO_prev_support = self.TDBO_levels['SUPPORT']
                    self.sl_points = round(self.TDBO_levels['ATR'] * self.MULTIPLAYER, 2)
                    self.TDBO_STOP_LOSS = self.TDBO_prev_support + self.sl_points
                    self.TDBO_ENTRY = self.TDBO_prev_support
                    self.TDBO_TARGET = round(self.TDBO_prev_support - (self.sl_points * self.RISK_TO_REWARD), 2)
                    if lasttick.ask <= self.TDBO_ENTRY:
                        self.TDBO_ORDER_ID_BUY = MT5_Buy_Order(self.TDBO_ENTRY, self.TDBO_STOP_LOSS, self.TDBO_TARGET,'TDBO',True)
                    else:
                        self.TDBO_ORDER_ID_SELL = MT5_Sell_Order(self.TDBO_ENTRY, self.TDBO_STOP_LOSS, self.TDBO_TARGET, 'TDBO')
                    logger.info(f'TDBO SELL_TRADE_TRIGGER --( {self.TDBO_ORDER_ID_SELL} )--')

                if self.TDSR_prev_resistance != self.TDSR_levels['RESISTANCE'] and not(self.TDSR_ORDER_ID_BUY):
                    if self.TDSR_ORDER_ID_BUY:
                        self.cancel_pending_order(self.TDSR_ORDER_ID_BUY)
                    self.TDSR_prev_resistance = self.TDSR_levels['RESISTANCE']
                    self.sl_points = round(self.TDSR_levels['ATR'] * self.MULTIPLAYER, 2)
                    self.TDSR_STOP_LOSS = self.TDSR_prev_resistance - self.sl_points
                    self.TDSR_ENTRY = self.TDSR_prev_resistance
                    self.TDSR_TARGET = round(self.TDSR_prev_resistance + (self.sl_points * self.RISK_TO_REWARD), 2)
                    logger.info(f'{self.TDSR_ENTRY} {self.TDSR_STOP_LOSS} {self.TDSR_TARGET}')
                    self.TDSR_ORDER_ID_BUY = MT5_Buy_Order(self.TDSR_ENTRY, self.TDSR_STOP_LOSS, self.TDSR_TARGET, 'TDSR')
                    logger.info(f'TDSR BUY_TRADE_TRIGGER --( {self.TDSR_ORDER_ID_BUY} )--')

                elif self.TDSR_prev_support !=  self.TDSR_levels['SUPPORT'] and not(self.TDSR_ORDER_ID_SELL):
                    if self.TDSR_ORDER_ID_SELL:
                        self.cancel_pending_order(self.TDSR_ORDER_ID_SELL)
                    self.TDSR_prev_support = self.TDSR_levels['SUPPORT']
                    self.sl_points = round(self.TDSR_levels['ATR'] * self.MULTIPLAYER, 2)
                    self.TDSR_STOP_LOSS = self.TDSR_prev_support + self.sl_points
                    self.TDSR_ENTRY = self.TDSR_prev_support
                    self.TDSR_TARGET = round(self.TDSR_prev_support - (self.sl_points * self.RISK_TO_REWARD), 2)
                    logger.info(f'{self.TDSR_ENTRY} {self.TDSR_STOP_LOSS} {self.TDSR_TARGET}')
                    self.TDSR_ORDER_ID_SELL = MT5_Sell_Order(self.TDSR_ENTRY, self.TDSR_STOP_LOSS, self.TDSR_TARGET, 'TDSR')
                    logger.info(f'TDSR SELL_TRADE_TRIGGER --( {self.TDSR_ORDER_ID_SELL} )--')

                if self.TDR_prev_resistance != self.TDR_levels['RESISTANCE'] and not(self.TDR_ORDER_ID_BUY):
                    if not mt5.initialize():
                        logger.error(f"initialize() failed, error code = {mt5.last_error()}")
                        quit()

                    selected = mt5.symbol_select("BTCUSD", True)
                    if not selected:
                        logger.error("Failed to select BTCUSD")
                        mt5.shutdown()
                        quit()
                    lasttick = mt5.symbol_info_tick("BTCUSD")
                    if self.TDR_ORDER_ID_BUY:
                        self.cancel_pending_order(self.TDR_ORDER_ID_BUY)
                    self.TDR_prev_resistance = self.TDR_levels['RESISTANCE']
                    self.sl_points = round(self.TDR_levels['ATR'] * self.MULTIPLAYER, 2)
                    self.TDR_STOP_LOSS = self.TDR_prev_resistance - self.sl_points
                    self.TDR_ENTRY = self.TDR_prev_resistance
                    self.TDR_TARGET = round(self.TDR_prev_resistance + (self.sl_points * self.RISK_TO_REWARD), 2)
                    if lasttick.ask >= self.TDR_ENTRY:
                        self.TDR_ORDER_ID_BUY = MT5_Buy_Order(self.TDR_ENTRY, self.TDR_STOP_LOSS, self.TDR_TARGET,'TDR', True)
                    else:
                        self.TDR_ORDER_ID_BUY = MT5_Buy_Order(self.TDR_ENTRY, self.TDR_STOP_LOSS, self.TDR_TARGET, 'TDR',)
                    logger.info(f'TDR BUY_TRADE_TRIGGER --( {self.TDR_ORDER_ID_BUY} )--')

                elif self.TDR_prev_support != self.TDR_levels['SUPPORT'] and not(self.TDR_ORDER_ID_SELL):
                    if not mt5.initialize():
                        logger.error(f"initialize() failed, error code = {mt5.last_error()}")
                        quit()

                    selected = mt5.symbol_select("BTCUSD", True)
                    if not selected:
                        logger.error("Failed to select BTCUSD")
                        mt5.shutdown()
                        quit()
                    lasttick = mt5.symbol_info_tick("BTCUSD")
                    if self.TDR_ORDER_ID_SELL:
                        self.cancel_pending_order(self.TDR_ORDER_ID_SELL)
                    self.TDR_prev_support = self.TDR_levels['SUPPORT']
                    self.sl_points = round(self.TDR_levels['ATR'] * self.MULTIPLAYER, 2)
                    self.TDR_STOP_LOSS = self.TDR_prev_support + self.sl_points
                    self.TDR_ENTRY = self.TDR_prev_support
                    self.TDR_TARGET = round(self.TDR_prev_support - (self.sl_points * self.RISK_TO_REWARD), 2)
                    if lasttick.ask <= self.TDR_ENTRY:
                        self.TDR_ORDER_ID_BUY = MT5_Buy_Order(self.TDR_ENTRY, self.TDR_STOP_LOSS, self.TDR_TARGET, 'TDR',True)
                    else:
                        self.TDR_ORDER_ID_SELL = MT5_Sell_Order(self.TDR_ENTRY, self.TDR_STOP_LOSS, self.TDR_TARGET,'TDR' )
                    logger.info(f'TDR SELL_TRADE_TRIGGER --( {self.TDR_ORDER_ID_SELL} )--')

                self.prev_minute = now.strftime("%H:%M")
                # time.sleep(0.2)

            if mt5.positions_get():
                for open_trades in mt5.positions_get():
                    if int(self.TDSR_ORDER_ID_BUY) == open_trades[0]:
                        self.TDSR_LONG = True
                    else:
                        self.TDSR_LONG = False

                    if int(self.TDSR_ORDER_ID_SELL) == open_trades[0]:
                        self.TDSR_SHORT = True
                    else:
                        self.TDSR_SHORT = False

                    if int(self.TDBO_ORDER_ID_BUY) == open_trades[0]:
                        self.TDBO_LONG = True
                    else:
                        self.TDBO_LONG = False

                    if int(self.TDBO_ORDER_ID_SELL) == open_trades[0]:
                        self.TDBO_SHORT = True
                    else:
                        self.TDBO_SHORT = False

                    if int(self.TDR_ORDER_ID_BUY) == open_trades[0]:
                        self.TDR_LONG = True
                    else:
                        self.TDR_LONG = False

                    if int(self.TDR_ORDER_ID_SELL) == open_trades[0]:
                        self.TDR_SHORT = True
                    else:
                        self.TDR_SHORT = False

            if self.TDBO_levels['counter'] > 1:
                if self.TDBO_ORDER_ID_BUY:
                    self.cancel_pending_order(self.TDBO_ORDER_ID_BUY)
                if self.TDBO_ORDER_ID_SELL:
                    self.cancel_pending_order(self.TDBO_ORDER_ID_SELL)
            if self.TDR_levels['buy_c'] > 3:
                if self.TDR_ORDER_ID_BUY:
                    self.cancel_pending_order(self.TDR_ORDER_ID_BUY)
            if self.TDR_levels['sell_c'] > 3:
                if self.TDR_ORDER_ID_SELL:
                    self.cancel_pending_order(self.TDR_ORDER_ID_SELL)


    def trailing_stops(self, curr_price, LONG, SHORT, ENTRY, STOP_LOSS, sl_points):
        # Implement the trailing stop logic
        if LONG:
            if (curr_price - ENTRY) > (sl_points * 4.5):
                if ENTRY + (sl_points * 4) > STOP_LOSS:

                    return round(ENTRY + (sl_points * 4), 2)
                else:
                    return STOP_LOSS
            elif (curr_price - ENTRY) > (sl_points * 4):
                if ENTRY + (sl_points * 3.5) > STOP_LOSS:

                    return round(ENTRY + (sl_points * 3.5), 2)
                else:
                    return STOP_LOSS
            elif (curr_price - ENTRY) > (sl_points * 3.5):
                if ENTRY + (sl_points * 3) > STOP_LOSS:
                    return round(ENTRY + (sl_points * 3), 2)
                else:
                    return STOP_LOSS
            elif (curr_price - ENTRY) > (sl_points * 3):
                if ENTRY + (sl_points * 2.5) > STOP_LOSS:

                    return round(ENTRY + (sl_points * 2.5), 2)
                else:
                    return STOP_LOSS
            elif (curr_price - ENTRY) > (sl_points * 2.5):
                if ENTRY + (sl_points * 2) > STOP_LOSS:

                    return round(ENTRY + (sl_points * 2), 2)
                else:
                    return STOP_LOSS
            elif (curr_price - ENTRY) > (sl_points * 2):
                if ENTRY + (sl_points * 1.5) > STOP_LOSS:

                    return round(ENTRY + (sl_points * 1.5), 2)
                else:
                    return STOP_LOSS
            elif (curr_price - ENTRY) > (sl_points * 0.8):
                if ENTRY + (sl_points * 1.5) > STOP_LOSS:

                    return round(ENTRY + (sl_points * 0.5), 2)
                else:
                    return STOP_LOSS
            elif (curr_price - ENTRY) > (sl_points * self.BREAK_EVEN_POINT):
                if ENTRY > STOP_LOSS:

                    return round(ENTRY, 2)
                else:
                    return STOP_LOSS
            else:
                return STOP_LOSS

        elif SHORT:
            if (ENTRY - curr_price) > (sl_points * 4.5):
                if ENTRY - (sl_points * 4) < STOP_LOSS:

                    return round(ENTRY - (sl_points * 4), 2)
                else:
                    return STOP_LOSS
            elif (ENTRY - curr_price) > (sl_points * 4):
                if ENTRY - (sl_points * 3.5) < STOP_LOSS:

                    return round(ENTRY - (sl_points * 3.5), 2)
                else:
                    return STOP_LOSS
            elif (ENTRY - curr_price) > (sl_points * 3.5):
                if ENTRY - (sl_points * 3) < STOP_LOSS:

                    return round(ENTRY - (sl_points * 3), 2)
                else:
                    return STOP_LOSS
            elif (ENTRY - curr_price) > (sl_points * 3):
                if ENTRY - (sl_points * 2.5) < STOP_LOSS:

                    return round(ENTRY - (sl_points * 2.5), 2)
                else:
                    return STOP_LOSS
            elif (ENTRY - curr_price) > (sl_points * 2.5):
                if ENTRY - (sl_points * 2) < STOP_LOSS:

                    return round(ENTRY - (sl_points * 2), 2)
                else:
                    return STOP_LOSS
            elif (ENTRY - curr_price) > (sl_points * 2):
                if ENTRY - (sl_points * 1.5) < STOP_LOSS:

                    return round(ENTRY - (sl_points * 1.5), 2)
                else:
                    return STOP_LOSS
            elif (ENTRY - curr_price) > (sl_points * 0.8):
                if ENTRY - (sl_points * 0.5) < STOP_LOSS:

                    return round(ENTRY - (sl_points * 0.5), 2)
                else:
                    return STOP_LOSS
            elif (ENTRY - curr_price) > (sl_points * self.BREAK_EVEN_POINT):
                if ENTRY < STOP_LOSS:

                    return round(ENTRY, 2)
                else:
                    return STOP_LOSS
            else:
                return STOP_LOSS


strategy = TradingStrategy()
strategy.connect()




