from rx.subject import Subject
import asyncio
import pytest

@pytest.mark.asyncio
async def test_rx_subject():
    sub1 = Subject()
    sub1.subscribe(lambda x: print(f'received event: {x}'))
    for i in range(50):
        sub1.on_next(i)
    # await asyncio.sleep(10)