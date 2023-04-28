import pandas as pd
from rx.subject import Subject # type: ignore
import rx.operators as op
import asyncio
import pytest
from src.helpers.dataclasses import HistoricalKlineEvent, OrderStatusEvent


def op_map_append_str(e):
    return ','.join([str(e), 'appended'])

def test_fetch_historical(e: HistoricalKlineEvent):
    return e

def test_event_map(e: OrderStatusEvent):
    return e

def test_rx_subject_filter_on_event_instance():
    print('started')
    sub1 = Subject()
    sub1.pipe(op.filter(lambda o: isinstance(o, HistoricalKlineEvent)), op.map(test_fetch_historical)).subscribe(lambda x: print(f'received (expect: FetchHistoricalEvent): {type(x)}'))
    sub1.pipe(op.filter(lambda o: isinstance(o, OrderStatusEvent)), op.map(test_event_map)).subscribe(lambda x: print(f'received (expect: OrderStatusEvent): {type(x)}'))
    for i in range(50):
        if i % 2 == 0:
            e = HistoricalKlineEvent('class', 'type', pd.Timestamp.now())
            sub1.on_next(e)
        else:
            e = OrderStatusEvent('class', 'type', {'a': 1})
            sub1.on_next(e)    
    

@pytest.mark.asyncio
async def test_rx_subject():
    sub1 = Subject()
    sub1.pipe(op.map(op_map_append_str)).subscribe(lambda x: print(f'received event: {x}'))
    for i in range(50):
        sub1.on_next(i)
    # await asyncio.sleep(10)

@pytest.mark.asyncio
async def test_map_object():
    sub1 = Subject()
    sub1.pipe(op.map(test_fetch_historical)).subscribe()
    for _ in range(5):
        await asyncio.sleep(3)
        e =  HistoricalKlineEvent('class', 'type', pd.Timestamp.now())
        sub1.on_next(e)


    
