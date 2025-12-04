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

# Create the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()


class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED

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
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED
        self.reaction_delay = 0.3  # AI reaction delay for challenge

    def update(self, ball):
        """AI tracks the ball with slight delay"""
        # Predict ball position
        if ball.velocity_x > 0:  # Ball moving towards AI
            target_y = ball.rect.centery
            # Add some imperfection
            target_y += random.randint(-20, 20)
            
            if self.rect.centery < target_y - 10:
                if self.rect.bottom < WINDOW_HEIGHT:
                    self.rect.y += self.speed
            elif self.rect.centery > target_y + 10:
                if self.rect.top > 0:
                    self.rect.y -= self.speed
        else:
            # Move towards center when ball is moving away
            center_y = WINDOW_HEIGHT // 2
            if self.rect.centery < center_y - 10:
                if self.rect.bottom < WINDOW_HEIGHT:
                    self.rect.y += self.speed
            elif self.rect.centery > center_y + 10:
                if self.rect.top > 0:
                    self.rect.y -= self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)


class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        """Reset ball to center with random direction"""
        self.rect = pygame.Rect(
            WINDOW_WIDTH // 2 - BALL_SIZE // 2,
            WINDOW_HEIGHT // 2 - BALL_SIZE // 2,
            BALL_SIZE,
            BALL_SIZE
        )
        # Random initial direction
        self.velocity_x = BALL_SPEED * random.choice([-1, 1])
        self.velocity_y = BALL_SPEED * random.choice([-1, 1])

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
            if abs(self.velocity_y) > BALL_SPEED * 2:
                self.velocity_y = BALL_SPEED * 2 * (1 if self.velocity_y > 0 else -1)
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
        self.player_paddle = Paddle(50, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ai_paddle = AIPaddle(WINDOW_WIDTH - 50 - PADDLE_WIDTH, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball()
        self.player_score = 0
        self.ai_score = 0
        self.paused = False
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)

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
            pause_text = self.font.render("PAUSED", True, WHITE)
            pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(pause_text, pause_rect)
            resume_text = self.small_font.render("Press SPACE or P to resume", True, WHITE)
            resume_rect = resume_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
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
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_p:
                        self.paused = not self.paused

            self.handle_input()
            if not self.paused:
                self.update()
            self.draw()
            clock.tick(60)  # 60 FPS

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

