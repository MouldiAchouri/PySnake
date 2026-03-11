from config.constants import *
import sys

class Menu:
    def __init__(self, options= None):
        self.active = False
        self.countdown = False
        self.timer = 0
        self.in_options = False
        self.confirm_quit = False

        self.overlay = pygame.Surface((WIDTH, HEIGHT))
        self.overlay.fill((0 ,0 ,0 ))
        self.start_ticks = pygame.time.get_ticks()

        self.main_options = options if options else ["Reprendre","Recommencer","Option", "Quitter"]
        self.settings_options = ["Plein Ecran", "Retour"]
        self.selected_index = 0

    @property
    def current_options(self):
        if self.confirm_quit:
            return ["Annuler", "Quitter Definitivement"]
        elif self.in_options:
            is_full = pygame.display.get_surface().get_flags() & pygame.FULLSCREEN
            fs_text = "Mode fenetre" if is_full else "Plein Ecran"
            return [fs_text, "Retour"]
        return self.main_options

    def start_countdown(self):
        self.countdown = True
        self.timer = 3
        self.start_ticks = pygame.time.get_ticks()

    def navigate(self, direction):
        self.selected_index = (self.selected_index + direction) % len(self.current_options)

    def execute_option(self):
        selection = self.current_options[self.selected_index]

        if self.confirm_quit:
            if selection == "Quitter Definitivement":
                pygame.quit()
                sys.exit()
            else:
                self.confirm_quit = False
                self.selected_index = 3
            return None

        if not self.in_options:
            if selection == "Reprendre":
                self.start_countdown()
            elif selection == "Recommencer":
                return "RESET"
            elif selection == "Option":
                self.in_options = True
                self.selected_index = 0
            elif selection == "Quitter":
                self.confirm_quit = True
                self.selected_index = 0
        else:
            if self.selected_index == 0:
                return "TOGGLE_FS"
            elif selection == "Retour":
                self.in_options = False
                self.selected_index = 2
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


