from typing import Dict, List
import pandas as pd
import datetime as dt
import os
from src.settings import get_settings
from src.utility import get_file_path
from rx.core import Subject
from src.helpers.dataclasses import Event

class Window:

    symbol_dict_df_dict: Dict[str, Dict[str, pd.DataFrame]] = {}
    symbol_dict_df_dict_added_row_count: Dict[str, Dict[str, int]] = {}
    consumers: Dict[str, Dict[str, object]] = {}
    prune_started = False
    
    def __init__(self, ws_client, calculate_indicators: Subject):
        self.calculate_indicators = calculate_indicators
        self.settings = get_settings('app')
        for symbols_config in self.settings['symbols_config']:
            df = self.load_symbol_window_data(symbols_config['symbol'])
            if bool(df):
                self.symbol_dict_df_dict[symbols_config['symbol']] = df
            else:
                self.symbol_dict_df_dict[symbols_config['symbol']] = {}    
        self.ws_client = ws_client
        # self.timer = threading.Timer(60, self.prune_windows)
        
    def start(self):
        self.ws_client.start()

    def add_consumer(self, consumer: object):
        for symbols_config in self.settings['symbols_config']:
            self.consumers.setdefault(symbols_config['symbol'], {})
            self.consumers[symbols_config['symbol']][consumer.df_name] = consumer   

    def load_symbol_window_data(self, symbol) -> Dict[str, pd.DataFrame]:
        df_names = self.get_df_names_from_csv_paths()
        df_dict = {}
        for df_name in df_names:
            path = self.get_symbol_window_csv_path(symbol, df_name)
            if os.path.exists(path):
                df = pd.read_csv(path, index_col=0, parse_dates=True)
                df.sort_index(inplace=True)
                # Convert last_window_end to a datetime object
                last_window_end = df.index[-1] # dt.datetime.strptime(df.index[-1], "%Y-%m-%d %H:%M:%S.%f")
                first_window_start = df.index[0] # dt.datetime.strptime(df.index[0], "%Y-%m-%d %H:%M:%S.%f")
                print(f"last_window_end: {type(last_window_end)}, first_window_start: {type(first_window_start)}")
                # Convert integer to timedelta object
                window_timedelta = dt.timedelta(minutes=int(self.settings['window']))
                # Subtract timedelta from datetime object
                window_start = last_window_end - window_timedelta
                if window_start > first_window_start:
                    df = df.loc[window_start:]
                df_dict[df_name] = df
        return df_dict

    def prune_windows(self):
        for symbols_config, df_dict in self.symbol_dict_df_dict.items():
            self.prune_symbol_window(symbols_config['symbol'], df_dict)

    # FIXME: This is not working
    # Define a function named prune_symbol_window that takes in two arguments, symbol and df_dict
    def prune_symbol_window(self, symbol: str, df_dict: Dict[str, pd.DataFrame]):
        pass
        # Loop through the keys of the dictionary df_dict
        for df_name in df_dict.keys():
            # Calculate the rolling window using the value of the current key
            rolling_window = df_dict[df_name].rolling(window=f"{self.settings['window']}min")
            # Check if the rolling window has valid values
            if rolling_window.has_valid_values():
                # Get the end time of the last window
                last_window_end = rolling_window.end_time[-1]
                # Get the data to drop from the start of the dataframe up to the last window end
                data_to_drop = df_dict[df_name][:last_window_end]
                # Append the data to the CSV file
                data_to_drop.to_csv(self.get_symbol_window_csv_path(symbol, df_name), mode='a', header=False)
                # Remove the dropped data from the dataframe
                df_dict[df_name] = df_dict[df_name][last_window_end:]
                # Update the symbol_dict_df_dict with the new rolling window
                self.symbol_dict_df_dict[symbol][df_name] = rolling_window
    

    def save_symbol_window_data(self):
        for symbol, df_dict in self.symbol_dict_df_dict.items():
            for df_name, df in df_dict.items():
                df.to_csv(self.get_symbol_window_csv_path(symbol, df_name))

    def shutdown(self):
        self.ws_client.stop()
        self.save_symbol_window_data()

    def get_symbol_window_csv_path(self, symbol: str, df_name: str) -> str:
        return get_file_path(f'symbol_windows/{symbol}-{df_name}.csv')
 
    def get_df_names_from_csv_paths(self) -> List[str]:
        dir_path = get_file_path(f'symbol_windows/')
        file_list = os.listdir(dir_path)
        file_list = [f for f in file_list if (f.endswith(
            '.csv') and os.path.isfile(os.path.join(dir_path, f)))]
        symbol_dict_names = self.group_by_prefix(file_list)
        if len(symbol_dict_names) > 0:
            df_names = [name[name.find('-')+1:name.find('.')] for name in symbol_dict_names[next(iter(symbol_dict_names))]]
            return df_names
        else:
            return []

    def group_by_prefix(self, strings) -> List[List[str]]:
        groups = {}
        for string in strings:
            prefix = string.split('-')[0]
            if prefix not in groups:
                groups[prefix] = []
            groups[prefix].append(string)
        return groups

    # Define a function to append a row to a dataframe
    def append_row(self, symbol: str, df_name: str, row: pd.Series, index: List[str] = None):
        # Check if pruning has started and start the timer if not
        if not self.prune_started:
            self.prune_started = True
            # self.timer.start()
        # Create a dictionary of dataframes for each symbol and dataframe name
        self.symbol_dict_df_dict.setdefault(symbol, {}).setdefault(df_name, pd.DataFrame())
        # Convert the timestamp to datetime format and set it as the index
        row['timestamp'] = pd.to_datetime(row['timestamp'], unit='ms')
        # Concatenate the new row with the existing dataframe and set the index to the timestamp
        row_as_frame = row.to_frame().T
        if index is None:
            row_as_frame.set_index('timestamp', inplace=True)
        else:
            row_as_frame.set_index(index, inplace=True)    
        self.symbol_dict_df_dict[symbol][df_name] = pd.concat([self.symbol_dict_df_dict[symbol][df_name], row_as_frame])  
        # Create a dictionary to keep track of the number of rows added to each dataframe
        self.symbol_dict_df_dict_added_row_count.setdefault(symbol, {}).setdefault(df_name, 1)
        # Increment the count for the current dataframe
        self.symbol_dict_df_dict_added_row_count[symbol][df_name] += 1
        self.eval_count_triggers()
    

    def get_consumer_triggers(self, consumer):
        triggers = []
        for attr in dir(consumer):
            if callable(getattr(consumer, attr)):
                func = getattr(consumer, attr)
                if hasattr(func, 'is_derived_consumer_trigger'):
                    triggers.append(func)
        return triggers

    def get_symbol_config(self, symbol: str):
        symbols_config = self.settings['symbols_config']
        return [d for d in symbols_config if d['symbol'] == symbol]    


    def eval_count_triggers(self):
        for symbol, consumer_dict in self.consumers.items():
            symbol_config = self.get_symbol_config(symbol)
            for df_name, consumer in consumer_dict.items():
                triggers = self.get_consumer_triggers(consumer)
                for trigger in triggers:
                    count = getattr(trigger, 'count')
                    derived_df_name = getattr(trigger, 'df_name')
                    if count is not None: 
                      if self.symbol_dict_df_dict_added_row_count[symbol][df_name] >= count:
                        self.symbol_dict_df_dict.setdefault(symbol, {}).setdefault(derived_df_name, pd.DataFrame())
                        try:
                            pre_existing_derived_df = self.symbol_dict_df_dict[symbol][derived_df_name]
                            derived_df = trigger(self.symbol_dict_df_dict[symbol][df_name], symbol_config)
                            print(f"eval_count_triggers ~ derived_df.columns: {derived_df.columns}")
                            print(f"eval_count_triggers ~ pre_existing_derived_df.columns: {pre_existing_derived_df.columns}")
                            pre_existing_derived_df = derived_df # pd.concat([pre_existing_derived_df, derived_df], ignore_index=True)
                            self.calculate_indicators.next(Event(f'{symbol}.{df_name}', derived_df))  
                        except Exception as e:
                            print(f"eval_count_triggers ~ Exception: {e}")
                       
                        self.symbol_dict_df_dict_added_row_count[symbol][df_name] = 0
                   

