import sys
import requests
from config.constants import *
from game import Snake, Apple, Menu
from view.input_box import InputBox
from view.render import Render
from view.state_render import StateRender
from view.window_manager import WindowManager
from utils.db_manager import *

class Game:
    def __init__(self):
        pygame.init()
        init_db()

        self.wm = WindowManager()
        self.screen = self.wm.screen

        self.sync_enabled = True

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

                    sync_rect = pygame.Rect(WIDTH // 2 - 100, int(HEIGHT * 0.82), 200, 30)

                    if switch_rect.collidepoint(mx, my):
                        self.auth_mode = "REGISTER" if self.auth_mode == "LOGIN" else "LOGIN"
                        for box in self.inputs.values(): box.text = ""

                    elif sync_rect.collidepoint(mx, my):
                        self.sync_enabled = not self.sync_enabled
                        username = self.inputs["user"].text

                        if self.state != STATE_AUTH and len(username) > 2:
                            update_user_sync_preference(username, self.sync_enabled)
                            print(f" préférence sauvegardée : {username}")

                            if self.sync_enabled:
                                self._fetch_remote_history()
                                self._sync_pending_scores()
                        else:
                            status = "ON" if self.sync_enabled else "OFF"
                            print(f"Option Partage de score : {status} (en attente de connexion)")

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        order = ["user", "pass", "conf"] if self.auth_mode == "REGISTER" else ["user", "pass"]
                        idx = -1
                        for i, name in enumerate(order):
                            if self.inputs[name].active:
                                idx = i
                                break
                        for box in self.inputs.values(): box.active = False
                        next_name = order[(idx + 1) % len(order)]
                        self.inputs[next_name].active = True
                        continue

                    if event.key == pygame.K_RETURN:
                        self._attempt_auth()
                        continue

                for name, box in self.inputs.items():
                    if name == "conf" and self.auth_mode == "LOGIN": continue
                    box.handle_event(event)
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
                if register_user(username, password, self.sync_enabled):
                    print(f"✅ Joueur créé avec sync: {self.sync_enabled}")
                    if self.sync_enabled:
                        self._sync_pending_scores()
                        self._fetch_remote_history()
                    self._start_game()
                else:
                    print("Erreur : Pseudo déjà pris")
        else:
            if login_user(username, password):
                print(f"Connexion réussie : {username}")
                self.sync_enabled = is_sync_enabled(username)
                print(f"📊 Préférence utilisateur chargée : Online={'ON' if self.sync_enabled else 'OFF'}")

                if self.sync_enabled:
                    self._sync_pending_scores()
                    self._fetch_remote_history()

                self._start_game()
            else:
                print("Erreur : Identifiants incorrects")

    def _start_game(self):
        self.state = STATE_PLAYING
        self.start_time = pygame.time.get_ticks()
        self.last_move = pygame.time.get_ticks()

    def _handle_overlay_input(self, key):
        if key in [UP, MENU_UP]:
            self.state_render.selected_index = (self.state_render.selected_index - 1) % 2
        elif key in [DOWN, MENU_DOWN]:
            self.state_render.selected_index = (self.state_render.selected_index + 1) % 2

        elif key == pygame.K_TAB:
            self.state_render.show_global = not self.state_render.show_global

            if self.state_render.show_global:
                print("🌐 Récupération des scores mondiaux...")
                self.state_render.fetch_global_scores()

        elif key == pygame.K_p:
            if not self.score_saved_globally:
                self._publish_to_server()

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
            if self.state_render.show_global:
                now = pygame.time.get_ticks()
                if not hasattr(self, 'last_global_refresh'):
                    self.last_global_refresh = now

                if now - self.last_global_refresh > 30000:
                    print("🔄 Actualisation automatique du classement mondial...")
                    self.state_render.fetch_global_scores()
                    self.last_global_refresh = now
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
        self.score_saved_globally = False

        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
        username = self.inputs["user"].text or "Joueur"

        self.last_score_id = save_score_locally(username, self.snake.score, elapsed_time)
        self.score_saved = True
        self.wm.toggle_resizable(True)

        print(f"Score local enregistré avec l'ID: {self.last_score_id}")

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
        auth_info = {"inputs": self.inputs, "mode": self.auth_mode, "sync_enabled": self.sync_enabled}
        self.render.draw(self.snake, self.apple, self.state, auth_info)

        if self.menu.active:
            self.render.draw_menu(self.menu)
        elif self.state in [STATE_LOSE, STATE_WIN]:
            self.state_render.draw_overlay(self.state, self.snake.score)

        self.wm.final_render()

    def _publish_to_server(self):
        username = self.inputs["user"].text or "Joueur"

        if not  is_sync_enabled(username):
            print("Publication annulée: l'option online désactivée")
            return

        score = self.snake.score
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000

        payload = {
            "username": username,
            "score_value": score,
            "timer": round(elapsed_time, 2)
        }

        try:
            print("🌐 Envoi du score au serveur Render...")
            response = requests.post("https://pysnake-api.onrender.com/scores", json=payload, timeout=10)

            if response.status_code == 200:
                print("✅ Score enregistré dans PostgreSQL !")
                mark_score_as_synced(self.last_score_id)
                self.score_saved = True
                self.score_saved_globally = True

                self.state_render.fetch_global_scores()
                self.state_render.show_global = True
            else:
                print(f"❌ Erreur serveur (Code {response.status_code})")
        except Exception as e:
            print(f"⚠️ Erreur de connexion : {e}")

    def _sync_pending_scores(self):
        username = self.inputs["user"].text
        pending = get_unsynced_scores(username)
        if not pending: return

        print(f"🔄 {len(pending)} score(s) en attente de sync")
        for s in pending:
            payload = {"username": username, "score_value": s["score_value"], "timer": round(s["timer"], 2)}
            try:
                r = requests.post("https://pysnake-api.onrender.com/scores", json=payload, timeout=10)
                if r.status_code == 200:
                    mark_score_as_synced(s["id"])
                    print(f"  Score {s['id']} synchronisé")
            except:
                break

    def _fetch_remote_history(self):
        username = self.inputs["user"].text
        print(f"🌐 Récupération de l'historique distant pour {username}...")
        try:
            r = requests.get(f"https://pysnake-api.onrender.com/scores/{username}", timeout=5)
            if r.status_code == 200:
                scores = r.json()
                for s in scores:
                    sync_remote_score_local(username, s['score_value'], s['timer'])
                print(f"✅ {len(scores)} scores synchronisés depuis le cloud.")
        except Exception as e:
            print(f"⚠️ Erreur lors de la récupération : {e}")