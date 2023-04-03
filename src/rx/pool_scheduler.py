import multiprocessing
from typing import Callable
from rx.scheduler import ThreadPoolScheduler
from rx import operators as ops
from rx.core import Observable

# calculate number of CPUs, then create a ThreadPoolScheduler with that number of threads
optimal_thread_count = multiprocessing.cpu_count()
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

def new_subscribe_on_pool_scheduler() -> Callable[[Observable], Observable]:
    """
    From: ops.observe_on documentation
    Subscribe on the specified scheduler.

    Wrap the source sequence in order to run its subscription and
    unsubscription logic on the specified scheduler. This operation is
    not commonly used; see the remarks section for more information on
    the distinction between subscribe_on and observe_on.

    This only performs the side-effects of subscription and
    unsubscription on the specified scheduler. In order to invoke
    observer callbacks on a scheduler, use observe_on.
    """
    return ops.subscribe_on(pool_scheduler)

def new_observe_on_pool_scheduler() -> Callable[[Observable], Observable]:
    """
    From: ops.observe_on documentation
    Wraps the source sequence in order to run its observer callbacks
    on the specified scheduler.

    Args:
        scheduler: Scheduler to notify observers on.

    This only invokes observer callbacks on a scheduler. In case the
    subscription and/or unsubscription actions have side-effects
    that require to be run on a scheduler, use subscribe_on.

    Returns:
        An operator function that takes an observable source and
        returns the source sequence whose observations happen on the
        specified scheduler.
    """
    return ops.observe_on(pool_scheduler)