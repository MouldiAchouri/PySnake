import sys
import threading
from config.constants import *
from game import Snake, Apple, Menu
from view.render import Render
from view.state_render import StateRender
from view.window_manager import WindowManager
from view.input_box import InputBox
from view.auth_render import AuthRender
import utils.db_manager as db
import score_manager

STATE_AUTH = 10
STATE_SYNC = 11


class Game:
    def __init__(self):
        pygame.init()
        db.init_db()

        self.wm = WindowManager()
        self.clock = pygame.time.Clock()
        self.start_time = pygame.time.get_ticks()
        self.score_saved = False
        self.current_user = None

        self.snake = Snake()
        self.apple = Apple()
        self.apple.spawn(self.snake.segments)
        self.menu = Menu()

        self.render = Render(self.wm.virtual_surface)
        self.state_render = StateRender(self.wm.virtual_surface)
        self.auth_render = AuthRender(self.wm.screen)

        self.auth_mode = "LOGIN"
        self.inputs = {
            "user": InputBox(0, 0, 0, 0),
            "pass": InputBox(0, 0, 0, 0, is_password=True),
            "conf": InputBox(0, 0, 0, 0, is_password=True),
        }
        self.auth_error = ""
        self._switch_btn_rect = None

        self.state = STATE_AUTH
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
                self._terminate()

            if event.type == pygame.VIDEORESIZE and not self.wm.is_fullscreen:
                self.wm.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.auth_render._update_screen_ref(self.wm.screen)

            if self.state == STATE_AUTH:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    for box in self.inputs.values():
                        if hasattr(box, 'screen_rect'):
                            box.active = box.screen_rect.collidepoint(pos)
                    if self._switch_btn_rect and self._switch_btn_rect.collidepoint(pos):
                        self._toggle_auth_mode()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self._process_auth()
                        return
                    for box in self.inputs.values():
                        box.handle_event(event)
                return

            if event.type == pygame.KEYDOWN:
                if self.state in [STATE_LOSE, STATE_WIN]:
                    self._handle_overlay_input(event.key)
                elif self.menu.active:
                    result = self.menu.handle_input(event)
                    if result == "RESET":
                        self.reset_game()
                    elif result == "TOGGLE_FS":
                        self.wm.toggle_fullscreen()
                        self.auth_render._update_screen_ref(self.wm.screen)
                    elif result == "TOGGLE_SYNC":
                        self._toggle_sync_from_menu()
                elif self.state == STATE_PLAYING:
                    if event.key == MENU_TOGGLE:
                        self.menu.sync_enabled = db.is_sync_enabled(self.current_user)
                        self.menu.pause()
                        self.wm.toggle_resizable(True)
                    elif not self.direction_lock:
                        self._change_direction(event.key)

    def _toggle_auth_mode(self):
        self.auth_mode = "LOGIN" if self.auth_mode == "REGISTER" else "REGISTER"
        self.auth_error = ""
        for box in self.inputs.values():
            box.text = ""
            box.active = False

    def _process_auth(self):
        username = self.inputs["user"].text.strip()
        password = self.inputs["pass"].text

        if len(username) < 3 or len(password) < 3:
            self.auth_error = "Pseudo et mot de passe : 3 caractères minimum."
            return

        if self.auth_mode == "REGISTER":
            confirm = self.inputs["conf"].text
            if password != confirm:
                self.auth_error = "Les mots de passe ne correspondent pas."
                return
            if db.register_user(username, password):
                self.current_user = username
                self._after_auth()
            else:
                self.auth_error = "Ce pseudo est déjà pris."
        else:
            if db.login_user(username, password):
                self.current_user = username
                self._after_auth(from_login=True)
            else:
                self.auth_error = "Pseudo ou mot de passe incorrect."
    def _run_sync_screen(self):
        self.wm.screen.fill((20, 20, 30))
        self.auth_render.draw_sync()
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._terminate()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_o:
                        db.set_sync_preference(self.current_user, True)
                        self.state = STATE_PLAYING
                        return
                    elif event.key == pygame.K_n:
                        db.set_sync_preference(self.current_user, False)
                        self.state = STATE_PLAYING
                        return
            self.clock.tick(FPS)

    def _after_auth(self, from_login=False):
        score_manager.refresh_online_cache(self.current_user)

        if not db.has_configured_sync(self.current_user):
            self._run_sync_screen()
            if from_login and db.is_sync_enabled(self.current_user):
                threading.Thread(target=db.download_scores_from_server, args=(self.current_user,), daemon=True).start()
        else:
            if from_login and db.is_sync_enabled(self.current_user):
                threading.Thread(target=db.download_scores_from_server, args=(self.current_user,), daemon=True).start()
            self.state = STATE_PLAYING

    def _toggle_sync_from_menu(self):
        current = db.is_sync_enabled(self.current_user)
        new_state = not current
        db.update_user_sync_preference(self.current_user, new_state)
        self.menu.sync_enabled = new_state

        if new_state:
            score_manager.sync_existing_scores(self.current_user)

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
            self.snake.direction = UP; self.direction_lock = True
        elif key == DOWN and self.snake.direction != UP:
            self.snake.direction = DOWN; self.direction_lock = True
        elif key == LEFT and self.snake.direction != RIGHT:
            self.snake.direction = LEFT; self.direction_lock = True
        elif key == RIGHT and self.snake.direction != LEFT:
            self.snake.direction = RIGHT; self.direction_lock = True

    def _handle_game_over(self, result_state):
        self.direction_lock = True
        self.state = result_state
        self.state_render.selected_index = 0

        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000

        score_manager.add_new_score(
            self.current_user,
            self.snake.score,
            elapsed_time,
            result_state
        )
        self.score_saved = True

        score_manager.refresh_online_cache(self.current_user)

        self.wm.toggle_resizable(True)
        self.last_move = pygame.time.get_ticks() + 10000

    def reset_game(self):
        self.snake.reset()
        self.apple.spawn(self.snake.segments)
        self.move_delay = 150
        self.state = STATE_PLAYING
        self.menu.active = False
        self.menu.countdown = False
        self.start_time = pygame.time.get_ticks()
        self.score_saved = False
        self.direction_lock = False
        self.last_move = pygame.time.get_ticks()

    def _update(self):
        self.menu.update()

        if self.state in [STATE_AUTH, STATE_SYNC]:
            return

        if self.state in [STATE_LOSE, STATE_WIN]:
            return

        if self.menu.countdown or (not self.menu.active and self.state == STATE_PLAYING):
            self.wm.toggle_resizable(False)
        else:
            self.wm.toggle_resizable(True)

        if self.menu.active:
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

    def _draw(self):
        if self.state == STATE_AUTH:
            self._switch_btn_rect = self.auth_render.draw_auth(
                self.auth_mode, self.inputs, self.auth_error)
        else:
            self.render.draw(self.snake, self.apple)
            if self.menu.active:
                self.render.draw_menu(self.menu)
            elif self.state in [STATE_LOSE, STATE_WIN]:
                self.state_render.current_username = self.current_user
                self.state_render.draw_overlay(self.state, self.snake.score)
            self.wm.final_render()