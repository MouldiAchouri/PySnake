import pygame
from config.constants import WIDTH, HEIGHT, STATE_LOSE


class StateRender:
    def __init__(self, screen, font_bold, font_standard):
        self.screen = screen
        self.font_bold = font_bold
        self.font_standard = font_standard

        self.options = ["Recommencer", "Quitter"]
        self.selected_index = 0

    def draw_overlay(self, state, score):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = "GAME OVER" if state == STATE_LOSE else "VICTOIRE !"
        color = (255, 50, 50) if state == STATE_LOSE else (50, 255, 50)
        self._draw_centered_text(title, self.font_bold, color, -100)

        self._draw_centered_text(f"Score : {score}", self.font_standard, (255, 255, 255), -30)

        for i, text in enumerate(self.options):
            is_selected = (i == self.selected_index)
            color = (255, 215, 0) if is_selected else (255, 255, 255)
            y_pos = 50 + (i * 60)
            self._draw_centered_text(text, self.font_standard, color, y_pos)

    def _draw_centered_text(self, text, font, color, y_offset):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
        self.screen.blit(surface, rect)