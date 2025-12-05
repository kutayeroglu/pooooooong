# pooooooong

A classic Pong game implemented in Python using pygame. Play against an AI opponent!

## Setup

1. Install Python 3.7 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

```bash
python pong.py
```

## Start Menu

When the game starts, you'll see a menu where you can configure:
- **Game Speed**: Use **↑/↓** to adjust (0.5x to 3.0x)
- **AI Difficulty**: Press **A** to cycle through Easy → Medium → Hard
- Press **ENTER** to start the game

## Controls

- **Mouse** - Move paddle (follows mouse Y position)
- **ESC** - Pause/Unpause game (double-press to exit)
- **↑/↓** - Adjust game speed (when paused)
- **A** - Cycle AI difficulty: Easy → Medium → Hard (when paused)
- Close window to quit

## Gameplay

- Control the left paddle with your mouse
- The AI controls the right paddle
- Score by getting the ball past your opponent's paddle
- First to score wins! (No score limit - play as long as you want)
