from config.constants import *

class Snake:
    def __init__(self):
        self.segments = []
        self.direction = RIGHT
        self.score = 0

        self.reset()

    def reset(self):
        x = (WIDTH // 2 // CELL_SIZE) * CELL_SIZE
        y = (HEIGHT // 2 // CELL_SIZE) * CELL_SIZE
        self.segments = [[x, y], [x - CELL_SIZE, y]]
        self.direction = RIGHT
        self.score = 0

    def get_next_head_position(self):
        head_x, head_y = self.segments[0]
        if self.direction == UP: head_y -= CELL_SIZE
        elif self.direction == DOWN: head_y += CELL_SIZE
        elif self.direction == LEFT: head_x -= CELL_SIZE
        elif self.direction == RIGHT: head_x += CELL_SIZE
        return [head_x, head_y]

    def move(self, new_head, growing=False):
        self.segments.insert(0, new_head)
        if not growing:
            self.segments.pop()
        else:
            self.score += 1

    def check_collision(self, head):
        x, y = head
        return x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT or head in self.segments