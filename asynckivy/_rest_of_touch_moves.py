__all__ = ('rest_of_touch_moves', )

from asynckivy._core_utils import get_my_own_agen


@get_my_own_agen
async def rest_of_touch_moves(widget, touch, *, eat_touch=False, get_my_own_agen):
    '''Returns an async-generator, which yields the touch when `on_touch_move`
    is fired, and ends when `on_touch_up` is fired. Grabs and ungrabs the
    touch automatically. If `eat_touch` is True, the touch will never be
    dispatched further.
    '''
    import asynckivy as ak
    from asynckivy._core import _get_step_coro, sleep_forever
    step_coro = await _get_step_coro()
    my_own_agen = get_my_own_agen()

    if eat_touch:
        def _on_touch_up(w, t):
            if t is touch:
                if t.grab_current is w:
                    t.ungrab(w)
                    ak.start(my_own_agen.aclose())
                    step_coro()
                return True
        def _on_touch_move(w, t):
            if t is touch:
                if t.grab_current is w:
                    step_coro()
                return True
    else:
        def _on_touch_up(w, t):
            if t.grab_current is w and t is touch:
                t.ungrab(w)
                ak.start(my_own_agen.aclose())
                step_coro()
                return True
        def _on_touch_move(w, t):
            if t.grab_current is w and t is touch:
                step_coro()
                return True

    touch.grab(widget)
    uid_up = widget.fbind('on_touch_up', _on_touch_up)
    uid_move = widget.fbind('on_touch_move', _on_touch_move)
    assert uid_up
    assert uid_move

    try:
        while True:
            await sleep_forever()
            yield touch
    finally:
        touch.ungrab(widget)
        widget.unbind_uid('on_touch_up', uid_up)
        widget.unbind_uid('on_touch_move', uid_move)


all_touch_moves = rest_of_touch_moves  # will be removed in the future
