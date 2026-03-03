from config.constants import *

class Render:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 24, bold=True)

    def draw(self, snake, apple):
        self.screen.fill(COLOR_BG)
        self._draw_grid()
        self._draw_apple(apple)
        self._draw_snake(snake)
        self._draw_score(snake.score)
        pygame.display.flip()

    def _draw_grid(self):
        for y in range(0, HEIGHT, CELL_SIZE):
            for x in range(0, WIDTH, CELL_SIZE):
                if (x // CELL_SIZE + y // CELL_SIZE) % 2 == 0:
                    pygame.draw.rect(self.screen, COLOR_GRID, (x, y, CELL_SIZE, CELL_SIZE))

    def _draw_apple(self, apple):
        pos = apple.position
        pygame.draw.rect(self.screen, COLOR_APPLE, (pos[0] + 2, pos[1] + 2, CELL_SIZE - 4, CELL_SIZE - 4))

    def _draw_snake(self, snake):
        for i, seg in enumerate(snake.segments):
            color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
            pygame.draw.rect(self.screen, color, (seg[0] + 1, seg[1] + 1, CELL_SIZE - 2, CELL_SIZE - 2))

    def _draw_score(self, score):
        text = self.font.render(f"Score: {score}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))