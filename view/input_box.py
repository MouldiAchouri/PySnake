import pygame

from config.constants import *

class InputBox:
    def __init__(self, x, y, w, h, text='', is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (100, 100, 100)
        self.text = text
        self.is_password = is_password
        self.font = pygame.font.SysFont("Arial", 24)
        self.txt_surface = self.font.render(text, True, (255, 255, 255))
        self.active = False

        self.last_backspace_time = 0
        self.current_backspace_delay = 500

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = (255, 255, 255) if self.active else (100, 100, 100)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key in [pygame.K_RETURN, pygame.K_TAB]:
                return
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self.last_backspace_time = pygame.time.get_ticks()
                self.current_backspace_delay = 500
            elif event.key == pygame.K_RETURN:
                pass
            elif event.key == pygame.K_TAB:
                pass
            else:
                if len(self.text) < 20 and event.unicode.isprintable():
                    self.text += event.unicode

    def update(self):
        if self.active and pygame.key.get_pressed()[pygame.K_BACKSPACE]:
            now = pygame.time.get_ticks()
            if now - self.last_backspace_time > self.current_backspace_delay:
                self.text = self.text[:-1]
                self.last_backspace_time = now
                self.current_backspace_delay = 50

    def draw(self, screen):
        display_text = "*" * len(self.text) if self.is_password else self.text
        self.txt_surface = self.font.render(display_text, True, (255, 255, 255))
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 7))