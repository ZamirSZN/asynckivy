'''The entire module is experimental'''

__all__ = ('run_awaitable', 'callable_to_asyncfn', )
import warnings
from inspect import iscoroutinefunction, isawaitable
from functools import wraps
import trio
import asynckivy
from asynckivy.exceptions import CancelledError


async def _ak_awaitable_wrapper(
        outcome:dict, end_signal:trio.Event, ak_awaitable):
    try:
        outcome['return_value'] = await ak_awaitable
    except GeneratorExit:
        outcome['cancelled'] = True
        raise
    except Exception as e:
        outcome['exception'] = e
    finally:
        end_signal.set()


async def run_awaitable(
        ak_awaitable, *, task_status=trio.TASK_STATUS_IGNORED):
    '''(experimental)
    Run an asynckivy-flavored awaitable under Trio.
    
    Usage #1:
        nursery.start_soon(run_awaitable, an_asynckivy_awaitable)

    Usage #2:
        return_value = await run_awaitable(an_asynckivy_awaitable)
    '''
    end_signal = trio.Event()
    try:
        outcome = {}
        wrapper_coro = _ak_awaitable_wrapper(
            outcome, end_signal, ak_awaitable, )
        asynckivy.start(wrapper_coro)
        task_status.started(wrapper_coro)
        await end_signal.wait()
        exception = outcome.get('exception', None)
        if exception is not None:
            raise exception
        if outcome.get('cancelled', False):
            raise CancelledError("Inner task was cancelled")
        return outcome['return_value']
    finally:
        wrapper_coro.close()


def callable_to_asyncfn(ak_callable):
    '''(experimental)
    Convert a callable that returns a asynckivy-flavored awaitable to
    a Trio-flavored async function.

    Usage:
        a_trio_asyncfn = callable_to_asyncfn(an_asynckivy_asyncfn)
    '''
    if not callable(ak_callable):
        raise ValueError(f"{ak_callable} is not callable")
    async def trio_asyncfn(*args, **kwargs):
        task_status = kwargs.pop('task_status', trio.TASK_STATUS_IGNORED)
        return await run_awaitable(
            ak_callable(*args, **kwargs), task_status=task_status, )
    return trio_asyncfn
