import pygame
from .constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    PADDLE_HEIGHT,
    PADDLE_WIDTH,
    screen,
    clock,
    WHITE,
    BLACK,
    GRAY,
    DARK_GRAY,
)
from .paddle import Paddle
from .ai_paddle import AIPaddle
from .ball import Ball


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
        """Handle mouse input"""
        if not self.paused:
            # Mouse control - paddle follows mouse Y position
            mouse_y = pygame.mouse.get_pos()[1]
            self.player_paddle.set_position(mouse_y)

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
            resume_text = self.small_font.render("Press ENTER to resume", True, GRAY)
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
                            self.paused = True
                        elif (
                            event.key == pygame.K_RETURN
                            or event.key == pygame.K_KP_ENTER
                        ):
                            if self.paused:
                                self.paused = False
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
