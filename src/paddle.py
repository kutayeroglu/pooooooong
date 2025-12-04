import pygame
from .constants import PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, WINDOW_HEIGHT, WHITE


class Paddle:
    def __init__(self, x, y, speed_multiplier=1.0):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.base_speed = PADDLE_SPEED
        self.speed_multiplier = speed_multiplier
        self.speed = self.base_speed * self.speed_multiplier

    def update_speed(self, multiplier):
        """Update speed based on multiplier"""
        self.speed_multiplier = multiplier
        self.speed = self.base_speed * self.speed_multiplier

    def move(self, direction):
        """Move paddle up (-1) or down (1)"""
        if direction == -1 and self.rect.top > 0:
            self.rect.y -= self.speed
        elif direction == 1 and self.rect.bottom < WINDOW_HEIGHT:
            self.rect.y += self.speed

    def set_position(self, y):
        """Set paddle position based on Y coordinate (centered on Y)"""
        # Center paddle on Y coordinate
        self.rect.centery = y
        # Keep paddle within bounds
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

