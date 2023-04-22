
import numpy as np
import pandas as pd
from src.fetch_historical.historical_kline import HistoricalKline
from src.helpers.dataclasses import IndicatorTickEvent
from src.settings import get_settings
from src.strategies.order_client import OrderClient
from src.strategies.simple_strategy.indicators import SimpleStrategyIndicators
from src.strategies.simple_strategy.strategy import SimpleStrategy
from src.stream_consumers.transformers.range_bars import RangeBar
from src.util import clear_logs, get_logger
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject
from rx.scheduler.eventloop import AsyncIOScheduler
import rx.operators as op
import time
import asyncio
import pytest
from tests.utils import get_test_out_absolute_path



def new_instance():
    main = Subject()
    settings = get_settings('bi')
    ws_client = UMFuturesWebsocketClient(stream_url=settings['stream_url'])
    window = Window(ws_client, main)
    return window, main

def test_relative_adr_range_size():
    def adr(df: pd.DataFrame) -> float:
        df['date'] = df.copy().index.date
        daily_high_low = df.groupby('date')['high', 'low'].agg(['max', 'min'])
        daily_high_low['adr'] = daily_high_low[(
            'high', 'max')] - daily_high_low[('low', 'min')]
        return np.mean(daily_high_low['adr'])

    def relative_adr_range_size(df_in: pd.DataFrame, resample_arg: str = 'W'):
        groups = df_in.resample(resample_arg)
        df_out = pd.DataFrame()
        for _, group in groups:
            week_day_seg = group.copy()
            average_adr = adr(week_day_seg)
            week_day_seg['average_adr'] = average_adr
            df_out = pd.concat([df_out, week_day_seg])
        return df_out

    def adv(df: pd.DataFrame, window=14):
        result = df['volume'].rolling(window=window).mean()
        result.fillna(0, inplace=True)
        df['adv'] = result
        return df
    
    csv_path = get_test_out_absolute_path('df_window.csv')
    df_window = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    df_window.sort_index(inplace=True)
    df = adv(relative_adr_range_size(df_window))
    df.to_csv(csv_path)
    assert len(df) > 0

def pytest_configure(config):
    def pytest_shutdown_hook():
        print("Tests are shutting down...")
        if interval_task is not None:
            interval_task.cancel()
    config.add_cleanup(pytest_shutdown_hook)

    
interval_task: asyncio.Task = None
@pytest.mark.asyncio
async def test_range_bars():
    global interval_task
    clear_logs()
    logger = get_logger('RangeBarsTest')
    logger.info('started')
    window, main = new_instance()
    main.pipe(op.filter(lambda o: isinstance(o, IndicatorTickEvent))).subscribe(lambda x: logger.info(f'IndicatorTickEvent: tick test: {str(x)}'))
    window.init_subscriptions()
    RangeBar(window, main)
    HistoricalKline(main)
    SimpleStrategyIndicators(main)
    client: OrderClient = OrderClient()
    SimpleStrategy(client, main)
    window.start()
    interval_task = asyncio.create_task(window.start_interval_save())





