import pygame
import os
import sys


class SoundManager:
    """Manages sound effects for the game"""

    def __init__(self):
        """Initialize sound manager and load sound files"""
        self.sounds = {}
        self.enabled = True

        # Initialize pygame mixer (if not already initialized)
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except pygame.error:
            print("Warning: Could not initialize sound system. Sound effects disabled.")
            self.enabled = False
            return

        # Get the assets directory path
        # This works whether running from project root or from pooooooong directory
        if getattr(sys, "frozen", False):
            # If running as a compiled executable
            base_path = sys._MEIPASS
        else:
            # If running as a script
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        assets_dir = os.path.join(base_path, "assets")

        # Load sound files
        self._load_sound("wall_hit", os.path.join(assets_dir, "wall_hit.wav"))
        self._load_sound("paddle_hit", os.path.join(assets_dir, "paddle_hit.wav"))
        self._load_sound("goal_scored", os.path.join(assets_dir, "goal_scored.wav"))

    def _load_sound(self, name, filepath):
        """Load a sound file"""
        try:
            if os.path.exists(filepath):
                self.sounds[name] = pygame.mixer.Sound(filepath)
            else:
                print(f"Warning: Sound file not found: {filepath}")
                self.sounds[name] = None
        except pygame.error as e:
            print(f"Warning: Could not load sound {filepath}: {e}")
            self.sounds[name] = None

    def play_wall_hit(self):
        """Play sound when ball hits a wall"""
        if self.enabled and self.sounds.get("wall_hit"):
            try:
                self.sounds["wall_hit"].play()
            except pygame.error:
                pass  # Silently fail if sound can't play

    def play_paddle_hit(self):
        """Play sound when ball hits a paddle"""
        if self.enabled and self.sounds.get("paddle_hit"):
            try:
                self.sounds["paddle_hit"].play()
            except pygame.error:
                pass  # Silently fail if sound can't play

    def play_goal_scored(self):
        """Play sound when a goal is scored"""
        if not self.enabled:
            return
        sound = self.sounds.get("goal_scored")
        if sound:
            try:
                # Use a dedicated channel for goal sound to ensure it plays
                channel = pygame.mixer.Channel(0)
                channel.play(sound)
            except pygame.error as e:
                print(f"Warning: Could not play goal scored sound: {e}")
        else:
            print("Warning: Goal scored sound not loaded")
