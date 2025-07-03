from threading import Thread

threads = []


def clean_up() -> int:
    global threads
    old_len = len(threads)
    threads = list(filter(lambda thread: thread.is_alive(), threads))
    new_len = len(threads)
    for i, thread in threads:
        if thread.is_alive():
            # still doing it's shit
            continue
    return old_len - new_len


def send_thread(target, args=None, kwargs=None):
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}

    t = Thread(target=target, args=args, kwargs=kwargs)
    t.start()
    global threads
    threads.append(t)
