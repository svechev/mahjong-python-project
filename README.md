# Mahjong

A single-player Riichi Mahjong game implemented in Python with Pygame. 
Play against simple bots that discard the tile they draw. Supports Riichi rules used in competitive Riichi Mahjong.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/svechev/mahjong-python-project
cd mahjong-python-project
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate # Linux / macOS
venv\Scripts\activate # Windows
```

3. Install dependencies:

```bash
pip install .
```

## Usage

Run the game with:

```bash
python main.py
```

### Gameplay

Click on a tile in your hand to discard when it's your turn.
Buttons appear for Pon, Chii, Kan, Riichi, and Tsumo when applicable.
You must click one of them or Skip before you proceed with the game.
Restart button is always available - during a round and after it's ended. It resets the round.

## Features

- Single-player against simple bots
- Displays information about the state of the game: hand, open combos, discarded tiles, dora indicators, player winds
- Detects winning hands and yaku
- Detects a ready hand and displays which tiles are needed to make it a winning hand
- Supports every yaku used in competitive Riichi Mahjong
- Hover highlights and visual cues for playable tiles

## Project Structure

- assets/           - Images for tiles
- src/
  - game.py         - Main game logic
  - gamestate.py    - Handles game state
  - renderer.py     - Drawing code
  - tiles.py        - Tile objects
  - yaku_checker.py - Functions for yaku
  - winning_hand_checker.py - Check winning hands
- tests/            - Unit tests for logic
- main.py           - Starts the game
- pyproject.toml    - Project metadata and dependencies

## Dependencies

- Python >= 3.10
- Pygame >= 2.6
- README.md        

