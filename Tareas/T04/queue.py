from collections import deque
from abc import abstractmethod


class Queue:
    def __init__(self, max_length):
        self.max_length = max_length
        self.queue = deque()

    def enter(self, item):
        if self.length >= self.max_length:
            pass

    def leave_early(self, item):
        self.queue.remove(item)

    @property
    def length(self):
        return len(self.queue)

    @abstractmethod
    def on_exit(self):
        pass

    
