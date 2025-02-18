import multiprocessing


def task_fn(arr):
    for i in arr:
        print(i**2)


if __name__ == '__main__':
    args = range(5)
    ctx = multiprocessing.get_context('fork')
    p = ctx.Process(target=task_fn, args=(args,))
    p.start()
    p.join()
    p.close()
