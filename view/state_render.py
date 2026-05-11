import pygame
from config.constants import WIDTH, HEIGHT, STATE_LOSE
import score_manager


class StateRender:
    def __init__(self, screen):
        self.screen = screen
        self.selected_index = 0
        self.options = ["Recommencer", "Quitter"]
        self.current_username = None

    def _get_font(self, ratio, bold=False, mono=False):
        size = int(HEIGHT * ratio)
        name = "Consolas" if mono else "Arial"
        return pygame.font.SysFont(name, size, bold=bold)

    def draw_overlay(self, state, current_score):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(230)
        overlay.fill((10, 10, 10))
        self.screen.blit(overlay, (0, 0))

        title = "GAME OVER" if state == STATE_LOSE else "VICTOIRE !"
        title_color = (255, 50, 50) if state == STATE_LOSE else (50, 255, 50)

        self._draw_centered(title, self._get_font(0.1, bold=True), title_color, HEIGHT * 0.15)
        self._draw_centered(f"SCORE : {current_score}", self._get_font(0.05), (255, 255, 255), HEIGHT * 0.25)

        self._draw_highscore_table()

        for i, text in enumerate(self.options):
            is_selected = (i == self.selected_index)
            color = (255, 215, 0) if is_selected else (180, 180, 180)
            y_pos = HEIGHT * 0.8 + (i * HEIGHT * 0.08)
            self._draw_centered(text, self._get_font(0.05, bold=is_selected), color, y_pos)

    def _draw_highscore_table(self):
        if self.current_username:
            scores = score_manager.get_leaderboard(self.current_username)
        else:
            scores = []

        if not scores:
            font = self._get_font(0.035, mono=True)
            self._draw_centered("Aucun score disponible", font, (150, 150, 150), HEIGHT * 0.5)
            return

        col_ratios = [0.15, 0.32, 0.65, 0.82]
        y_table_start = HEIGHT * 0.35

        f_head = self._get_font(0.03, bold=True, mono=True)
        f_row = self._get_font(0.035, mono=True)

        headers = ["RANG", "JOUEUR", "SCORE", "TEMPS"]
        for i, head in enumerate(headers):
            surf = f_head.render(head, True, (150, 150, 150))
            self.screen.blit(surf, (WIDTH * col_ratios[i], y_table_start))

        for i, entry in enumerate(scores):
            y_row = y_table_start + HEIGHT * 0.05 + (i * HEIGHT * 0.038)
            color = (255, 215, 0) if i == 0 else (255, 255, 255)

            data = [f"#{i + 1}", entry['username'][:10], str(entry['score']), f"{entry['timer']:.1f}s"]
            for j, text in enumerate(data):
                surf = f_row.render(text, True, color)
                self.screen.blit(surf, (WIDTH * col_ratios[j], y_row))

    def _draw_centered(self, text, font, color, y_pos):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(WIDTH // 2, y_pos))
        self.screen.blit(surface, rect)