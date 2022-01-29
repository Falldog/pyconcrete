from threading import Thread

try:
    from queue import Queue
except:  # noqa: E722
    from Queue import Queue


def main():
    # global Queue, Thread, sqrt
    q = Queue()
    worker = []

    for i in range(5):
        t = Thread(target=sqrt, args=(q, i))
        t.start()
        worker.append(t)

    for w in worker:
        w.join()

    while not q.empty():
        print(q.get())


def sqrt(q, n):
    q.put(n * n)


if __name__ == '__main__':
    main()
