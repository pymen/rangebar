from rx.subject import Subject
from src.helpers.dataclasses import TickEvent
from scipy.stats import linregress
import logging
from src.strategies.order_client import OrderClient

class SimpleStrategy:
    per_trade_risk_perc_equity = 0.1
    per_trade_amount_mbtc = 0.001
    rsi_upper_limit = 70
    rsi_lower_limit = 30
    stop_loss_aadr_multiplier = 0.1
    potential_profit_aadr_multiplier = 0.15
    def __init__(self, client: OrderClient, next_bar: Subject):
        self.client = client
        next_bar.pipe().subscribe(self.on_next_bar)

    def on_next_bar(self, e: TickEvent):
        df = e.df
        row = df.tail(1)
        current_close = row['Close']
        index = df.index[-1]
        numeric_index = self.df.index.get_loc(index)
        stop_loss_magnitude = row['average_adr'] * self.stop_loss_aadr_multiplier
        potential_profit_magnitude = row['average_adr'] * self.potential_profit_aadr_multiplier

        sl_buy = current_close - stop_loss_magnitude
        tp_buy = current_close + potential_profit_magnitude
        sl_sell = current_close + stop_loss_magnitude
        tp_sell = current_close - potential_profit_magnitude
        
        is_long_rsi = row['rsi'] > self.rsi_upper_limit
        is_long_macd = row['macd'] > row['macd_signal'] > 0
        is_bb_upper_near = self.bb_upper_near(numeric_index, row)
        is_bb_upper_pointing_up = self.bb_upper_pointing_up(numeric_index)

        is_short_rsi = row['rsi'] < self.rsi_lower_limit
        is_short_macd = row['macd'] < row['macd_signal'] < 0
        is_bb_lower_near = self.bb_lower_near(numeric_index, row)
        is_bb_lower_pointing_down = self.bb_lower_pointing_down(numeric_index)
        is_bb_dist_above = row['bb_distance'] > self.anti_squeeze_distance

        if is_long_rsi and is_long_macd and is_bb_upper_near and is_bb_upper_pointing_up and is_bb_dist_above:  
            self.client.buy(symbol=e.symbol, quantity=self.per_trade_amount_mbtc, stop_loss=sl_buy, take_profit=tp_buy, entry_price=None)
        elif is_short_rsi and is_short_macd and is_bb_lower_near and is_bb_lower_pointing_down and is_bb_dist_above:
            self.client.sell(symbol=e.symbol, quantity=self.per_trade_amount_mbtc, stop_loss=sl_sell, take_profit=tp_sell, entry_price=None)

    def bb_upper_near(self, index, row):
        try:
            upper_series = self.df.iloc[:index+1]['bb_upper']
            if len(upper_series) < 2:
                return False
            # logging.info(f'upper_series:\n{str(upper_series)}')
            close = row['Close']
            since = self.iterations_back_till_condition(upper_series, lambda x: x >= close)
            # logging.info(f'bb_upper_near(upper_series >= close): index: {index}, close: {close}, since: {since}')
            return since < 2
        except Exception as e:
            logging.info(f'bb_upper_near: exception: {e.__cause__}')
            raise e
        

    def bb_lower_near(self, index, row):
       try:
         lower_series = self.df.iloc[:index+1]['bb_lower']
         if len(lower_series) < 2:
                return False
        #  logging.info(f'lower_series:\n{str(lower_series)}')
         close = row['Close']
         since = self.iterations_back_till_condition(lower_series, lambda x: x <= close)
        #  logging.info(f'bb_lower_near(lower_series <= close): index: {index}, close: {close}, since: {since}')
         return since < 2
       except Exception as e:
            logging.info(f'bb_lower_near: exception: {e.__cause__}')
            raise e
       
    def iterations_back_till_condition(self, series, condition):
        count = 0
        for value in series[::-1]:
            if condition(value):
                break
            count += 1
        return count
       
    def bb_upper_pointing_up(self, index):
        bb_seg = self.df.iloc[index-3:index+1]['bb_upper']
        # logging.info(f'bb_seg: {len(bb_seg)}')
        if len(bb_seg) > 0:
            seg_len = len(bb_seg)
            try:
                slope, _, _, _, _ = linregress(range(seg_len), bb_seg)
                # logging.info(f'bb_upper_pointing_up: seg_len: {seg_len}, slope: {slope}')
                return slope > 0
            except Exception as e:
                logging.info(f'bb_upper_pointing_up: exception: {str(e)}')
        return False

    def bb_lower_pointing_down(self, index):
        bb_seg = self.df.iloc[index-3:index+1]['bb_lower']
        # logging.info(f'bb_seg: {len(bb_seg)}')
        if len(bb_seg) > 0:
            seg_len = len(bb_seg)
            try:
                slope, _, _, _, _ = linregress(range(seg_len), bb_seg)
                # logging.info(f'bb_lower_pointing_down: seg_len: {seg_len}, slope: {slope}')
                return slope < 0
            except Exception as e:
                logging.info(f'bb_lower_pointing_down: exception: {str(e)}')  
        return False