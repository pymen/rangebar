import pandas as pd
from rx.subject import AsyncSubject

import rx.operators as op
import asyncio
import pytest

from src.helpers.dataclasses import FetchHistoricalEvent

def op_map_append_str(e):
    return ','.join([str(e), 'appended'])

def test_fetch_historical(e: FetchHistoricalEvent):
    print(f'fetch_historical: e.type: {type(e)}, e: {str(e)}')


@pytest.mark.asyncio
async def test_rx_subject():
    sub1 = AsyncSubject()
    sub1.pipe(op.map(op_map_append_str)).subscribe(lambda x: print(f'received event: {x}'))
    for i in range(50):
        sub1.on_next(i)
    # await asyncio.sleep(10)

@pytest.mark.asyncio
async def test_map_object():
    sub1 = AsyncSubject()
    sub1.pipe(op.map(test_fetch_historical)).subscribe()
    for _ in range(5):
        await asyncio.sleep(3)
        e =  FetchHistoricalEvent('class', 'type', pd.Timestamp.now())
        sub1.on_next(e)


    
