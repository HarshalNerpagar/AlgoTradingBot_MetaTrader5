import MetaTrader5 as mt5
from Logging import logger
from MT5_initialize import initialize

initialize()

def BUY_LIMIT_ORDER(price, sl, tp , strategy,flag=False):
    initialize()
    symbol = "XAUUSD"  # Replace with your desired symbol
    volume = 0.1  # Replace with your desired volume
    deviation = 20  # Allowed deviation in points
    # Create a buy limit order request
    order_request = {
        "action": mt5.TRADE_ACTION_PENDING if flag != True else mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY_STOP if flag != True else mt5.ORDER_TYPE_BUY,
        "price": price if flag != True else mt5.symbol_info_tick(symbol).ask,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 234000,  # Magic number (any unique number to identify your EA)
        "comment": strategy if not flag else strategy,  # Simple comment without special characters
        "type_time": mt5.ORDER_TIME_GTC,  # Good till canceled
        "type_filling": mt5.ORDER_FILLING_RETURN if not flag else mt5.ORDER_FILLING_IOC,
    }
    # Send the order
    result = mt5.order_send(order_request) #217927971
    logger.success(f'{result.request.comment} | ENTRY: {round(result.request.price,3)} | SL: {round(result.request.sl, 3)} | TP: {round(result.request.tp, 3)}')
    # logger.success(f'{result}')
    return list(result)[2]


def SELL_LIMIT_ORDER(price, sl, tp, strategy, flag=False):
    initialize()
    symbol = "XAUUSD"  # Replace with your desired symbol
    volume = 0.1  # Replace with your desired volume
    deviation = 20  # Allowed deviation in points
    # Create a buy limit order request
    order_request = {
        "action": mt5.TRADE_ACTION_PENDING if flag != True else mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL_STOP if flag != True else mt5.ORDER_TYPE_SELL,
        "price": price if flag != True else mt5.symbol_info_tick(symbol).bid,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 234000,  # Magic number (any unique number to identify your EA)
        "comment": strategy if not flag else strategy,  # Simple comment without special characters
        "type_time": mt5.ORDER_TIME_GTC,  # Good till canceled
        "type_filling": mt5.ORDER_FILLING_RETURN if not flag else mt5.ORDER_FILLING_IOC,
    }
    # Send the order
    result = mt5.order_send(order_request)  # 217927971
    logger.success(f'{result.request.comment} | ENTRY: {round(result.request.price, 3)} | SL: {round(result.request.sl, 3)} | TP: {round(result.request.tp, 3)}')
    # logger.success(f'{result.comment}')
    return list(result)[2]

def MODIFY_SL(ticket, new_sl):
    initialize()
    position = mt5.positions_get(ticket=ticket)
    if position:
        position = position[0]  # Get the first (and only) position
        # Create a request to modify the Stop Loss
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "sl": new_sl,
            "symbol": position.symbol,
            "comment": "Modify SL"
        }
        # Send the request
        result = mt5.order_send(request)
        # logger.success(f'SL Modifies {ticket} | SL: {new_sl}')
        return result
    else:
        logger.error(f"Position with ticket {ticket} not found.")
        return None

def cancel_pending_order(ticket):
        initialize()
        request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": ticket,
            }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Failed to cancel order {ticket}, retcode: {result.retcode}")
        else:
                logger.success(f"Successfully canceled order {ticket}")


