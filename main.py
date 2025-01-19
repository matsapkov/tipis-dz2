import random # Для генерации случайных данных (размер задач и количество операций)
import csv # Для записи данных о выполнении задач в CSV-файл
import time # Для имитации задержек и расчета времени
from queue import Queue # Для реализации очереди задач
from pythonProject.stats.statistics import Statistics


stats = Statistics()
counter = 0

# Функция для инициализации лог-файлов системы и процессоров
def initialize_logs(processors_count):
    # Создает и очищает общий системный лог
    with open("SystemLOG.txt", "w", encoding="utf-8") as file:
        file.write("=== System Logs ===\n")
    # Создает и очищает лог-файлы для каждого процессора
    for processor_id in range(processors_count):
        with open(f"Processor-{processor_id}_log.txt", "w", encoding="utf-8") as file:
            file.write(f"=== Logs for Processor-{processor_id} ===\n")


# Функция для записи сообщений в лог конкретного процессора
def print_proc_logs(processor_name, log, cycle_time):
    # Конвертирует такты процессора в секунды
    time_in_seconds = cycle_time / Processor.clock_speed
    # Добавляет запись в файл процессора
    with open(f"{processor_name}_log.txt", "a", encoding="utf-8") as file:
        file.write(f"Time {time_in_seconds:.9f}s: {log}\n")


# Функция для записи сообщений в общий системный лог
def print_system_logs(log, cycle_time):
    # Конвертирует такты процессора в секунды
    time_in_seconds = cycle_time / Processor.clock_speed
    # Добавляет запись в системный лог
    with open("SystemLOG.txt", "a", encoding="utf-8") as file:
        file.write(f"Time {time_in_seconds:.9f}s: {log}\n")


# Логирует текущее состояние всех задач в памяти
def log_all_tasks_state(memory, cycle_time):
    # Формирует список состояния задач (имя задачи и статус)
    task_state = [(task.name, task.status) for task in memory.tasks]
    # Формирует сообщение о состоянии задач
    log_message = f"All Tasks State at Time {cycle_time / Processor.clock_speed:.9f}s: {task_state}"
    # Записывает в системный лог
    print_system_logs(log_message, cycle_time)


def get_user_config():
    # Настройки для каждого типа задачи
    config = {}

    print("Настройте параметры для каждого типа задачи.")

    # Настройка для типа Cycling
    config['Cycling'] = {
        'ttl': int(input("Введите TTL для задачи типа 'Cycling': ")),
        'tick_range': (int(input("Введите начальное количество тактов для 'Cycling': ")),
                      int(input("Введите конечное количество тактов для 'Cycling': "))),
        'size_range': (int(input("Введите начальный размер в битах для 'Cycling': ")),
                       int(input("Введите конечный размер в битах для 'Cycling': ")))
    }

    # Настройка для типа Periodic
    config['Periodic'] = {
        'ttl': int(input("Введите TTL для задачи типа 'Periodic': ")),
        'tick_range': (int(input("Введите начальное количество тактов для 'Periodic': ")),
                      int(input("Введите конечное количество тактов для 'Periodic': "))),
        'size_range': (int(input("Введите начальный размер в битах для 'Periodic': ")),
                       int(input("Введите конечный размер в битах для 'Periodic': ")))
    }

    # Настройка для типа Impulse
    config['Impulse'] = {
        'ttl': int(input("Введите TTL для задачи типа 'Impulse': ")),
        'tick_range': (int(input("Введите начальное количество тактов для 'Impulse': ")),
                      int(input("Введите конечное количество тактов для 'Impulse': "))),
        'size_range': (int(input("Введите начальный размер в битах для 'Impulse': ")),
                       int(input("Введите конечный размер в битах для 'Impulse': ")))
    }

    return config


# Класс, представляющий канал передачи данных
class DataChannel:
    speed = 100 * (10 ** 9) # Скорость передачи данных в битах/сек (100 Гбит/с)

    def __init__(self, memory):
        self.memory = memory # Память с задачами
        self.frames = [] # Список Ethernet-фреймов
        self.ethernet_frame_size = 12144 # Максимальный размер Ethernet-фрейма в битах
        self.min_ethernet_frame_size = 512 # Минимальный размер Ethernet-фрейма в битах
        self.headers_size = 144 # Размер заголовков Ethernet-фрейма

    # Распределяет задачи по Ethernet-фреймам
    def calculate_frames(self):
        frame = Frame() # Создает новый фрейм
        for task in self.memory.tasks:
            # Проверяет, влезает ли задача в текущий фрейм
            if task.size + frame.get_occupied_space() <= self.ethernet_frame_size - self.headers_size:
                frame.add_task(task) # Добавляет задачу в фрейм
            else:
                self.frames.append(frame)  # Заканчивает текущий фрейм
                frame = Frame() # Создает новый фрейм
                frame.add_task(task) # Добавляет задачу в новый фрейм
        self.frames.append(frame) # Добавляет последний фрейм в список
        print(f"Total Ethernet frames required: {len(self.frames)}")  # Выводит количество фреймов
        for frame in self.frames:
            print(frame)  # Печатает содержимое каждого фрейма
        return len(self.frames) # Возвращает общее количество фреймов

    # Передает данные (фреймы) через канал
    def transmit(self):
        total_frames = self.calculate_frames() # Рассчитывает фреймы
        transfer_time = 0 # Счетчик общего времени передачи
        for frame in self.frames:
            frame_size = frame.get_occupied_space()  # Получает размер фрейма
            transfer_time += frame_size/self.speed  # Добавляет время передачи текущего фрейма
        print(f"Total transfer time: {transfer_time} seconds.") # Печатает общее время передачи
        time.sleep(transfer_time) # Имитация времени передачи данных
        return self.frames  # Возвращает список фреймов


# Класс для Ethernet-фрейма, содержащего задачи
class Frame:
    def __init__(self):
        self.max_size = 12144 # Максимальный размер фрейма (бит)
        self.headers_size = 144  # Размер заголовков (бит)
        self.tasks = [] # Список задач в фрейме
        self.occupied_space = 0 # Занятое пространство в фрейме (бит)

    # Форматирует строковое представление фрейма
    def __str__(self):
        tasks_info = ", ".join([str(task) for task in self.tasks])
        return f"Frame with {len(self.tasks)} tasks (Occupied space: {self.occupied_space} bits): [{tasks_info}]"

    # Возвращает текущее занятое пространство в фрейме
    def get_occupied_space(self):
        return self.occupied_space

    # Возвращает полный размер фрейма (включая минимальный размер)
    def get_frame_size(self):
        if self.occupied_space + 144 < 512: # Если фрейм меньше минимального
            return 512 # Возвращает минимальный размер
        else:
            return self.occupied_space + 144 # Возвращает фактический размер

    # Добавляет задачу в фрейм
    def add_task(self, task):
        self.tasks.append(task) # Добавляет задачу в список задач
        self.occupied_space += task.size # Увеличивает занятое пространство фрейма


class Task:
    def __init__(self, name, task_type, ticks_to_complete, size, ttl):
        self.name = name # Уникальное имя задачи
        self.ticks_to_complete = ticks_to_complete # Время для завершения задачи в тактах
        self.size = 64 * size # Размер задачи в битах
        self.remaining_operations = self.ticks_to_complete # Остаток операций (изначально равен общему количеству)
        self.status = "In queue" # Начальный статус задачи
        self.start_time = None # Время начала выполнения задачи
        self.end_time = None # Время завершения задачи
        self.ttl = ttl
        self.task_type = task_type
        # Выводит информацию о созданной задаче
        print(f"Task {self.name} created with {self.ticks_to_complete} operations and size {self.size} bits.")

    # Метод для выполнения одного шага задачи
    def run(self):
        self.remaining_operations -= 1 # Уменьшает количество оставшихся тактов на 1
        self.ttl -= 1
        if self.remaining_operations <= 0: # Если операции закончилис
            self.remaining_operations = 0 # Устанавливает остаток операций в 0
        if self.ttl <= 0:
            self.ttl = 0
        return self.remaining_operations # Возвращает количество оставшихся операций

    # Форматирует строковое представление задачи
    def __str__(self):
        return f"Task {self.name} (Operations: {self.remaining_operations}/{self.ticks_to_complete}, Size: {self.size} bits, Status: {self.status})"


# Класс, реализующий алгоритм планирования Round Robin
class RoundRobin:
    def __init__(self, time_quantum, processors_count, config,num_tasks, num_cores):
        self.memory = Memory(config, num_tasks) # Инициализация памяти с задачами
        self.time_quantum = time_quantum  # Временной квант для алгоритма Round Robin
        # Получает очередь задач из канала передачи данных
        self.task_queue = self.get_tasks_from_data_channel(DataChannel(self.memory).transmit())
        self.processors = [] # Список процессоров
        self.completed_tasks = 0 # Количество завершенных задач
        self.total_tasks = len(self.memory.tasks) # Общее количество задач
        self.cycle_time = 0 # Время в тактах системы
        for i in range(processors_count):
            # Создает процессоры с заданным количеством ядер и добавляет их в список
            processor = Processor(name=f"Processor-{i}", num_cores=num_cores)
            self.processors.append(processor)

    @staticmethod
    def get_tasks_from_data_channel(data):
        # Метод для извлечения задач из списка фреймов
        frames = data # Список фреймов
        queue = Queue() # Создает очередь для задач
        for frame in frames:
            for task in frame.tasks:
                queue.put(task) # Добавляет каждую задачу из фреймов в очередь
        return queue # Возвращает очередь задач

    # Основной метод выполнения задач
    def execute(self):
        active_tasks = [] # Список активных задач, которые выполняются на ядрах
        while not self.task_queue.empty() or active_tasks:
            self.cycle_time += 1 # Увеличивает счетчик времени
            # log_all_tasks_state(self.memory, self.cycle_time) # Логирует состояние всех задач
            for processor in self.processors:
                for core in processor.cores:
                    # Если ядро свободно и очередь задач не пуста
                    if core.status is None and not self.task_queue.empty():
                        task = self.task_queue.get() # Извлекает задачу из очереди
                        task.status = "Working" # Устанавливает статус задачи "В работе"
                        core.assign_task(task, self.cycle_time) # Назначает задачу ядру
                        log_message = f"Task {task.name} assigned to Core {core.name}."
                        # print_proc_logs(processor.name, log_message, self.cycle_time)
                        # Логирует факт назначения задачи
                        active_tasks.append((processor, core))  # Добавляет пару (процессор, ядро) в активные задачи

            completed_cores = [] # Список завершивших выполнение ядер
            for processor, core in active_tasks:
                core.execute_task(self.time_quantum, processor.name, self.task_queue,
                                  self.completed_tasks, self.cycle_time)
                # Выполняет задачу на ядре
                if core.status is None: # Если ядро стало свободным
                    if core.current_task:
                        core.current_task.status = "Completed" # Меняет статус задачи на "Завершена"
                    completed_cores.append((processor, core)) # Добавляет ядро в список завершенных
            # Удаляет завершившие ядра из списка активных
            active_tasks = [t for t in active_tasks if t not in completed_cores]

            if self.task_queue.empty():
                # Если очередь задач пуста, логирует завершение работы
                # print_system_logs("All tasks completed. Ending execution.", self.cycle_time)
                print("All tasks completed. Ending execution.")
                for processor in self.processors:
                    print(f'Processor {processor.name} completed {processor.completed_tasks} in {self.cycle_time/processor.clock_speed} seconds')
                break


# Класс, представляющий процессор с несколькими ядрами
class Processor:
    clock_speed = 1 * (10 ** 9)  # Частота процессора в герцах (1 ГГц)

    def __init__(self, name, num_cores):
        self.name = name # Имя процессора
        # Создает список ядер с уникальными именами
        self.cores = [Core(name=f'Core-{i}') for i in range(num_cores)]
        self.completed_tasks = 0

    def increment_completed_tasks(self):
        self.completed_tasks += 1

    def __str__(self):
        return self.name  # Возвращает имя процессора как строку


# Класс, представляющий ядро процессора
class Core:
    def __init__(self, name):
        self.status = None # Статус ядра: None, если свободно
        self.name = name # Имя ядра
        self.current_task = None # Текущая задача, выполняемая на ядре
        self.start_time = None # Время начала выполнения задачи
        self.end_time = None # Время окончания выполнения задачи
        self.uncompleted_tasks = []

    # Выполняет задачу с учетом временного кванта
    def execute_task(self, time_quantum, processor_name, task_queue, completed_tasks, cycle_time):
        global counter
        if self.current_task:
            log_message = f"Core {self.name} is executing Task {self.current_task.name}. Remaining operations: {self.current_task.remaining_operations}."
            # print_proc_logs(processor_name, log_message, cycle_time) # Логирует выполнение задачи

            for _ in range(time_quantum):  # Выполняет задачу в рамках временного кванта
                if self.current_task.remaining_operations > 0 and self.current_task.ttl > 0:
                    self.current_task.run()  # Уменьшает оставшиеся операции задачи
                    self.current_task.ttl -= 1  # Уменьшает TTL
                    self.current_task.status = 'In work'  # Обновляет статус задачи

                if self.current_task.remaining_operations <= 0:
                    # Задача завершена
                    counter += 1
                    processor = next(p for p in round_robin.processors if p.name == processor_name)
                    processor.increment_completed_tasks()
                    self.end_time = cycle_time  # Фиксирует время окончания
                    self.current_task.status = 'Completed'  # Обновляет статус задачи
                    self.record_task_time(processor_name)  # Сохраняет статистику выполнения задачи
                    # log_message = f"Task {self.current_task.name} completed successfully on Core {self.name} of Processor {processor_name}."
                    # print_proc_logs(processor_name, log_message, cycle_time)
                    completed_tasks += 1  # Увеличивает счетчик завершенных задач
                    self.status = None  # Освобождает ядро
                    self.current_task = None
                    return

                if self.current_task.ttl <= 0:
                    # TTL задачи истек
                    self.current_task.status = "TTL Expired"
                    self.uncompleted_tasks.append(self.current_task)  # Добавляем задачу в список незавершенных
                    # log_message = f"Task {self.current_task.name} expired on Core {self.name} of Processor {processor_name}."
                    # print_proc_logs(processor_name, log_message, cycle_time)
                    self.status = None  # Освобождаем ядро
                    self.current_task = None
                    return

            # Если задача не завершена за временной квант
            if self.current_task and self.current_task.remaining_operations > 0:
                task_queue.put(self.current_task)  # Возвращаем задачу в очередь
                self.current_task.status = "In queue"  # Обновляем статус задачи
                self.status = None  # Освобождаем ядро
                self.current_task = None

    # Назначает задачу ядру
    def assign_task(self, task, cycle_time):
        if self.status is None: # Если ядро свободно
            if task.start_time is None:
                task.start_time = cycle_time # Фиксирует время начала выполнения задачи
            self.current_task = task # Привязывает задачу к ядру
            self.status = task # Обновляет статус ядра
            self.current_task.status = "In work" # Изменяет статус задачи
            return True
        return False # Возвращает False, если ядро занято

    # Записывает информацию о времени выполнения задачи в CSV-файл
    def record_task_time(self, processor_name):
        start_time_in_seconds = self.current_task.start_time / Processor.clock_speed
        end_time_in_seconds = self.end_time / Processor.clock_speed
        execution_time_in_seconds = (self.end_time - self.current_task.start_time) / Processor.clock_speed
        stats.execution_times.append(execution_time_in_seconds)

        with open('task_times.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                self.current_task.name,  # Имя задачи
                f"{start_time_in_seconds:.9f}", # Время начала выполнения в секундах
                f"{end_time_in_seconds:.9f}",  # Время окончания выполнения в секундах
                f"{execution_time_in_seconds:.9f}", # Общее время выполнения в секундах
                processor_name, # Имя процессора
                self.name # Имя ядра
            ])


# Класс памяти, содержащий задачи
class Memory:
    def __init__(self, config, num_tasks):
        self.tasks = []
        for i in range(num_tasks):
            task_name = i
            task = self.generate_task(config, task_name)
            self.tasks.append(task)

    @staticmethod
    def generate_task(config, name):
        task_type = random.choice(list((config.keys())))
        task_config = config[task_type]
        # Генерация случайных значений для задачи
        ticks_to_complete = random.randint(task_config['tick_range'][0], task_config['tick_range'][1])
        size = random.randint(task_config['size_range'][0], task_config['size_range'][1])
        ttl = task_config['ttl']
        # Создаем задачу
        return Task(name, task_type, ticks_to_complete, size, ttl)


# Основной блок программы
if __name__ == '__main__':
    # Инициализирует CSV-файл для записи статистики
    with open('task_times.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Имя задачи", # Название столбца для имени задачи
            "Время начала выполнения задачи",  # Название столбца для времени начала
            "Время конца выполнения задачи", # Название столбца для времени окончания
            "Общее время выполнения", # Название столбца для общего времени выполнения
            "Имя процессора",  # Название столбца для имени процессора
            "Имя ядра" # Название столбца для имени ядра
        ])

    time_quantum = int(input('Пожалуйста, введите временной квант для планировщика RoundRobin:'))
    processors_count = int(input('Пожалуйста, введите количество процессоров, участвующих в эксперименте(max=12):'))
    # Создает файлы логов для процессоров
    initialize_logs(processors_count=4)
    user_config = get_user_config()
    num_tasks = int(input('Введите количество задач для симуляции:'))
    # Создает экземпляр класса RoundRobin с двумя процессорами и двумя ядрами в каждом
    round_robin = RoundRobin(time_quantum, processors_count, user_config, num_tasks, num_cores=8)
    # Запускает выполнение задач с использованием Round Robin
    round_robin.execute()
    print(counter)
    # print(stats.execution_times)
    stats.print_stats()
    for processor in round_robin.processors:
        for core in processor.cores:
            print(f'Процессор {processor.name}, ядро {core.name}. Количество невыполненных задач на ядре из-за истекшего TTL: {len(core.uncompleted_tasks)}')
