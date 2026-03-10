import sys
from config.constants import *
from game import Snake, Apple, Render, Menu


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        self.snake = Snake()
        self.apple = Apple()
        self.apple.spawn(self.snake.segments)
        self.menu = Menu()
        self.render = Render(self.screen)

        self.direction_lock = False
        self.move_delay = 150
        self.last_move = pygame.time.get_ticks()


    def run(self):
        while True:
            self._handle_events()
            self._update()
            self.render.draw(self.snake, self.apple)
            if self.menu.active:
                self.render.draw_menu(self.menu)
            pygame.display.flip()
            self.clock.tick(FPS)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == MENU_TOGGLE:
                    if not self.menu.active:
                        self.menu.pause()
                    else:
                        result= self.menu.handle_input(event)
                        if result == "RESET":
                            self.reset_game()
                        elif result == "TOGGLE_FS":
                            self._toggle_fullscreen()

                elif self.menu.active:
                    result = self.menu.handle_input(event)
                    if result == "RESET":
                        self.reset_game()
                    elif result == "TOGGLE_FS":
                        self._toggle_fullscreen()

                elif not self.direction_lock:
                    self._change_direction(event.key)

    def _change_direction(self, key):
        if key == UP and self.snake.direction != DOWN:
            self.snake.direction = UP
            self.direction_lock = True
        elif key == DOWN and self.snake.direction != UP:
            self.snake.direction = DOWN
            self.direction_lock = True
        elif key == LEFT and self.snake.direction != RIGHT:
            self.snake.direction = LEFT
            self.direction_lock = True
        elif key == RIGHT and self.snake.direction != LEFT:
            self.snake.direction = RIGHT
            self.direction_lock = True

    def _update(self):
        self.menu.update()

        if self.menu.active:
            return

        now = pygame.time.get_ticks()
        if now - self.last_move > self.move_delay:
            self.direction_lock = False

            new_head = self.snake.get_next_head_position()

            if self.snake.check_collision(new_head):
                self.snake.reset()
                self.move_delay = 150

            elif new_head == self.apple.position:
                self.snake.move(new_head, growing=True)
                self.apple.spawn(self.snake.segments)
                self.move_delay = max(90, self.move_delay - 3)

            else:
                self.snake.move(new_head, growing=False)

            self.last_move = now

    def reset_game(self):
        self.snake.reset()
        self.apple.spawn(self.snake.segments)
        self.move_delay = 150
        self.menu.active = False
        self.menu.countdown = False

    def _toggle_fullscreen(self):
        is_full = self.screen.get_flags() & pygame.FULLSCREEN

        if not is_full:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((WIDTH, HEIGHT))
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE)

        self.render.screen = self.screen
        pygame.event.clear()