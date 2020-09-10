class Touch:
    __slots__ = ('grab_current', 'grab_list', )
    def __init__(self):
        self.grab_current = None
        self.grab_list = []
    def grab(self, w):
        self.grab_list.append(w)
    def ungrab(self, w):
        if w in self.grab_list:
            self.grab_list.remove(w)


def simulate_touch(n_touch_moves):
    from kivy.uix.widget import Widget
    import asynckivy as ak

    async def _test(w, t):
        async for __ in ak.rest_of_touch_moves(w, t):
            pass
        nonlocal done;done = True
        
    done = False
    w = Widget()
    t = Touch()
    ak.start(_test(w, t))
    for __ in range(n_touch_moves):
        t.grab_current = None
        w.dispatch('on_touch_move', t)
        t.grab_current = w
        w.dispatch('on_touch_move', t)
    t.grab_current = None
    w.dispatch('on_touch_up', t)
    t.grab_current = w
    w.dispatch('on_touch_up', t)
    assert done


from timeit import timeit
import asynckivy as ak

for n_touch_moves in (0, 0, 1, 60, 120, 300):
    print('{: 4}:'.format(n_touch_moves), timeit(lambda: simulate_touch(n_touch_moves), number=100))
