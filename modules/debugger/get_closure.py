import gc, inspect

def get_closure(frame):
    code = frame.f_code

    for ob in gc.get_referrers(code):
        if inspect.isfunction(ob):
            func = ob
            break
    else:
        return {}

    if hasattr(func, '__closure__'):
        closure = func.__closure__
    else:
        closure = func.func_closure

    if closure is None:
        return {}

    return dict(zip(code.co_freevars, (c.cell_contents for c in closure)))