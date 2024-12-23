import numpy as np


class Statistics:

    def __init__(self):
        self.execution_times = []

    def print_stats(self):

        average_time = np.mean(self.execution_times)
        print(f"Average task execution time: {average_time:.9f} seconds.")

        min_time = np.min(self.execution_times)
        max_time = np.max(self.execution_times)
        print(f"Minimum execution time: {min_time:.9f} seconds.")
        print(f"Maximum execution time: {max_time:.9f} seconds.")

        print(f'Временной квант времени для выполнения задачи {10 / (1 * (10 ** 9)):.18f} секунд')




