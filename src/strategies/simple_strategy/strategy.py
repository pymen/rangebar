from rx.core import Subject
from src.strategies.utils import iterations_back_till_condition
from src.stream_consumers.helpers.dataclasses import Event
from scipy.stats import linregress

class SimpleStrategy:
    per_trade_risk = 0.1
    def __init__(self, client, next_bar: Subject):
        self.client = client
        next_bar.pipe().subscribe(self.on_next_bar)

    def on_next_bar(self, event: Event):
        df = event.df
        current_close = df.Close[-1]
        index = df.index[-1]
        range_size = df.average_adr[-1] * 0.1
        potential_profit = df.average_adr[-1] * 0.15
        
        is_long_rsi = df['rsi'][-1] > 70
        is_long_macd = df['macd'][-1] > df['macd_signal'][-1] > 0
        is_bb_upper_near = self.bb_upper_near(index, current_close, df)
        is_bb_upper_pointing_up = self.bb_upper_pointing_up(index, df)

        is_short_rsi = df['rsi'][-1] < 30
        is_short_macd = df['macd'][-1] < df['macd_signal'][-1] < 0
        is_bb_lower_near = self.bb_lower_near(index, current_close, df)
        is_bb_lower_pointing_down = self.bb_lower_pointing_down(index, df)
   
        if is_long_rsi and is_long_macd and is_bb_upper_near and is_bb_upper_pointing_up:  
            self.client.buy(size=self.per_trade_risk, sl=current_close - range_size, tp=current_close + potential_profit)
        elif is_short_rsi and is_short_macd and is_bb_lower_near and is_bb_lower_pointing_down:
            self.client.sell(size=self.per_trade_risk, sl=current_close + range_size, tp=current_close - potential_profit)

    def bb_upper_near(self, index, close, df):
        try:
            upper_series = df.iloc[:index+1]['bb_upper']
            if len(upper_series) < 2:
                return False
            # print(f'upper_series:\n{str(upper_series)}')
            since = self.iterations_back_till_condition(upper_series, lambda x: x >= close)
            # print(f'bb_upper_near(upper_series >= close): index: {index}, close: {close}, since: {since}')
            return since < 2
        except Exception as e:
            print(f'bb_upper_near: exception: {e.__cause__}')
            raise e
        

    def bb_lower_near(self, index, close, df):
       try:
         lower_series = df.iloc[:index+1]['bb_lower']
         if len(lower_series) < 2:
                return False
        #  print(f'lower_series:\n{str(lower_series)}')
         since = iterations_back_till_condition(lower_series, lambda x: x <= close)
        #  print(f'bb_lower_near(lower_series <= close): index: {index}, close: {close}, since: {since}')
         return since < 2
       except Exception as e:
            print(f'bb_lower_near: exception: {e.__cause__}')
            raise e
              
    def bb_upper_pointing_up(self, index, df):
        bb_seg = df.iloc[index-3:index+1]['bb_upper']
        # print(f'bb_seg: {len(bb_seg)}')
        if len(bb_seg) > 0:
            seg_len = len(bb_seg)
            try:
                slope, _, _, _, _ = linregress(range(seg_len), bb_seg)
                # print(f'bb_upper_pointing_up: seg_len: {seg_len}, slope: {slope}')
                return slope > 0
            except Exception as e:
                print(f'bb_upper_pointing_up: exception: {str(e)}')
        return False

    def bb_lower_pointing_down(self, index, df):
        bb_seg = df.iloc[index-3:index+1]['bb_lower']
        # print(f'bb_seg: {len(bb_seg)}')
        if len(bb_seg) > 0:
            seg_len = len(bb_seg)
            try:
                slope, _, _, _, _ = linregress(range(seg_len), bb_seg)
                # print(f'bb_lower_pointing_down: seg_len: {seg_len}, slope: {slope}')
                return slope < 0
            except Exception as e:
                print(f'bb_lower_pointing_down: exception: {str(e)}')  
           
        return False
        