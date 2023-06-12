# Boggle Blitz

A spin-off of the classic board game, *Boggle*, turned into a digital version. Complete with network compatibility and additional game rules. I created this for fun.

To play the game, make sure you have the following installed on each machine:
- Python 3
- PyGame

Then, follow the instructions below.

## Setup

One machine must host the server. Run `scripts\server.py`, and input your IPv4 address (use `ipconfig` to see).

Next, at least two clients (up to 4) need to be run. The client program is `scripts\app.py`. A client can be run on the same machine as the one hosting the server. Each player needs their own keyboard, so clients should be run on separate machines if you play the game properly. Again, you will need to input the IPv4 address of the server machine (the same address used to start the server).

## Gameplay

In the client window, press `SPACE` to ready up. The game will automatically start 3 seconds after every player has done so, upon which players can start playing words.

To play a word, simply type the word and press `RETURN`. Letters can be removed from your input with `BACKSPACE`. Longer words score more many more points.

Note that words must follow traditional *Boggle* rules to count for points:
- Words must be at least 3 letters long.
- Each letter must be present in the grid.
- Letters can be used only once per word.
- Each subsequent letter in the word must be adjacent to the previous on the grid (including diagonals).

Additionally, this version of the game also restricts words from being played more than once across all players, so speed is especially important!

When the timer (the vertical pink bar) runs out, words can no longer be played, and scores are final. The server and each client must be re-run to play again.

## Development Notes

This project was created using PyGame.

Some useful experience I gained in this project:
- Designing an efficient and synchronized server-client framework
- Designing a visually intuitive and pleasing UI
