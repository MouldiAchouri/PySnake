import pygame
from config.constants import HEIGHT

class InputBox:
    def __init__(self, x, y, w, h, is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.is_password = is_password
        self.active = False
        self.font = pygame.font.SysFont("Arial", int(HEIGHT * 0.035))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key not in (pygame.K_RETURN, pygame.K_TAB):
                if len(self.text) < 20 and event.unicode.isprintable():
                    self.text += event.unicode

    def draw(self, surface, label):
        # Label
        font_label = pygame.font.SysFont("Arial", int(HEIGHT * 0.028))
        label_surf = font_label.render(label, True, (180, 180, 180))
        surface.blit(label_surf, (self.rect.x, self.rect.y - int(HEIGHT * 0.03)))

        # Box
        border_color = (120, 100, 255) if self.active else (80, 80, 80)
        pygame.draw.rect(surface, (30, 30, 40), self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)

        # Text
        display = "*" * len(self.text) if self.is_password else self.text
        txt_surf = self.font.render(display, True, (255, 255, 255))
        surface.blit(txt_surf, (self.rect.x + 10, self.rect.y + (self.rect.h - txt_surf.get_height()) // 2))