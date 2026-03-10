from config.constants import *
import sys

class Menu:
    def __init__(self, options= None):
        self.active = False
        self.countdown = False
        self.timer = 0

        self.overlay = pygame.Surface((WIDTH, HEIGHT))
        self.overlay.fill((0 ,0 ,0 ))
        self.start_ticks = pygame.time.get_ticks()

        self.options = options if options else ["Reprendre","Recommencer","Option", "Quitter"]
        self.selected_index = 0

    def start_countdown(self):
        self.countdown = True
        self.timer = 3
        self.start_ticks = pygame.time.get_ticks()

    def navigate(self, direction):
        self.selected_index = (self.selected_index + direction) % len(self.options)

    def execute_option(self):
        selection = self.options[self.selected_index]

        if selection == "Reprendre":
            self.start_countdown()
        elif selection == "Quitter":
            pygame.quit()
            sys.exit()
        elif selection == "Recommencer":
            return "RESET"

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


