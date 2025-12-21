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
from .sounds import SoundManager


class Game:
    def __init__(self):
        self.speed_multiplier = 1.0
        self.ai_difficulty = "medium"  # easy, medium, hard
        # Initialize sound manager
        self.sound_manager = SoundManager()
        self.player_paddle = Paddle(
            50, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, self.speed_multiplier
        )
        self.ai_paddle = AIPaddle(
            WINDOW_WIDTH - 50 - PADDLE_WIDTH,
            WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2,
            self.speed_multiplier,
            self.ai_difficulty,
        )
        self.ball = Ball(self.speed_multiplier, self.sound_manager)
        self.player_score = 0
        self.ai_score = 0
        self.paused = False
        self.game_started = False
        self.last_esc_press_time = 0
        self.esc_double_press_threshold = 500  # milliseconds
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.tiny_font = pygame.font.Font(None, 28)
        # Maximum score feature
        self.max_score = None
        self.max_score_input = ""
        self.game_over = False
        self.game_winner = None
        self.menu_button_rect = None

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

    def reset_to_menu(self):
        """Reset game state and return to main menu"""
        self.player_score = 0
        self.ai_score = 0
        self.paused = False
        self.game_started = False
        self.game_over = False
        self.game_winner = None
        self.ball.reset()
        # Reset paddles to center
        self.player_paddle.set_position(WINDOW_HEIGHT // 2)
        self.ai_paddle.rect.centery = WINDOW_HEIGHT // 2

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
            # Play goal scored sound
            self.sound_manager.play_goal_scored()
            self.ball.reset()

            # Check win condition
            if self.max_score is not None:
                if self.player_score >= self.max_score:
                    self.game_over = True
                    self.game_winner = "player"
                elif self.ai_score >= self.max_score:
                    self.game_over = True
                    self.game_winner = "ai"

    def draw_start_menu(self):
        """Draw start menu for selecting speed and difficulty"""
        screen.fill(BLACK)

        # Draw title
        title_text = self.font.render("PONG", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
        screen.blit(title_text, title_rect)

        # Draw background panel for settings
        panel_width = 500
        panel_height = 420
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2 + 50
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, DARK_GRAY, panel_rect)
        pygame.draw.rect(screen, WHITE, panel_rect, 3)  # Border

        # Calculate left alignment for all labels (use longest label as reference)
        label_left_x = (
            WINDOW_WIDTH // 2 - 100 - self.small_font.size("AI Difficulty:")[0] // 2
        )

        # Draw speed settings
        speed_label = self.small_font.render("Game Speed:", True, WHITE)
        speed_label_rect = speed_label.get_rect(
            left=label_left_x, centery=WINDOW_HEIGHT // 2 - 20
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
            left=label_left_x, centery=WINDOW_HEIGHT // 2 + 50
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

        # Draw Max Score settings
        max_score_label = self.small_font.render("Max Score:", True, WHITE)
        max_score_label_rect = max_score_label.get_rect(
            left=label_left_x, centery=WINDOW_HEIGHT // 2 + 110
        )
        screen.blit(max_score_label, max_score_label_rect)

        # Display current input or placeholder
        display_value = self.max_score_input if self.max_score_input else "10"
        max_score_value = self.small_font.render(display_value, True, WHITE)
        max_score_value_rect = max_score_value.get_rect(
            center=(WINDOW_WIDTH // 2 + 80, WINDOW_HEIGHT // 2 + 110)
        )
        screen.blit(max_score_value, max_score_value_rect)

        # Draw max score controls
        max_score_controls = self.tiny_font.render("Type number (1-50)", True, GRAY)
        max_score_controls_rect = max_score_controls.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 140)
        )
        screen.blit(max_score_controls, max_score_controls_rect)

        # Draw start instruction
        start_text = self.small_font.render("Press ENTER to start", True, WHITE)
        start_rect = start_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 180)
        )
        screen.blit(start_text, start_rect)

        pygame.display.flip()

    def draw_game_over(self):
        """Draw game over screen"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)  # Semi-transparent
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        # Draw background panel
        panel_width = 500
        panel_height = 300
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, DARK_GRAY, panel_rect)
        pygame.draw.rect(screen, WHITE, panel_rect, 3)  # Border

        # Draw win/lose message
        if self.game_winner == "player":
            result_text = self.font.render("YOU WIN!", True, WHITE)
        else:
            result_text = self.font.render("YOU LOSE", True, WHITE)
        result_rect = result_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60)
        )
        screen.blit(result_text, result_rect)

        # Draw final scores
        final_score_text = self.small_font.render(
            f"Final Score: {self.player_score} - {self.ai_score}", True, WHITE
        )
        final_score_rect = final_score_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
        )
        screen.blit(final_score_text, final_score_rect)

        # Draw exit instruction
        exit_text = self.tiny_font.render("Double-press ESC to exit", True, GRAY)
        exit_rect = exit_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80)
        )
        screen.blit(exit_text, exit_rect)

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

        # Draw game over screen if game is over
        if self.game_over:
            self.draw_game_over()
            pygame.display.flip()
            return

        # Draw pause message if paused
        if self.paused:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(180)  # Semi-transparent
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            # Draw background panel for settings
            panel_width = 450
            panel_height = 430  # Increased to fit menu button and instruction
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
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 90)
            )
            screen.blit(resume_text, resume_rect)

            # Draw exit instruction
            exit_text = self.tiny_font.render("Double-press ESC to exit", True, GRAY)
            exit_rect = exit_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 120)
            )
            screen.blit(exit_text, exit_rect)

            # Draw return to menu instruction (keyboard shortcut)
            menu_instruction = self.small_font.render(
                "Press M to return to menu", True, WHITE
            )
            menu_instruction_rect = menu_instruction.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 150)
            )
            screen.blit(menu_instruction, menu_instruction_rect)

            # Draw return to menu button
            button_width = 250
            button_height = 40
            button_x = (WINDOW_WIDTH - button_width) // 2
            button_y = WINDOW_HEIGHT // 2 + 190
            self.menu_button_rect = pygame.Rect(
                button_x, button_y, button_width, button_height
            )

            # Check if mouse is hovering over button
            mouse_pos = pygame.mouse.get_pos()
            button_hovered = self.menu_button_rect.collidepoint(mouse_pos)

            # Draw button with hover effect
            button_color = WHITE if button_hovered else GRAY
            pygame.draw.rect(screen, button_color, self.menu_button_rect)
            pygame.draw.rect(screen, WHITE, self.menu_button_rect, 2)  # Border

            # Draw button text (white on gray, black on white for contrast)
            text_color = BLACK if button_hovered else WHITE
            menu_button_text = self.small_font.render(
                "Return to Main Menu", True, text_color
            )
            menu_button_text_rect = menu_button_text.get_rect(
                center=self.menu_button_rect.center
            )
            screen.blit(menu_button_text, menu_button_text_rect)

            # Draw click hint
            click_hint = self.tiny_font.render("(or click button)", True, GRAY)
            click_hint_rect = click_hint.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 240)
            )
            screen.blit(click_hint, click_hint_rect)

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        if self.paused and self.menu_button_rect:
                            if self.menu_button_rect.collidepoint(event.pos):
                                self.reset_to_menu()
                if event.type == pygame.KEYDOWN:
                    if not self.game_started:
                        # Start menu controls
                        if (
                            event.key == pygame.K_RETURN
                            or event.key == pygame.K_KP_ENTER
                        ):
                            # Validate and set max_score before starting
                            if self.max_score_input:
                                try:
                                    score = int(self.max_score_input)
                                    if 1 <= score <= 50:
                                        self.max_score = score
                                    else:
                                        # If invalid, use default
                                        self.max_score = 10
                                except ValueError:
                                    self.max_score = 10
                            else:
                                # Default if no input
                                self.max_score = 10
                            self.game_started = True
                        elif event.key == pygame.K_UP:
                            self.adjust_speed(0.1)
                        elif event.key == pygame.K_DOWN:
                            self.adjust_speed(-0.1)
                        elif event.key == pygame.K_a:
                            self.cycle_ai_difficulty()
                        elif event.key == pygame.K_BACKSPACE:
                            # Handle backspace to delete last character
                            if self.max_score_input:
                                self.max_score_input = self.max_score_input[:-1]
                        elif event.key in (
                            pygame.K_0,
                            pygame.K_1,
                            pygame.K_2,
                            pygame.K_3,
                            pygame.K_4,
                            pygame.K_5,
                            pygame.K_6,
                            pygame.K_7,
                            pygame.K_8,
                            pygame.K_9,
                        ):
                            # Handle number input (0-9)
                            digit = event.key - pygame.K_0
                            new_input = self.max_score_input + str(digit)
                            # Validate that the new input would be in range (1-50)
                            try:
                                test_value = int(new_input)
                                if 1 <= test_value <= 50:
                                    self.max_score_input = new_input
                            except ValueError:
                                pass  # Ignore invalid input
                    else:
                        # Game controls
                        if event.key == pygame.K_ESCAPE:
                            if self.game_over:
                                # During game over, check for double-press to exit
                                current_time = pygame.time.get_ticks()
                                time_since_last_press = (
                                    current_time - self.last_esc_press_time
                                )
                                if (
                                    self.last_esc_press_time > 0
                                    and time_since_last_press
                                    < self.esc_double_press_threshold
                                ):
                                    running = False
                                else:
                                    # Single press just updates timer
                                    self.last_esc_press_time = current_time
                            elif self.paused:
                                # Check for double-press to exit
                                current_time = pygame.time.get_ticks()
                                time_since_last_press = (
                                    current_time - self.last_esc_press_time
                                )
                                if (
                                    self.last_esc_press_time > 0
                                    and time_since_last_press
                                    < self.esc_double_press_threshold
                                ):
                                    running = False
                                else:
                                    # Single press just updates timer, doesn't resume
                                    self.last_esc_press_time = current_time
                            else:
                                self.paused = True
                                self.last_esc_press_time = 0  # Reset when pausing
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
                            elif event.key == pygame.K_m:
                                # Return to main menu
                                self.reset_to_menu()

            if self.game_started:
                self.handle_input()
                if not self.paused and not self.game_over:
                    self.update()
                self.draw()
            else:
                self.draw_start_menu()
            clock.tick(60)  # 60 FPS

        pygame.quit()
