import matplotlib
matplotlib.use('TkAgg')  # Устанавливаем бэкенд до импорта pyplot

import matplotlib.pyplot as plt
import numpy as np


def plot_task_counts(processors):
    """
    Печатает гистограмму количества задач, выполненных процессорами.

    :param processors: Список названий процессоров.
    :param task_counts: Список, где каждый элемент соответствует количеству задач, выполненных соответствующим процессором.
    """
    task_counts = []
    processors_names = []
    for processor in processors:
        task_counts.append(processor.completed_tasks)
        processors_names.append(processor.name)
    plt.figure(figsize=(10, 6))
    plt.bar(processors_names, task_counts, color='skyblue')
    plt.xlabel('Процессор')
    plt.ylabel('Количество задач')
    plt.title('Гистограмма количества задач, выполненных процессорами')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_task_type_counts(processors):
    """
    Печатает гистограмму количества задач каждого типа, выполненных каждым процессором.

    :param processors: Список названий процессоров.
    :param task_types: Список типов задач.
    :param task_counts: Двумерный список, где каждая строка соответствует процессору,
                         а каждый столбец — количеству задач конкретного типа, выполненных этим процессором.
    """
    task_types = ['cycling', 'periodic', 'impulse']
    processors_names = []
    for processor in processors:
        for task in processor.completed_tasks_for_diagram:
            if task.task_type == 'Cycling':
                processor.cycling_tasks.append(task)
            elif task.task_type == 'Periodic':
                processor.periodic_tasks.append(task)
            elif task.task_type == 'Impulse':
                processor.impulse_tasks.append(task)
    task_counts = [[len(processor.cycling_tasks), len(processor.periodic_tasks), len(processor.impulse_tasks)] for processor in processors]

    for processor in processors:
        processors_names.append(processor.name)

    x = np.arange(len(processors))  # Место для процессоров на оси X
    width = 0.15  # Ширина каждого столбца на гистограмме
    fig, ax = plt.subplots(figsize=(12, 8))

    task_counts = np.array(task_counts)
    # print(task_counts)
    # Создаем бар для каждого типа задач
    for i, task_type in enumerate(task_types):
        ax.bar(x + i * width, task_counts[:, i], width, label=task_type)

    ax.set_xlabel('Процессор')
    ax.set_ylabel('Количество задач')
    ax.set_title('Гистограмма количества задач каждого типа, выполненных каждым процессором')
    ax.set_xticks(x + width * (len(task_types) - 1) / 2)
    ax.set_xticklabels(processors_names, rotation=45)
    ax.legend(title='Типы задач', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()


def plot_ethernet_frame_load(ethernet_frames):
    """
    Печатает гистограмму загруженности Ethernet фреймов.

    :param ethernet_frames: Список названий Ethernet фреймов.
    :param load_percentages: Список с процентами загрузки для каждого Ethernet фрейма.
    """
    load_percentages = []
    for frame in ethernet_frames:
        load_percentages.append(frame.frame_fill_percentage)
    plt.figure(figsize=(10, 6))
    indices = []
    for i in range(len(ethernet_frames)):
        indices.append(i)
    plt.bar(indices, load_percentages, color='lightcoral')
    plt.xlabel('Ethernet фрейм')
    plt.ylabel('Загруженность (%)')
    plt.title('Гистограмма загруженности Ethernet фреймов')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
