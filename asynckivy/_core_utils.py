import inspect
import functools


def get_my_own_agen(async_gen_func):
    assert inspect.isasyncgenfunction(async_gen_func)
    @functools.wraps(async_gen_func)
    def wrapper(*args, **kwargs):
        agen = async_gen_func(*args, get_my_own_agen=lambda: agen, **kwargs)
        assert inspect.isasyncgen(agen)
        return agen
    return wrapper
