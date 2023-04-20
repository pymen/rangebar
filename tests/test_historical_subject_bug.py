import pandas as pd
from rx.subject import Subject, Subject
from src.helpers.dataclasses import FetchHistoricalEvent
from tests.utils import init_logging
import asyncio
import pytest
import time
import rx.operators as op

class Test1:

    def __init__(self, historical: Subject) -> None:
         self.historical = historical
         self.historical.pipe(op.map(self.test_fetch_historical)).subscribe()

    def test_fetch_historical(self, e: FetchHistoricalEvent):
        print(f'fetch_historical: e.type: {type(e)}, e: {str(e)}')     

class Test2:

    def __init__(self, historical: Subject) -> None:
         self.historical = historical
         
    def test_next(self):
        event =  FetchHistoricalEvent('class', 'type', pd.Timestamp.now())
        print('subject on next')
        self.historical.on_next(event)      




def test_bug_case():
    init_logging()
    historical = Subject()
    t1 = Test1(historical)
    t2 = Test2(historical)
    for _ in range(5):
        time.sleep(3)
        t2.test_next()
