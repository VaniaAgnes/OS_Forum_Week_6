import threading
import time
import random

LOWER_NUM = 1
UPPER_NUM = 10000
BUFFER_SIZE = 100
MAX_COUNT = 10000

# Bounded buffer (stack)
buffer = []
lock = threading.Lock()
condition = threading.Condition(lock)

# Flag to indicate whether the producer has finished producing
producer_done = False

# Producer thread
class Producer(threading.Thread):
    def run(self):
        global producer_done
        for _ in range(MAX_COUNT):
            number = random.randint(LOWER_NUM, UPPER_NUM)
            with condition:
                while len(buffer) >= BUFFER_SIZE:
                    condition.wait()
                buffer.append(number)
                with open("all.txt", "a") as f:
                    f.write(str(number) + "\n")
                condition.notify_all()
        producer_done = True

# Customer threads
class Customer(threading.Thread):
    def __init__(self, parity):
        super().__init__()
        self.parity = parity

    def run(self):
        while True:
            with condition:
                while not buffer or buffer[-1] % 2 != self.parity:
                    if producer_done and not buffer:
                        return
                    condition.wait()
                number = buffer.pop()
                filename = "even.txt" if self.parity == 0 else "odd.txt"
                with open(filename, "a") as f:
                    f.write(str(number) + "\n")
                condition.notify_all()

time_start = time.time()

# Create threads
thread_producer = Producer()
thread_even_customer = Customer(0)
thread_odd_customer = Customer(1)

# Start the threads
thread_producer.start()
thread_even_customer.start()
thread_odd_customer.start()

# Join the producer thread
thread_producer.join()

# Wait for consumers to finish processing remaining items
thread_even_customer.join()
thread_odd_customer.join()

time_end = time.time()

time_to_execute = time_end - time_start

print("The printing process is done with an execution time of:", time_to_execute,"sec")

