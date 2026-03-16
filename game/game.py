import sys
from config.constants import *
from game import Snake, Apple, Menu
from view.render import Render
from view.state_render import StateRender


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

        self.state_render = StateRender(
            self.screen,
            self.render.font_bold,
            self.render.font_standard
        )

        self.state = STATE_PLAYING
        self.direction_lock = False
        self.move_delay = 150
        self.last_move = pygame.time.get_ticks()

    def run(self):
        while True:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if self.state in [STATE_LOSE, STATE_WIN]:
                    if event.key in [MENU_UP, pygame.K_UP]:
                        self.state_render.selected_index = (self.state_render.selected_index - 1) % len(
                            self.state_render.options)
                    elif event.key in [MENU_DOWN, pygame.K_DOWN]:
                        self.state_render.selected_index = (self.state_render.selected_index + 1) % len(
                            self.state_render.options)
                    elif event.key == MENU_TOGGLE:
                        if self.state_render.selected_index == 0:
                            self.reset_game()
                        else:
                            pygame.quit()
                            sys.exit()
                    return

                if self.menu.active:
                    if event.key == MENU_TOGGLE:
                        result = self.menu.handle_input(event)
                        if result == "RESET": self.reset_game()
                        elif result == "TOGGLE_FS": self._toggle_fullscreen()
                    else:
                        result = self.menu.handle_input(event)
                        if result == "RESET": self.reset_game()
                        elif result == "TOGGLE_FS": self._toggle_fullscreen()
                    return

                if event.key == MENU_TOGGLE:
                    self.menu.pause()
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

        if self.menu.active or self.state in [STATE_LOSE, STATE_WIN]:
            return

        now = pygame.time.get_ticks()
        if now - self.last_move > self.move_delay:
            self.direction_lock = False
            new_head = self.snake.get_next_head_position()

            if self.snake.check_collision(new_head):
                self.state = STATE_LOSE
                self.state_render.selected_index = 0
                return

            max_cells = (WIDTH // CELL_SIZE) * (HEIGHT // CELL_SIZE)
            if len(self.snake.segments) >= max_cells:
                self.state = STATE_WIN
                self.state_render.selected_index = 0
                return

            if new_head == self.apple.position:
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
        self.state = STATE_PLAYING
        self.menu.active = False
        self.menu.countdown = False

    def _draw(self):
        self.render.draw(self.snake, self.apple)

        if self.menu.active:
            self.render.draw_menu(self.menu)
        elif self.state in [STATE_LOSE, STATE_WIN]:
            self.state_render.draw_overlay(self.state, self.snake.score)

        pygame.display.flip()

    def _toggle_fullscreen(self):
        try:
            pygame.display.toggle_fullscreen()
            self.menu.overlay = pygame.Surface((WIDTH, HEIGHT))
            self.menu.overlay.fill((0, 0, 0))
            pygame.event.clear()
        except pygame.error:
            print("erreur")