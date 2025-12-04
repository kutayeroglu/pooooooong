import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 15
PADDLE_SPEED = 5
BALL_SPEED = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)

# Create the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()


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
                self.velocity_y = int(max_velocity * (1 if self.velocity_y > 0 else -1))
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


class Game:
    def __init__(self):
        self.speed_multiplier = 1.0
        self.ai_difficulty = "medium"  # easy, medium, hard
        self.player_paddle = Paddle(
            50, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, self.speed_multiplier
        )
        self.ai_paddle = AIPaddle(
            WINDOW_WIDTH - 50 - PADDLE_WIDTH,
            WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2,
            self.speed_multiplier,
            self.ai_difficulty,
        )
        self.ball = Ball(self.speed_multiplier)
        self.player_score = 0
        self.ai_score = 0
        self.paused = False
        self.game_started = False
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.tiny_font = pygame.font.Font(None, 28)

    def handle_input(self):
        """Handle keyboard and mouse input"""
        if not self.paused:
            # Mouse control - paddle follows mouse Y position
            mouse_y = pygame.mouse.get_pos()[1]
            self.player_paddle.set_position(mouse_y)

            # Keyboard control (still works as alternative)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.player_paddle.move(-1)
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.player_paddle.move(1)

    def adjust_speed(self, delta):
        """Adjust game speed multiplier"""
        new_multiplier = max(0.5, min(3.0, self.speed_multiplier + delta))
        if new_multiplier != self.speed_multiplier:
            self.speed_multiplier = new_multiplier
            self.player_paddle.update_speed(self.speed_multiplier)
            self.ai_paddle.update_speed(self.speed_multiplier)
            self.ball.update_speed(self.speed_multiplier)

    def set_ai_difficulty(self, difficulty):
        """Set AI difficulty level"""
        if difficulty in ("easy", "medium", "hard"):
            self.ai_difficulty = difficulty
            self.ai_paddle.set_difficulty(difficulty)
            self.ai_paddle.update_speed(self.speed_multiplier)

    def cycle_ai_difficulty(self):
        """Cycle through AI difficulty levels"""
        difficulties = ["easy", "medium", "hard"]
        current_index = difficulties.index(self.ai_difficulty)
        next_index = (current_index + 1) % len(difficulties)
        self.ai_difficulty = difficulties[next_index]
        self.ai_paddle.set_difficulty(self.ai_difficulty)
        self.ai_paddle.update_speed(self.speed_multiplier)

    def update(self):
        """Update game state"""
        self.ball.update()
        self.ai_paddle.update(self.ball)

        # Check collisions
        self.ball.check_collision(self.player_paddle)
        self.ball.check_collision(self.ai_paddle)

        # Check for scoring
        if self.ball.is_out_of_bounds():
            if self.ball.rect.right < 0:
                self.ai_score += 1
            else:
                self.player_score += 1
            self.ball.reset()

    def draw_start_menu(self):
        """Draw start menu for selecting speed and difficulty"""
        screen.fill(BLACK)

        # Draw title
        title_text = self.font.render("PONG", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
        screen.blit(title_text, title_rect)

        # Draw background panel for settings
        panel_width = 500
        panel_height = 350
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2 + 50
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, DARK_GRAY, panel_rect)
        pygame.draw.rect(screen, WHITE, panel_rect, 3)  # Border

        # Draw speed settings
        speed_label = self.small_font.render("Game Speed:", True, WHITE)
        speed_label_rect = speed_label.get_rect(
            center=(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 20)
        )
        screen.blit(speed_label, speed_label_rect)

        speed_value = self.small_font.render(
            f"{self.speed_multiplier:.1f}x", True, WHITE
        )
        speed_value_rect = speed_value.get_rect(
            center=(WINDOW_WIDTH // 2 + 80, WINDOW_HEIGHT // 2 - 20)
        )
        screen.blit(speed_value, speed_value_rect)

        # Draw speed controls
        speed_controls = self.tiny_font.render("UP/DOWN to adjust", True, GRAY)
        speed_controls_rect = speed_controls.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10)
        )
        screen.blit(speed_controls, speed_controls_rect)

        # Draw AI difficulty settings
        ai_label = self.small_font.render("AI Difficulty:", True, WHITE)
        ai_label_rect = ai_label.get_rect(
            center=(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 50)
        )
        screen.blit(ai_label, ai_label_rect)

        ai_value = self.small_font.render(self.ai_difficulty.upper(), True, WHITE)
        ai_value_rect = ai_value.get_rect(
            center=(WINDOW_WIDTH // 2 + 80, WINDOW_HEIGHT // 2 + 50)
        )
        screen.blit(ai_value, ai_value_rect)

        # Draw AI difficulty controls
        ai_controls = self.tiny_font.render("Press A to cycle", True, GRAY)
        ai_controls_rect = ai_controls.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80)
        )
        screen.blit(ai_controls, ai_controls_rect)

        # Draw start instruction
        start_text = self.small_font.render("Press ENTER to start", True, WHITE)
        start_rect = start_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 130)
        )
        screen.blit(start_text, start_rect)

        pygame.display.flip()

    def draw(self):
        """Draw game elements"""
        screen.fill(BLACK)

        # Draw center line
        for y in range(0, WINDOW_HEIGHT, 20):
            pygame.draw.rect(screen, WHITE, (WINDOW_WIDTH // 2 - 5, y, 10, 10))

        # Draw paddles and ball
        self.player_paddle.draw(screen)
        self.ai_paddle.draw(screen)
        self.ball.draw(screen)

        # Draw scores
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (WINDOW_WIDTH // 4, 50))
        screen.blit(ai_text, (3 * WINDOW_WIDTH // 4, 50))

        # Draw pause message if paused
        if self.paused:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(180)  # Semi-transparent
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            # Draw background panel for settings
            panel_width = 450
            panel_height = 320
            panel_x = (WINDOW_WIDTH - panel_width) // 2
            panel_y = (WINDOW_HEIGHT - panel_height) // 2
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(screen, DARK_GRAY, panel_rect)
            pygame.draw.rect(screen, WHITE, panel_rect, 3)  # Border

            # Draw pause text
            pause_text = self.font.render("PAUSED", True, WHITE)
            pause_rect = pause_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100)
            )
            screen.blit(pause_text, pause_rect)

            # Draw speed settings
            speed_label = self.small_font.render("Game Speed:", True, WHITE)
            speed_label_rect = speed_label.get_rect(
                center=(WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 - 40)
            )
            screen.blit(speed_label, speed_label_rect)

            speed_value = self.small_font.render(
                f"{self.speed_multiplier:.1f}x", True, WHITE
            )
            speed_value_rect = speed_value.get_rect(
                center=(WINDOW_WIDTH // 2 + 50, WINDOW_HEIGHT // 2 - 40)
            )
            screen.blit(speed_value, speed_value_rect)

            # Draw speed controls
            speed_controls = self.tiny_font.render("UP/DOWN to adjust", True, GRAY)
            speed_controls_rect = speed_controls.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 10)
            )
            screen.blit(speed_controls, speed_controls_rect)

            # Draw AI difficulty settings
            ai_label = self.small_font.render("AI Difficulty:", True, WHITE)
            ai_label_rect = ai_label.get_rect(
                center=(WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 + 30)
            )
            screen.blit(ai_label, ai_label_rect)

            ai_value = self.small_font.render(self.ai_difficulty.upper(), True, WHITE)
            ai_value_rect = ai_value.get_rect(
                center=(WINDOW_WIDTH // 2 + 50, WINDOW_HEIGHT // 2 + 30)
            )
            screen.blit(ai_value, ai_value_rect)

            # Draw AI difficulty controls
            ai_controls = self.tiny_font.render("Press A to cycle", True, GRAY)
            ai_controls_rect = ai_controls.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60)
            )
            screen.blit(ai_controls, ai_controls_rect)

            # Draw resume instruction
            resume_text = self.small_font.render("Press ESC to resume", True, GRAY)
            resume_rect = resume_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 110)
            )
            screen.blit(resume_text, resume_rect)

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if not self.game_started:
                        # Start menu controls
                        if (
                            event.key == pygame.K_RETURN
                            or event.key == pygame.K_KP_ENTER
                        ):
                            self.game_started = True
                        elif event.key == pygame.K_UP:
                            self.adjust_speed(0.1)
                        elif event.key == pygame.K_DOWN:
                            self.adjust_speed(-0.1)
                        elif event.key == pygame.K_a:
                            self.cycle_ai_difficulty()
                    else:
                        # Game controls
                        if event.key == pygame.K_ESCAPE:
                            self.paused = not self.paused
                        elif self.paused:
                            # Speed adjustment controls when paused
                            if event.key == pygame.K_UP:
                                self.adjust_speed(0.1)
                            elif event.key == pygame.K_DOWN:
                                self.adjust_speed(-0.1)
                            elif event.key == pygame.K_a:
                                self.cycle_ai_difficulty()

            if self.game_started:
                self.handle_input()
                if not self.paused:
                    self.update()
                self.draw()
            else:
                self.draw_start_menu()
            clock.tick(60)  # 60 FPS

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
