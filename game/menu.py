from config.constants import *
import sys


class Menu:
    def __init__(self, options=None):
        self.active = False
        self.countdown = False
        self.timer = 0
        self.in_options = False
        self.confirm_quit = False
        self.sync_enabled = False

        self.overlay = pygame.Surface((WIDTH, HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.start_ticks = pygame.time.get_ticks()

        self.main_options = options if options else ["Reprendre", "Recommencer", "Option", "Quitter"]
        self.settings_options = ["Plein Ecran", "Retour"]
        self.selected_index = 0

    @property
    def current_options(self):
        if self.confirm_quit:
            return [TXT_CANCEL, TXT_CONFIRM_QUIT]
        if self.in_options:
            is_full = pygame.display.get_surface().get_flags() & pygame.FULLSCREEN
            sync_label = "Sync : ON" if self.sync_enabled else "Sync : OFF"
            return [TXT_WINDOWED if is_full else TXT_FULLSCREEN, sync_label, TXT_BACK]
        return [TXT_RESUME, TXT_RESTART, TXT_OPTIONS, TXT_QUIT]

    def start_countdown(self):
        self.countdown = True
        self.timer = 3
        self.start_ticks = pygame.time.get_ticks()

    def navigate(self, direction):
        self.selected_index = (self.selected_index + direction) % len(self.current_options)

    def execute_option(self):
        selection = self.current_options[self.selected_index]

        if self.confirm_quit:
            if selection == TXT_CONFIRM_QUIT:
                pygame.quit()
                sys.exit()
            self.confirm_quit = False
            self.selected_index = 3
            return None

        if self.in_options:
            if self.selected_index == 0:
                return "TOGGLE_FS"
            elif self.selected_index == 1:
                return "TOGGLE_SYNC"
            self.in_options = False
            self.selected_index = 2
            return None

        if selection == TXT_RESUME:
            self.start_countdown()
        elif selection == TXT_RESTART:
            return "RESET"
        elif selection == TXT_OPTIONS:
            self.in_options = True
            self.selected_index = 0
        elif selection == TXT_QUIT:
            self.confirm_quit = True
            self.selected_index = 0
        return None

    def handle_input(self, event):
        if self.active and not self.countdown:
            if event.type == pygame.KEYDOWN:
                if event.key == MENU_UP:
                    self.navigate(-1)
                elif event.key == MENU_DOWN:
                    self.navigate(1)
                elif event.key == MENU_TOGGLE:
                    return self.execute_option()
        return None

    def pause(self):
        if not self.active:
            self.active = True
            self.countdown = False
        else:
            self.start_countdown()

    def update(self):
        if self.active and self.countdown:
            now = pygame.time.get_ticks()
            elapsed = (now - self.start_ticks) // 1000
            self.timer = 3 - elapsed
            if self.timer <= 0:
                self.active = False
                self.countdown = False