import pygame
import ctypes
import os
from config.constants import WIDTH, HEIGHT

try:
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass


class WindowManager:
    def __init__(self):
        self.logical_res = (WIDTH, HEIGHT)
        self.virtual_surface = pygame.Surface(self.logical_res)

        os.environ['SDL_VIDEO_CENTERED'] = '1'

        info = pygame.display.Info()
        self.monitor_w = info.current_w
        self.monitor_h = info.current_h

        self.win_size = int(self.monitor_h * 0.8)
        self.is_fullscreen = False

        self.screen = pygame.display.set_mode((self.win_size, self.win_size), pygame.RESIZABLE)
        pygame.display.set_caption('Snake')

    def toggle_resizable(self, can_resize):
        if self.is_fullscreen: return

        flags = pygame.RESIZABLE if can_resize else 0
        if (self.screen.get_flags() & pygame.RESIZABLE) != flags:
            curr_w, curr_h = self.screen.get_size()
            self.screen = pygame.display.set_mode((curr_w, curr_h), flags)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((self.monitor_w, self.monitor_h), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.win_size, self.win_size), pygame.RESIZABLE)

    def final_render(self):
        win_w, win_h = self.screen.get_size()

        game_size = min(win_w, win_h)

        pos_x = (win_w - game_size) // 2
        pos_y = (win_h - game_size) // 2

        scaled_surf = pygame.transform.scale(self.virtual_surface, (game_size, game_size))

        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled_surf, (pos_x, pos_y))
        pygame.display.flip()

    def get_virtual_mouse_pos(self, real_pos):
        win_w, win_h = self.screen.get_size()
        game_size = min(win_w, win_h)
        pos_x = (win_w - game_size) // 2
        pos_y = (win_h - game_size) // 2

        try:
            virtual_x = (real_pos[0] - pos_x) * (WIDTH / game_size)
            virtual_y = (real_pos[1] - pos_y) * (HEIGHT / game_size)
            return int(virtual_x), int(virtual_y)
        except (ZeroDivisionError, TypeError):
            return 0, 0
