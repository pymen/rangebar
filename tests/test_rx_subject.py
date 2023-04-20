from rx.subject import Subject
from rx.operators import map as op_map
import asyncio
import pytest

def op_map_append_str(e):
    return ','.join([str(e), 'appended'])

@pytest.mark.asyncio
async def test_rx_subject():
    sub1 = Subject()
    sub1.pipe(op_map(op_map_append_str)).subscribe(lambda x: print(f'received event: {x}'))
    for i in range(50):
        sub1.on_next(i)
    # await asyncio.sleep(10)

@pytest.mark.asyncio
async def test_map_object():
    sub1 = Subject()
    sub1.pipe(op_map(op_map_append_str)).subscribe(lambda x: print(f'received event: {x}'))
    for i in range(50):
        sub1.on_next(i)
    # await asyncio.sleep(10)


    
