import pygame
import random
from .constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BALL_SIZE,
    BALL_SPEED,
    PADDLE_HEIGHT,
    WHITE,
)


class Ball:
    def __init__(self, speed_multiplier=1.0):
        self.speed_multiplier = speed_multiplier
        self.reset()

    def update_speed(self, multiplier):
        """Update speed multiplier and recalculate velocities"""
        self.speed_multiplier = multiplier
        # Adjust current velocities to maintain direction but scale speed
        current_speed = (self.velocity_x**2 + self.velocity_y**2) ** 0.5
        if current_speed > 0:
            scale = (BALL_SPEED * self.speed_multiplier) / current_speed
            self.velocity_x = int(self.velocity_x * scale)
            self.velocity_y = int(self.velocity_y * scale)

    def reset(self):
        """Reset ball to center with random direction"""
        self.rect = pygame.Rect(
            WINDOW_WIDTH // 2 - BALL_SIZE // 2,
            WINDOW_HEIGHT // 2 - BALL_SIZE // 2,
            BALL_SIZE,
            BALL_SIZE,
        )
        # Random initial direction
        base_velocity = BALL_SPEED * self.speed_multiplier
        self.velocity_x = int(base_velocity * random.choice([-1, 1]))
        self.velocity_y = int(base_velocity * random.choice([-1, 1]))

    def update(self):
        """Update ball position"""
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        # Bounce off top and bottom walls
        if self.rect.top <= 0 or self.rect.bottom >= WINDOW_HEIGHT:
            self.velocity_y = -self.velocity_y

    def check_collision(self, paddle):
        """Check collision with paddle and reverse direction"""
        if self.rect.colliderect(paddle.rect):
            # Reverse x direction and add slight angle variation
            self.velocity_x = -self.velocity_x
            # Add some spin based on where ball hits paddle
            hit_pos = (self.rect.centery - paddle.rect.centery) / (PADDLE_HEIGHT // 2)
            self.velocity_y += hit_pos * 2
            # Keep speed reasonable
            max_velocity = BALL_SPEED * self.speed_multiplier * 2
            if abs(self.velocity_y) > max_velocity:
                self.velocity_y = int(
                    max_velocity * (1 if self.velocity_y > 0 else -1)
                )
            # Move ball away from paddle to prevent sticking
            if self.velocity_x > 0:
                self.rect.left = paddle.rect.right
            else:
                self.rect.right = paddle.rect.left
            return True
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

    def is_out_of_bounds(self):
        """Check if ball is out of bounds (scored)"""
        return self.rect.right < 0 or self.rect.left > WINDOW_WIDTH

