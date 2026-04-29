import sys
from config.constants import *
from game import Snake, Apple, Menu
from view.input_box import InputBox
from view.render import Render
from view.state_render import StateRender
from view.window_manager import WindowManager
from utils import score_manager
from utils.db_manager import init_db, register_user


class Game:
    def __init__(self):
        pygame.init()
        init_db()

        self.wm = WindowManager()
        self.screen = self.wm.screen

        self.clock = pygame.time.Clock()
        self.start_time = pygame.time.get_ticks()
        self.score_saved = False

        self.snake = Snake()
        self.apple = Apple()
        self.apple.spawn(self.snake.segments)
        self.menu = Menu()

        self.render = Render(self.wm.virtual_surface)
        self.state_render = StateRender(self.wm.virtual_surface)

        self.state = STATE_AUTH
        self.auth_mode = "LOGIN"

        box_w = 300
        self.inputs = {
            "user": InputBox(WIDTH // 2 - box_w // 2, HEIGHT * 0.4, box_w, 40),
            "pass": InputBox(WIDTH // 2 - box_w // 2, HEIGHT * 0.5, box_w, 40, is_password=True),
            "conf": InputBox(WIDTH // 2 - box_w // 2, HEIGHT * 0.6, box_w, 40, is_password=True),
        }
        self.direction_lock = False
        self.move_delay = 150
        self.last_move = pygame.time.get_ticks()

    def run(self):
        while True:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

    def _fix_mouse_pos(self, event):
        win_w, win_h = self.wm.screen.get_size()
        game_size = min(win_w, win_h)
        offset_x = (win_w - game_size) // 2
        offset_y = (win_h - game_size) // 2

        m_x, m_y = event.pos
        virtual_x = (m_x - offset_x) * (WIDTH / game_size)
        virtual_y = (m_y - offset_y) * (HEIGHT / game_size)
        event.pos = (virtual_x, virtual_y)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._terminate()

            if self.state == STATE_AUTH:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._fix_mouse_pos(event)
                    mx, my = event.pos

                    switch_rect = pygame.Rect(WIDTH // 2 - 150, int(HEIGHT * 0.9), 300, 40)

                    if switch_rect.collidepoint(mx, my):
                        self.auth_mode = "REGISTER" if self.auth_mode == "LOGIN" else "LOGIN"
                        for box in self.inputs.values(): box.text = ""

                for box in self.inputs.values():
                    box.handle_event(event)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        keys = list(self.inputs.keys())
                        for i, key in enumerate(keys):
                            if self.inputs[key].active:
                                self.inputs[key].active = False
                                next_key = keys[(i + 1) % len(keys)]
                                self.inputs[next_key].active = True
                                break
                continue

            if event.type == pygame.VIDEORESIZE:
                if not self.wm.is_fullscreen:
                    self.wm.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            if event.type == pygame.KEYDOWN:
                if self.state in [STATE_LOSE, STATE_WIN]:
                    self._handle_overlay_input(event.key)
                elif self.menu.active:
                    result = self.menu.handle_input(event)
                    if result == "RESET":
                        self.reset_game()
                    elif result == "TOGGLE_FS":
                        self.wm.toggle_fullscreen()
                else:
                    if event.key == MENU_TOGGLE:
                        self.menu.pause()
                        self.wm.toggle_resizable(True)
                    elif not self.direction_lock:
                        self._change_direction(event.key)

    def _attempt_auth(self):
        username = self.inputs["user"].text
        password = self.inputs["pass"].text

        if self.auth_mode == "REGISTER":
            confirm = self.inputs["conf"].text
            if password == confirm and len(username) > 2 and len(password) > 3:
                success = register_user(username, password, True)
                if success:
                    print(f"Joueur {username} créé")
                    self._start_game()
                else:
                    print("Pseudo déjà pris")
        else:
            if len(username) > 2:
                print(f"Connexion de {username}...")
                self._start_game()

    def _start_game(self):
        """Initialise les timers pour éviter un game over immédiat après l'auth."""
        self.state = STATE_PLAYING
        self.start_time = pygame.time.get_ticks()
        self.last_move = pygame.time.get_ticks()

    def _handle_overlay_input(self, key):
        if key in [UP, MENU_UP]:
            self.state_render.selected_index = (self.state_render.selected_index - 1) % 2
        elif key in [DOWN, MENU_DOWN]:
            self.state_render.selected_index = (self.state_render.selected_index + 1) % 2
        elif key == MENU_TOGGLE:
            if self.state_render.selected_index == 0:
                self.reset_game()
            else:
                self._terminate()

    @staticmethod
    def _terminate():
        pygame.quit()
        sys.exit()

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
        if self.state == STATE_AUTH:
            for box in self.inputs.values():
                box.update()
            return

        self.menu.update()

        if self.menu.countdown or (not self.menu.active and self.state == STATE_PLAYING):
            self.wm.toggle_resizable(False)
        else:
            self.wm.toggle_resizable(True)

        if self.menu.active or self.state in [STATE_LOSE, STATE_WIN]:
            return

        now = pygame.time.get_ticks()
        if now - self.last_move > self.move_delay:
            self.direction_lock = False
            new_head = self.snake.get_next_head_position()

            if self.snake.check_collision(new_head):
                self._handle_game_over(STATE_LOSE)
                return

            max_cells = (WIDTH // CELL_SIZE) * (HEIGHT // CELL_SIZE)
            if len(self.snake.segments) >= max_cells:
                self._handle_game_over(STATE_WIN)
                return

            if new_head == self.apple.position:
                self.snake.move(new_head, growing=True)
                self.apple.spawn(self.snake.segments)
                self.move_delay = max(90, self.move_delay - 3)
            else:
                self.snake.move(new_head, growing=False)

            self.last_move = now

    def _handle_game_over(self, result_state):
        self.state = result_state
        self.state_render.selected_index = 0
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
        score_manager.add_new_score(self.inputs["user"].text or "Joueur", self.snake.score, elapsed_time, result_state)
        self.score_saved = True
        self.wm.toggle_resizable(True)

    def reset_game(self):
        self.snake.reset()
        self.apple.spawn(self.snake.segments)
        self.move_delay = 150
        self.state = STATE_PLAYING
        self.menu.active = False
        self.menu.countdown = False
        self.start_time = pygame.time.get_ticks()
        self.score_saved = False

    def _draw(self):
        auth_info = {"inputs": self.inputs, "mode": self.auth_mode}
        self.render.draw(self.snake, self.apple, self.state, auth_info)

        if self.menu.active:
            self.render.draw_menu(self.menu)
        elif self.state in [STATE_LOSE, STATE_WIN]:
            self.state_render.draw_overlay(self.state, self.snake.score)

        self.wm.final_render()