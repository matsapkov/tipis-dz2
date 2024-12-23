import numpy as np

completed_tasks = [12496, 12496, 12496, 12496, 12504, 12504, 12504, 12504]

mean = np.mean(completed_tasks)

variance = np.var(completed_tasks)
std_deviation = np.std(completed_tasks)

print("Количество выполненных задач:")
print(completed_tasks)

print("\nВычисленные статистики:")
print(f"Среднее значение: {mean}")
print(f"Дисперсия: {variance}")
print(f"Стандартное отклонение: {std_deviation}")
