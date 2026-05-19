import pygame
import os
from dotenv import load_dotenv

load_dotenv()

SERVER_URL= "https://pysnake-api.onrender.com"

WIDTH = int(os.getenv('WIDTH'))
HEIGHT = int(os.getenv('HEIGHT'))
FPS = int(os.getenv('FPS'))
CELL_SIZE = int(os.getenv('CELL_SIZE'))

COLOR_BG = (173, 255, 47)
COLOR_GRID = (154, 232, 49)
COLOR_SNAKE_HEAD = (100, 149, 237)
COLOR_SNAKE_BODY = (65, 105, 225)
COLOR_APPLE = (255, 69, 0)
WHITE = (255, 255, 255)

UP = pygame.K_UP
DOWN = pygame.K_DOWN
LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT

MENU_TOGGLE = pygame.K_SPACE
MENU_UP = UP
MENU_DOWN = DOWN
MENU_LEFT = LEFT
MENU_RIGHT = RIGHT
MENU_EXIT = pygame.K_ESCAPE

STATE_MENU = 0
STATE_PLAYING = 1
STATE_LOSE = 2
STATE_WIN = 3
STATE_AUTH = 10
STATE_SYNC = 11

TXT_RESUME = "Reprendre"
TXT_RESTART = "Recommencer"
TXT_OPTIONS = "Options"
TXT_QUIT = "Quitter"
TXT_FULLSCREEN = "Plein Écran"
TXT_WINDOWED = "Mode Fenêtré"
TXT_BACK = "Retour"
TXT_CANCEL = "Annuler"
TXT_CONFIRM_QUIT = "Quitter le jeu"
TXT_SYNC = "Synchronisation en ligne"