from config.constants import *
import pygame


class Render:
    def __init__(self, screen_surface):
        self.screen = screen_surface
        self.ratio_title = 0.12
        self.ratio_standard = 0.06
        self.ratio_score = 0.04

    def _get_font(self, ratio, bold=False):
        size = int(HEIGHT * ratio)
        return pygame.font.SysFont("Arial", size, bold=bold)

    def draw(self, snake, apple, state, auth_info=None):
        if state == STATE_AUTH:
            self.draw_auth(auth_info)
        else:
            self.screen.fill(COLOR_BG)
            self._draw_grid()
            self._draw_apple(apple)
            self._draw_snake(snake)
            self._draw_score(snake.score)

    def draw_auth(self, auth_info):
        self.screen.fill((30, 30, 30))

        if not auth_info: return
        mode = auth_info["mode"]
        inputs = auth_info["inputs"]

        title_txt = "INSCRIPTION" if mode == "REGISTER" else "CONNEXION"
        self._draw_text_centered(title_txt, WIDTH // 2, HEIGHT * 0.15, self._get_font(self.ratio_title, True),
                                 (255, 255, 255))

        for name, box in inputs.items():
            if name == "conf" and mode != "REGISTER": continue
            box.draw(self.screen)

            font_label = self._get_font(0.03)
            label_map = {"user": "Nom d'utilisateur", "pass": "Mot de passe", "conf": "Confirmer le mot de passe"}
            label_surf = font_label.render(label_map[name], True, (200, 200, 200))
            self.screen.blit(label_surf, (box.rect.x, box.rect.y - 25))

        switch_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT * 0.9, 300, 40)
        pygame.draw.rect(self.screen, (60, 60, 60), switch_rect, border_radius=10)

        switch_txt = "Pas de compte ? S'inscrire" if mode == "LOGIN" else "Déjà un compte ? Se connecter"
        self._draw_text_centered(switch_txt, WIDTH // 2, HEIGHT * 0.925, self._get_font(0.035), (100, 100, 255))

        self._draw_text_centered("Appuyez sur ENTREE pour valider", WIDTH // 2, HEIGHT * 0.82, self._get_font(0.03),
                                 (150, 150, 150))

    def _draw_grid(self):
        for y in range(0, HEIGHT, CELL_SIZE):
            for x in range(0, WIDTH, CELL_SIZE):
                if (x // CELL_SIZE + y // CELL_SIZE) % 2 == 0:
                    pygame.draw.rect(self.screen, COLOR_GRID, (x, y, CELL_SIZE, CELL_SIZE))

    def _draw_apple(self, apple):
        x, y = apple.position
        margin = CELL_SIZE * 0.1
        pygame.draw.rect(self.screen, COLOR_APPLE,
                         (x + margin, y + margin, CELL_SIZE - margin * 2, CELL_SIZE - margin * 2))

    def _draw_snake(self, snake):
        for i, seg in enumerate(snake.segments):
            color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
            x, y = seg
            margin = CELL_SIZE * 0.05
            pygame.draw.rect(self.screen, color,
                             (x + margin, y + margin, CELL_SIZE - margin * 2, CELL_SIZE - margin * 2))

    def _draw_score(self, score):
        font = self._get_font(self.ratio_score, bold=True)
        text = font.render(f"Score: {score}", True, (255, 255, 255))
        self.screen.blit(text, (WIDTH * 0.02, HEIGHT * 0.02))

    def draw_menu(self, menu):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        if menu.countdown:
            font = self._get_font(0.2, bold=True)
            self._draw_text_centered(str(menu.timer), WIDTH // 2, HEIGHT // 2, font, (255, 255, 0))
        else:
            options = menu.current_options
            for i, text in enumerate(options):
                is_selected = (i == menu.selected_index)
                color = (255, 215, 0) if is_selected else (255, 255, 255)
                font = self._get_font(self.ratio_standard, bold=is_selected)
                y_pos = HEIGHT * 0.4 + (i * HEIGHT * 0.1)
                self._draw_text_centered(text, WIDTH // 2, y_pos, font, color)

    def _draw_text_centered(self, text, x, y, font, color):
        img = font.render(text, True, color)
        rect = img.get_rect(center=(x, y))
        self.screen.blit(img, rect)