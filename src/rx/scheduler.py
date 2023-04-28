import multiprocessing
from typing import Callable
from rx.scheduler import ThreadPoolScheduler, CurrentThreadScheduler # type: ignore
from rx import operators as ops
from rx.core import Observable # type: ignore
from src.util import get_settings

# calculate number of CPUs, then create a ThreadPoolScheduler with that number of threads
optimal_thread_count = multiprocessing.cpu_count()
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)
current_thread_scheduler = CurrentThreadScheduler()
settings = get_settings('app')
use_thread_pool = settings['use_thread_pool']

def observe_on_scheduler() -> Callable[[Observable], Observable]:
    if use_thread_pool:
        return ops.observe_on(pool_scheduler)
    else:
        return ops.observe_on(current_thread_scheduler)