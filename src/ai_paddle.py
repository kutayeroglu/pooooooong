import pygame
import random
from .constants import PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, WINDOW_HEIGHT, WHITE


class AIPaddle:
    def __init__(self, x, y, speed_multiplier=1.0, difficulty="medium"):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.base_speed = PADDLE_SPEED
        self.speed_multiplier = speed_multiplier
        self.speed = self.base_speed * self.speed_multiplier
        self.difficulty = difficulty
        self.set_difficulty(difficulty)

    def set_difficulty(self, difficulty):
        """Set AI difficulty level"""
        self.difficulty = difficulty
        if difficulty == "easy":
            self.imperfection_range = 40  # More error
            self.reaction_threshold = 20  # Slower reaction
            self.speed_factor = 0.7  # Slower movement
        elif difficulty == "medium":
            self.imperfection_range = 20  # Moderate error
            self.reaction_threshold = 10  # Normal reaction
            self.speed_factor = 1.0  # Normal speed
        else:  # hard
            self.imperfection_range = 5  # Minimal error
            self.reaction_threshold = 5  # Fast reaction
            self.speed_factor = 1.2  # Faster movement

    def update_speed(self, multiplier):
        """Update speed based on multiplier"""
        self.speed_multiplier = multiplier
        self.speed = self.base_speed * self.speed_multiplier * self.speed_factor

    def update(self, ball):
        """AI tracks the ball with difficulty-based behavior"""
        # Predict ball position
        if ball.velocity_x > 0:  # Ball moving towards AI
            target_y = ball.rect.centery
            # Add imperfection based on difficulty
            target_y += random.randint(
                -self.imperfection_range, self.imperfection_range
            )

            # Speed already includes speed_factor from update_speed
            if self.rect.centery < target_y - self.reaction_threshold:
                if self.rect.bottom < WINDOW_HEIGHT:
                    self.rect.y += self.speed
            elif self.rect.centery > target_y + self.reaction_threshold:
                if self.rect.top > 0:
                    self.rect.y -= self.speed
        else:
            # Move towards center when ball is moving away
            center_y = WINDOW_HEIGHT // 2
            if self.rect.centery < center_y - self.reaction_threshold:
                if self.rect.bottom < WINDOW_HEIGHT:
                    self.rect.y += self.speed
            elif self.rect.centery > center_y + self.reaction_threshold:
                if self.rect.top > 0:
                    self.rect.y -= self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

