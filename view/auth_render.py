import pygame


class AuthRender:
    def __init__(self, screen):
        self.screen = screen

    def _update_screen_ref(self, screen):
        self.screen = screen

    def _font(self, size_px, bold=False):
        return pygame.font.SysFont("Arial", max(8, size_px), bold=bold)

    def _W(self):
        return self.screen.get_width()

    def _H(self):
        return self.screen.get_height()

    def _centered(self, text, font, color, y):
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=(self._W() // 2, y)))

    def _blit_on_rect(self, text, font, color, rect):
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def draw_auth(self, mode, inputs, error_msg=""):
        W, H = self._W(), self._H()
        self.screen.fill((20, 20, 30))

        self._centered(
            "INSCRIPTION" if mode == "REGISTER" else "CONNEXION",
            self._font(int(H * 0.08), bold=True),
            (200, 190, 255),
            int(H * 0.11)
        )

        field_w = int(W * 0.38)
        field_h = int(H * 0.07)
        field_x = W // 2 - field_w // 2
        font_label = self._font(int(H * 0.026))
        font_text  = self._font(int(H * 0.033))

        if mode == "REGISTER":
            fields = [
                ("user", "Nom d'utilisateur",        int(H * 0.26)),
                ("pass", "Mot de passe",              int(H * 0.41)),
                ("conf", "Confirmer le mot de passe", int(H * 0.56)),
            ]
        else:
            fields = [
                ("user", "Nom d'utilisateur", int(H * 0.32)),
                ("pass", "Mot de passe",       int(H * 0.48)),
            ]

        for key, label, y in fields:
            box = inputs[key]

            lsurf = font_label.render(label, True, (170, 170, 180))
            self.screen.blit(lsurf, (field_x, y - int(H * 0.03)))

            rect = pygame.Rect(field_x, y, field_w, field_h)
            border_col = (130, 105, 255) if box.active else (65, 65, 78)
            pygame.draw.rect(self.screen, (28, 28, 40), rect, border_radius=9)
            pygame.draw.rect(self.screen, border_col, rect, 2, border_radius=9)

            display = "*" * len(box.text) if box.is_password else box.text
            tsurf = font_text.render(display, True, (245, 245, 245))
            self.screen.blit(tsurf, (rect.x + 12,
                                     rect.y + (field_h - tsurf.get_height()) // 2))

            box.screen_rect = rect

        if error_msg:
            err_y = int(H * 0.74) if mode == "REGISTER" else int(H * 0.62)
            self._centered(error_msg, self._font(int(H * 0.027)), (255, 75, 75), err_y)

        hint_y = int(H * 0.82) if mode == "REGISTER" else int(H * 0.70)
        self._centered(
            "Appuyez sur ENTRÉE pour valider",
            self._font(int(H * 0.025)), (100, 100, 110), hint_y
        )

        btn_w   = int(W * 0.40)
        btn_h   = int(H * 0.058)
        btn_y   = int(H * 0.90)
        btn_rect = pygame.Rect(W // 2 - btn_w // 2, btn_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, (38, 38, 52), btn_rect, border_radius=10)
        pygame.draw.rect(self.screen, (78, 66, 158), btn_rect, 2, border_radius=10)
        switch_txt = ("Pas de compte ? S'inscrire"
                      if mode == "LOGIN" else "Déjà un compte ? Se connecter")
        self._blit_on_rect(switch_txt, self._font(int(H * 0.028)), (135, 125, 248), btn_rect)

        pygame.display.flip()
        return btn_rect

    def draw_sync(self):
        W, H = self._W(), self._H()

        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((10, 10, 30, 215))
        self.screen.blit(overlay, (0, 0))

        bw = int(W * 0.52)
        bh = int(H * 0.42)
        bx = (W - bw) // 2
        by = (H - bh) // 2

        pygame.draw.rect(self.screen, (22, 22, 42), (bx, by, bw, bh), border_radius=14)
        pygame.draw.rect(self.screen, (88, 72, 198), (bx, by, bw, bh), 2, border_radius=14)

        self._centered("Publier vos scores en ligne ?",
                       self._font(int(H * 0.048), bold=True),
                       (218, 212, 255), by + int(bh * 0.18))

        self._centered("Vos résultats seront visibles dans le classement mondial.",
                       self._font(int(H * 0.027)),
                       (145, 140, 195), by + int(bh * 0.40))

        self._centered("Ce choix ne sera plus redemandé. si vous souhaitez modifier votre choix, changez le directement dans les paramètres",
                       self._font(int(H * 0.023)),
                       (85, 83, 125), by + int(bh * 0.54))

        btn_h = int(H * 0.062)
        btn_w = int(W * 0.15)
        gap   = int(W * 0.04)
        btn_y = by + int(bh * 0.70)

        oui_rect = pygame.Rect(W // 2 - gap // 2 - btn_w, btn_y, btn_w, btn_h)
        non_rect = pygame.Rect(W // 2 + gap // 2,          btn_y, btn_w, btn_h)

        pygame.draw.rect(self.screen, (68, 52, 188), oui_rect, border_radius=8)
        pygame.draw.rect(self.screen, (48, 48, 62),  non_rect, border_radius=8)

        self._blit_on_rect("[O] Oui", self._font(int(H * 0.034), bold=True),
                           (208, 198, 255), oui_rect)
        self._blit_on_rect("[N] Non", self._font(int(H * 0.034), bold=True),
                           (165, 165, 165), non_rect)