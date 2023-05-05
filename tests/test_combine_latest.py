from rx import combine_latest, interval
from rx.subject import Subject  # type: ignore
import rx.operators as op

def test_combine_latest():
    sub1 = Subject()
    sub2 = Subject()
    interval(1.0).pipe(op.map(lambda i: f'sub1: {i}')).subscribe(sub1)
    interval(1.5).pipe(op.map(lambda i: f'sub2: {i}')).subscribe(sub2) 
    combine_latest(sub1, sub2).subscribe(lambda x: print(f'combined: {x}'))