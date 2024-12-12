import random
import csv
import time
from queue import Queue


def initialize_logs(processors_count):
    with open("SystemLOG.txt", "w", encoding="utf-8") as file:
        file.write("=== System Logs ===\n")
    for processor_id in range(processors_count):
        with open(f"Processor-{processor_id}_log.txt", "w", encoding="utf-8") as file:
            file.write(f"=== Logs for Processor-{processor_id} ===\n")


def print_proc_logs(processor_name, log, cycle_time):
    time_in_seconds = cycle_time / Processor.clock_speed
    with open(f"{processor_name}_log.txt", "a", encoding="utf-8") as file:
        file.write(f"Time {time_in_seconds:.9f}s: {log}\n")


def print_system_logs(log, cycle_time):
    time_in_seconds = cycle_time / Processor.clock_speed
    with open("SystemLOG.txt", "a", encoding="utf-8") as file:
        file.write(f"Time {time_in_seconds:.9f}s: {log}\n")


def log_all_tasks_state(memory, cycle_time):
    task_state = [(task.name, task.status) for task in memory.tasks]
    log_message = f"All Tasks State at Time {cycle_time / Processor.clock_speed:.9f}s: {task_state}"
    print_system_logs(log_message, cycle_time)


class DataChannel:
    speed = 100 * (10 ** 9)

    def __init__(self, memory):
        self.memory = memory
        self.frames = []
        self.ethernet_frame_size = 512
        self.headers_size = 144

    def calculate_frames(self):
        frame = Frame()
        for task in self.memory.tasks:
            if task.size + frame.get_occupied_space() <= self.ethernet_frame_size - self.headers_size:
                frame.add_task(task)
            else:
                frame = Frame()
                self.frames.append(frame)
                frame.add_task(task)
        self.frames.append(frame)
        print(f"Total Ethernet frames required: {len(self.frames)}")
        for frame in self.frames:
            print(frame)
        return len(self.frames)

    def transmit(self):
        total_frames = self.calculate_frames()
        transfer_time = total_frames * (512 / self.speed)
        print(f"Total transfer time: {transfer_time} seconds.")
        time.sleep(transfer_time)
        return self.frames


class Frame:
    def __init__(self):
        self.min_size = 512
        self.headers_size = 144
        self.tasks = []
        self.occupied_space = 0

    def __str__(self):
        tasks_info = ", ".join([str(task) for task in self.tasks])
        return f"Frame with {len(self.tasks)} tasks (Occupied space: {self.occupied_space} bits): [{tasks_info}]"

    def get_occupied_space(self):
        return self.occupied_space

    def add_task(self, task):
        self.tasks.append(task)
        self.occupied_space += task.size


class Task:
    def __init__(self, name):
        self.name = name
        self.ticks_to_complete = random.randint(1000, 10000)
        self.size = random.randint(1, 128)
        self.remaining_operations = self.ticks_to_complete
        self.status = "In queue"
        self.start_time = None
        self.end_time = None
        print(f"Task {self.name} created with {self.ticks_to_complete} operations and size {self.size} bits.")

    def run(self):
        self.remaining_operations -= 1
        if self.remaining_operations <= 0:
            self.remaining_operations = 0
        return self.remaining_operations

    def __str__(self):
        return f"Task {self.name} (Operations: {self.remaining_operations}/{self.ticks_to_complete}, Size: {self.size} bits, Status: {self.status})"


class RoundRobin:
    def __init__(self, time_quantum, processors_count, num_cores):
        self.memory = Memory()
        self.time_quantum = time_quantum
        self.task_queue = self.get_tasks_from_data_channel(DataChannel(self.memory).transmit())
        self.processors = []
        self.completed_tasks = 0
        self.total_tasks = len(self.memory.tasks)
        self.cycle_time = 0
        for i in range(processors_count):
            processor = Processor(name=f"Processor-{i}", num_cores=num_cores)
            self.processors.append(processor)

    @staticmethod
    def get_tasks_from_data_channel(data):
        frames = data
        queue = Queue()
        for frame in frames:
            for task in frame.tasks:
                queue.put(task)
        return queue

    def execute(self):
        active_tasks = []
        while not self.task_queue.empty() or active_tasks:
            self.cycle_time += 1
            log_all_tasks_state(self.memory, self.cycle_time)
            for processor in self.processors:
                for core in processor.cores:
                    if core.status is None and not self.task_queue.empty():
                        task = self.task_queue.get()
                        task.status = "Working"
                        core.assign_task(task, self.cycle_time)
                        log_message = f"Task {task.name} assigned to Core {core.name}."
                        print_proc_logs(processor.name, log_message, self.cycle_time)
                        active_tasks.append((processor, core))

            completed_cores = []
            for processor, core in active_tasks:
                core.execute_task(self.time_quantum, processor.name, self.task_queue,
                                  self.completed_tasks, self.cycle_time)
                if core.status is None:
                    if core.current_task:
                        core.current_task.status = "Completed"
                    completed_cores.append((processor, core))

            active_tasks = [t for t in active_tasks if t not in completed_cores]

            if self.task_queue.empty():
                print_system_logs("All tasks completed. Ending execution.", self.cycle_time)
                print("All tasks completed. Ending execution.")
                break


class Processor:
    clock_speed = 2.5 * (10 ** 9)  # 2.5 GHz clock speed

    def __init__(self, name, num_cores):
        self.name = name
        self.cores = [Core(name=f'Core-{i}') for i in range(num_cores)]

    def __str__(self):
        return self.name


class Core:
    def __init__(self, name):
        self.status = None
        self.name = name
        self.current_task = None
        self.start_time = None
        self.end_time = None

    def execute_task(self, time_quantum, processor_name, task_queue, completed_tasks, cycle_time):
        if self.current_task:
            log_message = f"Core {self.name} is executing Task {self.current_task.name}. Remaining operations: {self.current_task.remaining_operations}."
            print_proc_logs(processor_name, log_message, cycle_time)
            for _ in range(time_quantum):
                self.current_task.run()
                self.current_task.status = 'In work'
                if self.current_task.remaining_operations <= 0:
                    self.end_time = cycle_time
                    self.current_task.status = 'Completed'
                    self.record_task_time()
                    log_message = f"Task {self.current_task.name} completed successfully on Core {self.name} of Processor {processor_name}."
                    print_proc_logs(processor_name, log_message, cycle_time)
                    completed_tasks += 1
                    self.status = None
                    self.current_task = None
                    return
            if self.current_task.remaining_operations > 0:
                log_message = f"Task {self.current_task.name} did not complete on Core {self.name} of Processor {processor_name}. Requeuing."
                print_proc_logs(processor_name, log_message, cycle_time)
                task_queue.put(self.current_task)
                self.current_task.status = "In queue"
                self.status = None
                self.current_task = None

    def assign_task(self, task, cycle_time):
        if self.status is None:
            if task.start_time is None:
                task.start_time = cycle_time
            self.current_task = task
            self.status = task
            self.current_task.status = "In work"
            return True
        return False

    def record_task_time(self):
        start_time_in_seconds = self.current_task.start_time / Processor.clock_speed
        end_time_in_seconds = self.end_time / Processor.clock_speed
        execution_time_in_seconds = (
                                                self.end_time - self.current_task.start_time) / Processor.clock_speed

        with open('task_times.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([self.current_task.name, f"{start_time_in_seconds:.9f}", f"{end_time_in_seconds:.9f}",
                             f"{execution_time_in_seconds:.9f}"])


class Memory:
    def __init__(self):
        self.tasks = [Task(name=i) for i in range(6)]


if __name__ == '__main__':
    with open('task_times.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Имя задачи", "Время начала выполнения задачи", "Время конца выполнения задачи", "Общее время выполнения"])

    initialize_logs(processors_count=2)
    round_robin = RoundRobin(time_quantum=10, processors_count=2, num_cores=2)
    round_robin.execute()
