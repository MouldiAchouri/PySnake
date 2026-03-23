import pygame
from config.constants import WIDTH, HEIGHT, STATE_LOSE
import score_manager

class StateRender:
    def __init__(self, screen, font_bold, font_standard):
        self.screen = screen
        self.font_bold = font_bold
        self.font_standard = font_standard
        self.font_mono = pygame.font.SysFont("Consolas", 32, bold=True)

        self.options = ["Recommencer", "Quitter"]
        self.selected_index = 0

    def draw_overlay(self, state, current_score):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(230)
        overlay.fill((10, 10, 10))
        self.screen.blit(overlay, (0, 0))

        title = "GAME OVER" if state == STATE_LOSE else "VICTOIRE !"
        title_color = (255, 50, 50) if state == STATE_LOSE else (50, 255, 50)

        self._draw_centered_text(title, self.font_bold, title_color, -400)
        self._draw_centered_text(f"SCORE : {current_score}", self.font_standard, (255, 255, 255), -320)

        self._draw_highscore_table()

        for i, text in enumerate(self.options):
            is_selected = (i == self.selected_index)
            color = (255, 215, 0) if is_selected else (180, 180, 180)
            y_pos = 380 + (i * 90)
            self._draw_centered_text(text, self.font_standard, color, y_pos)

    def _draw_highscore_table(self):
        scores = score_manager.load_scores()
        center_x = WIDTH // 2

        start_x = center_x - 380
        offsets = [ 0, 160, 480, 680 ]
        y_header = HEIGHT // 2 - 200

        headers = ["RANG", "JOUEUR", "SCORE", "TEMPS"]
        for i, head in enumerate(headers):
            surf = self.font_mono.render(head, True, (150, 150, 150))
            self.screen.blit(surf, (start_x + offsets[i], y_header))

        for i, entry in enumerate(scores):
            y_row = y_header + 70 + (i * 45)
            color = (255, 215, 0) if i == 0 else (255, 255, 255)
            row_data = [f"#{i+1}", entry['username'][:12], str(entry['score']), f"{entry['timer']:.2f}s"]
            for j, data in enumerate(row_data):
                surf = self.font_mono.render(data, True, color)
                self.screen.blit(surf, (start_x + offsets[j], y_row))

    def _draw_centered_text(self, text, font, color, y_offset):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
        self.screen.blit(surface, rect)