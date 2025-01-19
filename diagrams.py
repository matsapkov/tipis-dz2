import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np


def plot_task_counts(processors):
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


def plot_task_distribution_by_cores(processors):
    """
    Построить гистограммы распределения задач по ядрам для каждого процессора.

    :param processors: Список процессоров. У каждого процессора есть ядра и выполненные задачи.
    """
    task_types = ['Cycling', 'Periodic', 'Impulse']

    for processor in processors:
        # Собираем данные для каждого ядра
        core_names = [core.name for core in processor.cores]
        core_task_counts = []  # Массив количества задач для каждого ядра
        cycling_count = 0
        impulse_count = 0
        periodic_count = 0
        for core in processor.cores:
            for task in core.completed_task_for_diagram:
                if task.task_type == 'Cycling':
                    cycling_count += 1
                if task.task_type == 'Periodic':
                    periodic_count += 1
                if task.task_type == 'Impulse':
                    impulse_count += 1

            core_task_counts.append([cycling_count, periodic_count, impulse_count])

        core_task_counts = np.array(core_task_counts)  # Преобразуем в массив для удобства

        # Построение гистограммы для данного процессора
        x = np.arange(len(core_names))  # Индексы для ядер
        width = 0.2  # Ширина столбцов

        fig, ax = plt.subplots(figsize=(12, 6))
        for i, task_type in enumerate(task_types):
            ax.bar(x + i * width, core_task_counts[:, i], width, label=task_type)

        ax.set_xlabel('Ядра')
        ax.set_ylabel('Количество задач')
        ax.set_title(f'Распределение задач по ядрам процессора {processor.name}')
        ax.set_xticks(x + width * (len(task_types) - 1) / 2)
        ax.set_xticklabels(core_names, rotation=45)
        ax.legend(title='Типы задач')
        plt.tight_layout()
        plt.show()
