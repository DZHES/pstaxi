import datetime
from threading import Thread

from django.views.generic import TemplateView

from motorpool.models import Brand


def cpu_bound(iterations):
    for x in range(iterations):
        result = x ** 2


def io_bound(iterations):
    for x in range(iterations):
        result = Brand.objects.filter(id=1).first()


class WorkerThread(Thread):
    def __init__(self, target, args):
        super().__init__(target=target, args=args)
        self.total_time = 0
        self.iterations = args[0]

    def run(self):
        start = datetime.datetime.now()
        super().run()
        end = datetime.datetime.now()
        self.total_time = (end - start).total_seconds()

    def join(self, timeout=None):
        super().join(timeout)
        return self.total_time, self.iterations


class ThreadView(TemplateView):
    template_name = 'main/test_thread.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.test(context, 'cpu', cpu_bound, 20000000)
        self.test(context, 'io', io_bound, 200)

        return context

    @staticmethod
    def test(context, test_type, worker, iterations):
        # Обычный запуск - последовательное выполнение
        start = datetime.datetime.now()
        worker(iterations)
        end = datetime.datetime.now()
        context[f'{test_type}_synchronous_time'] = (end - start).total_seconds()
        context[f'{test_type}_iterations'] = iterations

        # Многопоточный запуск - параллельное выполнение в 4 потока
        threads_list = []
        for i in range(4):
            # Каждый поток выполняет 1/4 часть от общего количества итераций
            th = WorkerThread(target=worker, args=(int(iterations / 4),))
            th.start()
            threads_list.append(th)

        # Получаем результаты выполнения потоков
        threads_results = []
        thread_number = 1
        for thread in threads_list:
            result = thread.join()
            threads_results.append({
                'id': f'Поток {thread_number}',
                'time': result[0],
                'iterations': result[1]
            })
            thread_number += 1

        context[f'{test_type}_threads_results'] = threads_results