import multiprocessing
import platform


def task_fn(arr):
    for i in arr:
        print(i**2)


if __name__ == '__main__':
    args = range(5)
    context = 'spawn' if platform.system() == "Windows" else 'fork'
    ctx = multiprocessing.get_context(context)
    p = ctx.Process(target=task_fn, args=(args,))
    p.start()
    p.join()
    p.close()
