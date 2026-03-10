import pygame
import os

from arcade.experimental.pygame_interaction import PygameInteraction
from dotenv import load_dotenv

load_dotenv()

WIDTH = int(os.getenv('WIDTH'))
HEIGHT = int(os.getenv('HEIGHT'))
FPS= int(os.getenv('FPS'))
CELL_SIZE = int(os.getenv('CELL_SIZE'))

COLOR_BG = (173, 255, 47)
COLOR_GRID = (154, 232, 49)
COLOR_SNAKE_HEAD = (100, 149, 237)
COLOR_SNAKE_BODY = (65, 105, 225)
COLOR_APPLE = (255, 69, 0)

UP = pygame.K_UP
DOWN = pygame.K_DOWN
LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT

MENU_TOGGLE = pygame.K_SPACE
MENU_UP = pygame.K_UP
MENU_DOWN = pygame.K_DOWN
MENU_LEFT = pygame.K_LEFT
MENU_RIGHT = pygame.K_RIGHT
MENU_EXIT = pygame.K_ESCAPE