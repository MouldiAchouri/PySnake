import random
from config.constants import *

class Apple:
    def __init__(self):
        self.position = [0, 0]

    def spawn(self, snake_segments):
        while True:
            self.position = [
                random.randrange(0, WIDTH, CELL_SIZE),
                random.randrange(0, HEIGHT, CELL_SIZE)
            ]
            if self.position not in snake_segments:
                break