# Top-Down Racing Game

A simple top-down car racing game built with Python and Pygame.

## Features

- Player-controlled car that moves with left/right arrow keys
- Randomly generated traffic to avoid
- Score based on time survived
- Sound effects for engine, crashes, and power-ups
- Pause menu (press P)
- Game over screen
- Start menu with instructions
- Power-ups:
  - Shield (blue): Protects from one collision
  - Slow (purple): Reduces game speed
  - Points (yellow): Adds bonus points
- High score tracking using JSON

## How to Play

1. Install Python and Pygame:
```
pip3 install pygame
```

2. Run the game:
```
python3 racing_game_with_powerups.py
```

3. Controls:
   - LEFT/RIGHT arrow keys: Move car
   - P: Pause/unpause game
   - ENTER: Start game or return to menu after game over

## Files

- `racing_game.py`: Basic version with core functionality
- `racing_game_with_sound.py`: Version with sound effects
- `racing_game_with_powerups.py`: Complete version with power-ups and high scores

## Web Export

To export the game as a web application, you would need to use Pygbag:

1. Install Pygbag:
```
pip3 install pygbag
```

2. Build the web version:
```
pygbag racing_game_with_powerups.py
```

3. The web version will be available in the `build/web` directory.

## Notes

- The game automatically creates placeholder sound files if they don't exist
- High scores are saved in `racing_high_scores.json`
- Game difficulty increases over time as the speed increases
